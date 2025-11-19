#!/usr/bin/env python3
"""
Mirror Longdan CDN images into Supabase Storage so the frontend can serve
thumbnails from our own bucket instead of hot-linking the source site.

Usage:
    uv run python scripts/sync_catalog_images.py \
        --image-index ../heysalad-datasource/longdan_image_index.json \
        --bucket catalog-images --prefix products
"""

from __future__ import annotations

import argparse
import concurrent.futures
import mimetypes
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.database_supabase import get_supabase_client  # noqa: E402

DEFAULT_INDEX = Path("/home/admin/heysalad-datasource/longdan_image_index.json")
DEFAULT_BUCKET = os.getenv("CATALOG_IMAGE_BUCKET", "catalog-images")
DEFAULT_PREFIX = os.getenv("CATALOG_IMAGE_PREFIX", "products")


def ensure_bucket(storage, bucket: str) -> None:
    try:
        storage.create_bucket(bucket, options={"public": True})
    except Exception as exc:  # noqa: BLE001
        if "already exists" not in str(exc).lower():
            raise
    # Verify access
    storage.from_(bucket).list(path="", options={"limit": 1})


def list_existing_paths(storage, bucket: str, prefix: str) -> set[str]:
    existing: set[str] = set()
    folder = prefix.strip("/")
    limit = 1000
    offset = 0
    while True:
        options = {"limit": limit, "offset": offset}
        entries = storage.from_(bucket).list(path=folder, options=options)
        if not entries:
            break
        for entry in entries:
            name = entry.get("name")
            if name:
                if folder:
                    existing.add(f"{folder}/{name}")
                else:
                    existing.add(name)
        if len(entries) < limit:
            break
        offset += limit
    return existing


def _sanitize_component(value: str, allow_dot: bool = False) -> str:
    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    pattern = r"[^A-Za-z0-9._-]+" if allow_dot else r"[^A-Za-z0-9_-]+"
    ascii_value = re.sub(pattern, "-", ascii_value)
    ascii_value = re.sub(r"-{2,}", "-", ascii_value)
    return ascii_value.strip("-")


def build_storage_path(prefix: str, filename: str) -> Optional[str]:
    if not filename:
        return None
    name, ext = os.path.splitext(filename)
    safe_name = _sanitize_component(name)
    safe_ext = _sanitize_component(ext or ".jpg", allow_dot=True)
    safe_filename = f"{safe_name or 'product'}{safe_ext or '.jpg'}"
    trimmed_prefix = prefix.strip("/")
    return f"{trimmed_prefix}/{safe_filename}".strip("/") if trimmed_prefix else safe_filename


def iter_images(index_path: Path, limit: int | None) -> Iterable[Tuple[str, Dict[str, str]]]:
    import json

    data = json.loads(index_path.read_text(encoding="utf-8"))
    count = 0
    for sku, meta in data.items():
        if not meta.get("image_url"):
            continue
        yield sku, meta
        count += 1
        if limit and count >= limit:
            break


def fetch_image(url: str, timeout: int = 30) -> Tuple[bytes, str]:
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    content_type = resp.headers.get("Content-Type") or mimetypes.guess_type(url)[0] or "image/jpeg"
    return resp.content, content_type


def upload_image(storage, bucket: str, path: str, data: bytes, content_type: str) -> None:
    storage.from_(bucket).upload(
        path,
        data,
        {"content-type": content_type, "upsert": "true"},
    )


def sync_images(
    index_path: Path,
    bucket: str,
    prefix: str,
    limit: int | None,
    workers: int,
    skip_existing: bool,
) -> None:
    supabase = get_supabase_client()
    storage = supabase.storage
    ensure_bucket(storage, bucket)

    prefix = prefix.strip("/")
    uploaded = 0
    skipped = 0
    errors = 0

    items = list(iter_images(index_path, limit))
    total = len(items)

    existing_paths = set()
    if skip_existing:
        print("🔍 Gathering existing objects from storage...")
        existing_paths = list_existing_paths(storage, bucket, prefix)
        print(f"   Found {len(existing_paths)} existing objects; will skip duplicates.")

    def process(entry: Tuple[str, Dict[str, str]]) -> Tuple[str, bool]:
        sku, meta = entry
        filename = meta.get("image_filename") or f"{sku}.jpg"
        storage_path = build_storage_path(prefix, filename)
        if not storage_path:
            print(f"⚠️ {sku} skipped: invalid storage path for filename '{filename}'")
            return sku, None

        if skip_existing and storage_path in existing_paths:
            return sku, None

        try:
            data, content_type = fetch_image(meta["image_url"])
            upload_image(storage, bucket, storage_path, data, content_type)
            return sku, True
        except Exception as exc:  # noqa: BLE001
            print(f"❌ {sku} failed: {exc}")
            return sku, False

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        for sku, ok in executor.map(process, items):
            if ok is True:
                uploaded += 1
            elif ok is False:
                errors += 1
            else:
                skipped += 1
            processed = uploaded + errors + skipped
            if processed % 100 == 0:
                print(f"Processed {processed}/{total} (✅ {uploaded} / ⚠️ {skipped} / ❌ {errors})")

    print(f"\nDone! Total: {total}, Uploaded: {uploaded}, Skipped: {skipped}, Errors: {errors}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync Longdan images into Supabase Storage.")
    parser.add_argument("--image-index", type=Path, default=DEFAULT_INDEX, help="Path to longdan_image_index.json")
    parser.add_argument("--bucket", default=DEFAULT_BUCKET, help="Supabase Storage bucket name")
    parser.add_argument("--prefix", default=DEFAULT_PREFIX, help="Path prefix inside the bucket")
    parser.add_argument("--limit", type=int, help="Only sync the first N records (debugging)")
    parser.add_argument("--workers", type=int, default=8, help="Download concurrency")
    parser.add_argument("--skip-existing", action="store_true", help="Skip files that already exist in the target bucket")

    args = parser.parse_args()
    if not args.image_index.exists():
        raise SystemExit(f"Image index not found: {args.image_index}")

    sync_images(
        args.image_index,
        args.bucket,
        args.prefix,
        args.limit,
        args.workers,
        args.skip_existing,
    )


if __name__ == "__main__":
    main()
