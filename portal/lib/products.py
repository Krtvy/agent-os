"""
Product catalog mapping — portal/products.csv.

Mirrors the May Sheet PoC.csv pattern: a small flat file the operator
maintains. Columns: product, category (hero/bundle/extra), active, notes.

Used by:
  - /products page (read-only listing for now)
  - Future: product filter on the creator report (e.g. "show me only
    HGR-product creators")
  - Future: validation when adding products via UI

The DB catalog (rootlabs_core.rootlabs_products) is the source of truth
for SKUs. This file curates which products POCs CARE about — hero vs
bundle vs extra.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

PORTAL_DIR = Path(__file__).resolve().parents[1]
PRODUCTS_CSV = PORTAL_DIR / "products.csv"


@dataclass(frozen=True)
class Product:
    name: str
    category: str  # "hero" | "bundle" | "extra"
    active: bool
    notes: str = ""


_cache: list[Product] | None = None


def _load() -> list[Product]:
    global _cache
    if _cache is not None:
        return _cache
    out: list[Product] = []
    if not PRODUCTS_CSV.exists():
        _cache = out
        return out
    with PRODUCTS_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("product") or "").strip()
            if not name:
                continue
            out.append(
                Product(
                    name=name,
                    category=(row.get("category") or "extra").strip().lower(),
                    active=(row.get("active") or "yes").strip().lower() in ("yes", "y", "true", "1"),
                    notes=(row.get("notes") or "").strip(),
                )
            )
    _cache = out
    return out


def all_products() -> list[Product]:
    return _load()


def hero_products() -> list[Product]:
    return [p for p in _load() if p.category == "hero" and p.active]


def by_name(name: str) -> Product | None:
    if not name:
        return None
    target = name.strip().lower()
    for p in _load():
        if p.name.lower() == target:
            return p
    return None


def reload_cache() -> None:
    global _cache
    _cache = None
