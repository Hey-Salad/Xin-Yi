#!/usr/bin/env python3
"""
Import the Longdan grocery catalog into the Supabase `materials` table.

The script converts each Shopify variant row into a HeySalad-friendly material
record, deriving reasonable default quantities, safe stock levels, and bin
locations so the WMS dashboards remain meaningful.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

# Ensure the project root (so `backend` is importable) is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.database_supabase import get_supabase_client  # noqa: E402


DEFAULT_CSV = ROOT.parent / "heysalad-datasource" / "longdan_inventory_clean.csv"

# High-level category groups to drive storage locations
CATEGORY_ZONE_PREFIX = {
    "noodle": "NO",
    "rice": "RI",
    "condiment": "CD",
    "sauce": "CD",
    "cooking": "CK",
    "confection": "CF",
    "snack": "SN",
    "crisp": "SN",
    "frozen": "FR",
    "dried": "DR",
    "drink": "BE",
    "tea": "BE",
    "body": "PC",
    "skincare": "PC",
    "wholesale": "WH",
}

TEMPERATURE_KEYWORDS = {
    "frozen": "Frozen",
    "chill": "Chilled",
    "cold": "Chilled",
    "ambient": "Ambient",
}

UNIT_KEYWORDS = {
    "case": "case",
    "pack": "pack",
    "bottle": "bottle",
    "bottles": "bottle",
    "can": "can",
    "tin": "can",
    "jar": "jar",
    "sachet": "sachet",
    "cup": "cup",
}


def stable_hash(value: str) -> int:
    """Deterministic hash used to derive repeatable numeric values."""
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:12], 16)


def parse_bool(value: Optional[str]) -> bool:
    if value is None:
        return False
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def normalize_category(value: Optional[str]) -> str:
    if not value:
        return "General Grocery"
    value = value.strip()
    return value if value else "General Grocery"


def determine_unit(name: str) -> str:
    lower_name = name.lower()
    for keyword, unit in UNIT_KEYWORDS.items():
        if keyword in lower_name:
            return unit

    if any(token in lower_name for token in ("kg", "g", "gram")):
        return "pack"
    if any(token in lower_name for token in ("ml", "l", "litre")):
        return "bottle"
    return "unit"


def determine_temperature(tags: List[str], category: str) -> str:
    combined = " ".join(tags + [category]).lower()
    for keyword, label in TEMPERATURE_KEYWORDS.items():
        if keyword in combined:
            # Prefer the first matching keyword to avoid over-fitting
            return label
    return "Ambient"


def assign_location(category: str, sku: str) -> str:
    cat_lower = category.lower()
    prefix = "GN"
    for keyword, zone in CATEGORY_ZONE_PREFIX.items():
        if keyword in cat_lower:
            prefix = zone
            break

    slot = stable_hash(sku) % 80 + 1  # Bin slots 01-80 per zone
    return f"{prefix}-{slot:02d}"


def derive_quantity(sku: str, variant_id: str, available: bool, price: float) -> int:
    """Generate a bounded, repeatable quantity for dashboard use."""
    key = variant_id or sku
    seed = stable_hash(key)
    baseline = 35 + (seed % 165)  # 35-199 units by default

    if not available:
        baseline = max(0, baseline // 4)

    if price >= 50:
        baseline = max(10, baseline // 2)

    return max(5, baseline)


def derive_safe_stock(quantity: int, category: str) -> int:
    factor = 0.25
    if "frozen" in category.lower():
        factor = 0.15
    if "confection" in category.lower() or "snack" in category.lower():
        factor = 0.35
    return max(5, math.floor(quantity * factor))


@dataclass
class MaterialRow:
    name: str
    sku: str
    category: str
    quantity: int
    unit: str
    safe_stock: int
    location: str
    unit_of_measure: str
    temperature_zone: str

    def to_dict(self) -> Dict[str, object]:
        payload = {
            "name": self.name,
            "sku": self.sku,
            "category": self.category,
            "quantity": self.quantity,
            "unit": self.unit,
            "safe_stock": self.safe_stock,
            "location": self.location,
            "unit_of_measure": self.unit_of_measure,
            "temperature_zone": self.temperature_zone,
        }
        return payload


def transform_row(row: Dict[str, str]) -> Optional[MaterialRow]:
    sku = (row.get("sku") or "").strip()
    if not sku:
        return None

    variant_title = (row.get("variant_title") or "").strip()
    product_title = (row.get("product_title") or row.get("name") or "").strip()

    if variant_title and variant_title.lower() != "default title":
        if variant_title.lower() in product_title.lower():
            name = product_title
        else:
            name = f"{product_title} - {variant_title}".strip(" -")
    else:
        name = product_title or sku

    tags = [t.strip() for t in (row.get("tags") or "").split(",") if t.strip()]
    category = (
        (row.get("canonical_category") or "").strip()
        or normalize_category(row.get("product_type"))
    )
    temperature = (row.get("temperature_zone") or determine_temperature(tags, category)).title()
    unit = (row.get("unit") or determine_unit(name)).lower()

    price = 0.0
    try:
        price = float(row.get("price") or 0)
    except ValueError:
        price = 0.0

    quantity = derive_quantity(
        sku=sku,
        variant_id=(row.get("variant_id") or "").strip() or sku,
        available=parse_bool(row.get("available")),
        price=price,
    )
    safe_stock = derive_safe_stock(quantity, category)
    location = row.get("location") or assign_location(category, sku)

    return MaterialRow(
        name=name,
        sku=sku,
        category=category,
        quantity=quantity,
        unit=unit,
        safe_stock=safe_stock,
        location=location,
        unit_of_measure=row.get("unit_of_measure") or unit,
        temperature_zone=temperature,
    )


def chunked(iterable: List[Dict[str, object]], size: int) -> Iterable[List[Dict[str, object]]]:
    for idx in range(0, len(iterable), size):
        yield iterable[idx : idx + size]


def load_materials(csv_path: Path, limit: Optional[int] = None) -> List[Dict[str, object]]:
    materials: Dict[str, MaterialRow] = {}
    total_rows = 0

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            total_rows += 1
            material = transform_row(row)
            if not material:
                continue
            materials[material.sku] = material  # Deduplicate by SKU (last occurrence wins)
            if limit and len(materials) >= limit:
                break

    print(f"Parsed {total_rows} CSV rows → {len(materials)} unique SKUs")
    return [item.to_dict() for item in materials.values()]


def import_to_supabase(records: List[Dict[str, object]], batch_size: int) -> None:
    supabase = get_supabase_client()
    total = len(records)
    for idx, batch in enumerate(chunked(records, batch_size), start=1):
        supabase.table("materials").upsert(batch, on_conflict="sku").execute()
        processed = min(idx * batch_size, total)
        print(f"Upserted {processed}/{total} rows", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import the Longdan grocery CSV into Supabase materials."
    )
    parser.add_argument(
        "--csv-path",
        type=Path,
        default=DEFAULT_CSV,
        help="Path to longdan_inventory.csv (defaults to ../../heysalad-datasource/longdan_inventory.csv)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Number of rows per upsert batch (Supabase max is 1000).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Optional limit for debugging smaller imports.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Transform the CSV and print a preview without touching Supabase.",
    )

    args = parser.parse_args()
    csv_path = args.csv_path.expanduser()
    if not csv_path.exists():
        raise SystemExit(f"CSV file not found: {csv_path}")

    records = load_materials(csv_path, limit=args.limit)
    if not records:
        print("No valid rows found; exiting.")
        return

    print("Sample payload:", records[0])

    if args.dry_run:
        print("Dry run enabled; skipping Supabase import.")
        return

    import_to_supabase(records, batch_size=args.batch_size)
    print("✅ Import complete!")


if __name__ == "__main__":
    main()
