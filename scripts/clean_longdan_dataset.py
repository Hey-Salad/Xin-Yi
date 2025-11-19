#!/usr/bin/env python3
"""
Clean and enrich the Longdan grocery catalog before importing into Supabase.

Outputs:
1. A normalized CSV with canonical categories, packaging data, and image references
2. A JSON summary (category/vendor distributions, missing images, etc.)
3. An image index JSON so other services can stage uploads

Optional flags let you:
- Limit the number of processed rows for quick tests
- Call DeepSeek to refine category mappings for ambiguous source categories
- Upload the cleaned artifacts to Supabase Storage (requires service key)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.database_supabase import get_supabase_client

DEFAULT_SOURCE = Path("/home/admin/heysalad-datasource/longdan_inventory.csv")
DEFAULT_OUT_DIR = Path("/home/admin/heysalad-datasource")
DEFAULT_CLEAN_CSV = DEFAULT_OUT_DIR / "longdan_inventory_clean.csv"
DEFAULT_SUMMARY = DEFAULT_OUT_DIR / "longdan_inventory_clean_summary.json"
DEFAULT_IMAGE_INDEX = DEFAULT_OUT_DIR / "longdan_image_index.json"

CANONICAL_RULES: List[Tuple[str, Sequence[str]]] = [
    ("Noodles & Rice", ("nood", "ramen", "udon", "rice", "pho", "vermicelli", "bun ", "bun-", "bee hoon")),
    ("Sauces & Condiments", ("sauce", "paste", "condiment", "seasoning", "marinade", "dipping", "chilli oil")),
    ("Cooking Essentials", ("flour", "starch", "cooking", "broth", "stock", "bouillon", "oil", "vinegar")),
    ("Snacks & Confectionery", ("snack", "confection", "biscu", "cookie", "crisp", "chip", "candy", "chocolate", "sweet")),
    ("Dried Pantry", ("dried", "dry", "nuts", "seeds", "bean", "lentil", "seaweed")),
    ("Frozen & Chilled", ("frozen", "ready meal", "ready-meal", "dumpling", "gyoza", "ice cream", "ice-cream")),
    ("Beverages", ("drink", "juice", "tea", "coffee", "latte", "soda", "beverage", "milk", "bubble")),
    ("Fresh Produce", ("fresh", "vegetable", "fruit", "herb", "salad")),
    ("Meat & Seafood", ("meat", "pork", "beef", "chicken", "duck", "seafood", "fish", "prawn", "shrimp", "clam")),
    ("Bakery", ("bread", "bun", "cake", "bakery")),
    ("Household & Personal Care", ("bodycare", "skincare", "household", "clean", "detergent", "soap", "shampoo")),
    ("Wholesale Packs", ("wholesale", "case", "bulk")),
]

DEPARTMENT_MAP = {
    "Noodles & Rice": "Pantry",
    "Sauces & Condiments": "Pantry",
    "Cooking Essentials": "Pantry",
    "Snacks & Confectionery": "Pantry",
    "Dried Pantry": "Pantry",
    "Frozen & Chilled": "Frozen",
    "Beverages": "Beverages",
    "Fresh Produce": "Fresh",
    "Meat & Seafood": "Fresh",
    "Bakery": "Fresh",
    "Household & Personal Care": "Household",
    "Wholesale Packs": "Wholesale",
}

UNIT_PATTERN = re.compile(r"(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>kg|g|ml|l|ltrs|litre|liter|lb|oz)", re.IGNORECASE)
CASE_PATTERN = re.compile(r"(case|pack|box)\s*(of)?\s*(\d+)", re.IGNORECASE)
SERVING_PATTERN = re.compile(r"(\d+)\s*x\s*(\d+)", re.IGNORECASE)


@dataclass
class CleanedRow:
    sku: str
    name: str
    canonical_category: str
    subcategory: str
    department: str
    vendor: str
    price: float
    currency: str
    is_wholesale: bool
    case_size: Optional[int]
    unit_size: Optional[str]
    unit: str
    temperature_zone: str
    tags: str
    image_url: str
    image_filename: str
    source_url: str


def normalize_vendor(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return "Unknown"
    return value.title()


def clean_tags(raw: str) -> str:
    parts = []
    for tag in (raw or "").split(","):
        tag = tag.strip()
        if not tag:
            continue
        parts.append(tag)
    return ",".join(sorted(set(parts)))


def derive_temperature(tags: str, category_blob: str) -> str:
    blob = f"{tags} {category_blob}".lower()
    if "frozen" in blob or "ice" in blob:
        return "Frozen"
    if "chill" in blob or "cold" in blob or "fresh" in blob:
        return "Chilled"
    return "Ambient"


def guess_category(name_blob: str) -> str:
    lower = name_blob.lower()
    for category, keywords in CANONICAL_RULES:
        if any(keyword in lower for keyword in keywords):
            return category
    return "Pantry & Misc"


def extract_unit_info(text: str) -> Tuple[Optional[str], Optional[str]]:
    match = UNIT_PATTERN.search(text)
    if not match:
        return None, None
    value = match.group("value")
    unit = match.group("unit").lower()
    normalized_unit = unit.replace("litre", "l").replace("liter", "l").replace("ltrs", "l")
    return f"{value}{normalized_unit}", normalized_unit


def extract_case_size(text: str) -> Optional[int]:
    match = CASE_PATTERN.search(text)
    if match:
        return int(match.group(3))
    match = SERVING_PATTERN.search(text)
    if match:
        try:
            return int(match.group(1)) * int(match.group(2))
        except ValueError:
            return None
    return None


def build_image_filename(handle: str, sku: str) -> str:
    safe_handle = (handle or sku).replace("/", "-")
    return f"{safe_handle}-{sku}.jpg"


def call_deepseek(raw_categories: Sequence[str]) -> Dict[str, str]:
    """Ask DeepSeek to map uncommon categories to canonical buckets."""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY not set")

    import requests

    prompt = (
        "You are standardizing grocery categories. "
        "Map each raw category to the closest canonical category from this list:\n"
        f"{[rule[0] for rule in CANONICAL_RULES]} plus 'Pantry & Misc'. "
        "Return a JSON object where keys are the raw categories and values are canonical names."
        "\nRaw categories:\n"
        + "\n".join(sorted(set(raw_categories)))
    )

    payload = {
        "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        "temperature": float(os.getenv("DEEPSEEK_TEMPERATURE", 0.2)),
        "messages": [
            {"role": "system", "content": "You are a helpful grocery merchandiser."},
            {"role": "user", "content": prompt},
        ],
    }
    response = requests.post(
        os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1") + "/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise RuntimeError(f"DeepSeek response was not valid JSON:\n{content}")


def ensure_bucket(storage, bucket_name: str) -> None:
    try:
        storage.create_bucket(bucket_name)
    except Exception as exc:  # noqa: BLE001
        if "already exists" not in str(exc).lower():
            raise


def upload_file(storage, bucket: str, path: str, data: bytes, content_type: str) -> None:
    storage.from_(bucket).upload(
        path,
        data,
        {"content-type": content_type, "upsert": "true"},
    )


def clean_catalog(
    source: Path,
    limit: Optional[int] = None,
    use_deepseek: bool = False,
) -> Tuple[List[CleanedRow], Dict]:
    cleaned: Dict[str, CleanedRow] = {}
    summary = {
        "total_rows": 0,
        "unique_skus": 0,
        "missing_images": [],
        "category_counts": {},
        "department_counts": {},
        "vendor_counts": {},
        "uncategorized_samples": defaultdict(list),
    }

    raw_uncategorized: Counter[str] = Counter()

    with source.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            summary["total_rows"] += 1
            sku = (row.get("sku") or "").strip()
            if not sku:
                continue

            name = (row.get("product_title") or "").strip() or sku
            variant = (row.get("variant_title") or "").strip()
            if variant and variant.lower() != "default title" and variant.lower() not in name.lower():
                name = f"{name} - {variant}"

            vendor = normalize_vendor(row.get("vendor", ""))
            tags = clean_tags(row.get("tags", ""))
            image_url = (row.get("image_url") or "").strip()
            if not image_url:
                summary["missing_images"].append(sku)

            text_blob = " ".join([row.get("product_type") or "", tags, name])
            canonical = guess_category(text_blob)
            if canonical == "Pantry & Misc":
                raw_cat = (row.get("product_type") or "Unknown").strip() or "Unknown"
                raw_uncategorized[raw_cat] += 1
                if len(summary["uncategorized_samples"][raw_cat]) < 3:
                    summary["uncategorized_samples"][raw_cat].append(name)
            department = DEPARTMENT_MAP.get(canonical, "Pantry")

            unit_size, unit = extract_unit_info(name)
            case_size = extract_case_size(name)

            price = 0.0
            try:
                price = float(row.get("price") or 0)
            except ValueError:
                price = 0.0

            cleaned_row = CleanedRow(
                sku=sku,
                name=name,
                canonical_category=canonical,
                subcategory=(row.get("product_type") or "").strip() or canonical,
                department=department,
                vendor=vendor,
                price=round(price, 2),
                currency="GBP",
                is_wholesale="wholesale" in (row.get("product_type") or "").lower() or "badge_wholesale" in tags.lower(),
                case_size=case_size,
                unit_size=unit_size,
                unit=unit or "unit",
                temperature_zone=derive_temperature(tags, row.get("product_type") or ""),
                tags=tags,
                image_url=image_url,
                image_filename=build_image_filename(row.get("product_handle") or sku, sku),
                source_url=f"https://longdan.co.uk/products/{row.get('product_handle')}",
            )

            cleaned[sku] = cleaned_row

            if limit and len(cleaned) >= limit:
                break

    # Optional DeepSeek refinement
    if use_deepseek and raw_uncategorized:
        overrides = call_deepseek(raw_uncategorized.keys())
        for sku, row in cleaned.items():
            if row.canonical_category == "Pantry & Misc":
                new_cat = overrides.get(row.subcategory) or overrides.get(row.canonical_category)
                if new_cat:
                    cleaned[sku] = CleanedRow(
                        **{**asdict(row), "canonical_category": new_cat, "department": DEPARTMENT_MAP.get(new_cat, row.department)}
                    )

    summary["unique_skus"] = len(cleaned)
    summary["category_counts"] = Counter(row.canonical_category for row in cleaned.values())
    summary["department_counts"] = Counter(row.department for row in cleaned.values())
    summary["vendor_counts"] = Counter(row.vendor for row in cleaned.values())
    summary["missing_images"] = summary["missing_images"][:200]
    summary["uncategorized_samples"] = dict(summary["uncategorized_samples"])

    return list(cleaned.values()), summary


def write_csv(rows: Iterable[CleanedRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(CleanedRow.__annotations__.keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_json(data: Dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def export_to_storage(clean_path: Path, summary_path: Path, image_index_path: Path, bucket: str) -> None:
    supabase = get_supabase_client()
    storage = supabase.storage
    ensure_bucket(storage, bucket)

    upload_file(storage, bucket, "catalog/longdan_inventory_clean.csv", clean_path.read_bytes(), "text/csv")
    upload_file(storage, bucket, "catalog/longdan_inventory_summary.json", summary_path.read_bytes(), "application/json")
    upload_file(storage, bucket, "catalog/longdan_image_index.json", image_index_path.read_bytes(), "application/json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean Longdan grocery data for HeySalad.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Path to raw longdan_inventory.csv")
    parser.add_argument("--out-csv", type=Path, default=DEFAULT_CLEAN_CSV, help="Path for cleaned CSV output")
    parser.add_argument("--summary-json", type=Path, default=DEFAULT_SUMMARY, help="Where to write dataset summary JSON")
    parser.add_argument("--image-index", type=Path, default=DEFAULT_IMAGE_INDEX, help="Where to write SKU→image map JSON")
    parser.add_argument("--limit", type=int, help="Limit number of rows (debugging)")
    parser.add_argument("--use-deepseek", action="store_true", help="Consult DeepSeek for hard-to-map categories")
    parser.add_argument("--upload-storage", help="Supabase Storage bucket name to upload cleaned artifacts")

    args = parser.parse_args()
    rows, summary = clean_catalog(args.source, limit=args.limit, use_deepseek=args.use_deepseek)

    write_csv(rows, args.out_csv)
    write_json(
        {
            **summary,
            "category_counts": summary["category_counts"].most_common(),
            "department_counts": summary["department_counts"].most_common(),
            "vendor_counts": summary["vendor_counts"].most_common(50),
        },
        args.summary_json,
    )
    image_index = {
        row.sku: {
            "image_url": row.image_url,
            "image_filename": row.image_filename,
            "source_url": row.source_url,
        }
        for row in rows
        if row.image_url
    }
    write_json(image_index, args.image_index)

    print(f"Cleaned rows: {len(rows)}")
    print(f"Sample row: {asdict(rows[0]) if rows else 'N/A'}")
    print(f"Summary saved to {args.summary_json}")

    if args.upload_storage:
        export_to_storage(args.out_csv, args.summary_json, args.image_index, args.upload_storage)
        print(f"Uploaded cleaned artifacts to Supabase storage bucket '{args.upload_storage}'.")


if __name__ == "__main__":
    main()
