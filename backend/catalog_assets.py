"""
Catalog asset helpers.

Loads the Longdan image index that was uploaded to Supabase Storage so backend
endpoints can attach thumbnail URLs, filenames, and original product links
without duplicating the entire JSON payload on every request.
"""

from __future__ import annotations

import json
import os
import re
import threading
import time
import unicodedata
from typing import Dict, Optional

from database_supabase import get_supabase_client

CATALOG_BUCKET = os.getenv("CATALOG_BUCKET", "catalog-cache")
CATALOG_IMAGE_INDEX_KEY = os.getenv(
    "CATALOG_IMAGE_INDEX_KEY", "catalog/longdan_image_index.json"
)
CATALOG_IMAGE_CACHE_TTL = int(os.getenv("CATALOG_IMAGE_CACHE_TTL", "900"))
IMAGE_BUCKET = os.getenv("CATALOG_IMAGE_BUCKET", "catalog-images")
IMAGE_PREFIX = os.getenv("CATALOG_IMAGE_PREFIX", "products")
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
PUBLIC_IMAGE_BASE = (
    f"{SUPABASE_URL}/storage/v1/object/public/{IMAGE_BUCKET}".rstrip("/")
    if SUPABASE_URL
    else ""
)

_cache_lock = threading.Lock()
_image_cache: Dict[str, Dict[str, str]] = {}
_last_fetch = 0.0


def _load_index(force: bool = False) -> Dict[str, Dict[str, str]]:
    """Download the image index JSON from Supabase storage with basic caching."""
    global _image_cache, _last_fetch

    with _cache_lock:
        now = time.time()
        if _image_cache and not force and now - _last_fetch < CATALOG_IMAGE_CACHE_TTL:
            return _image_cache

        try:
            supabase = get_supabase_client()
            storage = supabase.storage
            data = storage.from_(CATALOG_BUCKET).download(CATALOG_IMAGE_INDEX_KEY)
            _image_cache = json.loads(data.decode("utf-8"))
            _last_fetch = now
        except Exception as exc:  # noqa: BLE001
            # Keep old cache if download fails
            print(f"⚠️ Failed to load catalog image index: {exc}")
        return _image_cache


def _sanitize_component(value: str, allow_dot: bool = False) -> str:
    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    pattern = r"[^A-Za-z0-9._-]+" if allow_dot else r"[^A-Za-z0-9_-]+"
    ascii_value = re.sub(pattern, "-", ascii_value)
    ascii_value = re.sub(r"-{2,}", "-", ascii_value)
    return ascii_value.strip("-")


def _storage_key(filename: str) -> Optional[str]:
    if not filename:
        return None
    name, ext = os.path.splitext(filename)
    safe_name = _sanitize_component(name)
    safe_ext = _sanitize_component(ext or ".jpg", allow_dot=True)
    combined = f"{safe_name or 'product'}{safe_ext or '.jpg'}"
    prefix = IMAGE_PREFIX.strip("/")
    return f"{prefix}/{combined}".strip("/") if prefix else combined


def build_storage_url(filename: str) -> Optional[str]:
    if not PUBLIC_IMAGE_BASE:
        return None
    key = _storage_key(filename)
    if not key:
        return None
    return f"{PUBLIC_IMAGE_BASE}/{key}"


def get_material_media(sku: str) -> Optional[Dict[str, str]]:
    """Return image metadata plus storage URL for a SKU."""
    if not sku:
        return None
    index = _load_index()
    media = index.get(sku)
    if not media:
        return None
    storage_url = build_storage_url(media.get("image_filename"))
    if storage_url:
        media = {**media, "storage_image_url": storage_url}
    return media


def refresh_catalog_media_cache() -> None:
    """Force refresh cache (e.g., after importer runs)."""
    _load_index(force=True)
