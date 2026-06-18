"""
Report registry — discovers `reports/<slug>/{manifest.json, query.sql}`.

Manifest shape (M1 subset, will grow with later milestones):
{
  "slug": "probe",
  "title": "Database probe",
  "description": "Smallest possible report — verifies DB connectivity.",
  "inputs": [],                        # M3+ will use this to render forms
  "owner_poc": []                      # [] means visible to everyone; M5+ scopes
}
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_ROOT = REPO_ROOT / "reports"


@dataclass(frozen=True)
class Report:
    slug: str
    title: str
    description: str
    inputs: list[dict]
    owner_poc: list[str]
    query_sql: str
    hidden: bool = False  # don't show in home menu but still runnable via URL


def _validate(manifest: dict, slug: str) -> None:
    required = {"slug", "title", "description"}
    missing = required - manifest.keys()
    if missing:
        raise ValueError(f"Report {slug} manifest missing keys: {sorted(missing)}")
    if manifest["slug"] != slug:
        raise ValueError(
            f"Report {slug} manifest.slug={manifest['slug']!r} does not match folder name"
        )


def load_report(slug: str) -> Report:
    report_dir = REPORTS_ROOT / slug
    manifest_path = report_dir / "manifest.json"
    query_path = report_dir / "query.sql"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No manifest at {manifest_path}")
    if not query_path.exists():
        raise FileNotFoundError(f"No query at {query_path}")

    manifest = json.loads(manifest_path.read_text())
    _validate(manifest, slug)

    return Report(
        slug=slug,
        title=manifest["title"],
        description=manifest["description"],
        inputs=manifest.get("inputs", []),
        owner_poc=manifest.get("owner_poc", []),
        query_sql=query_path.read_text(),
        hidden=bool(manifest.get("hidden", False)),
    )


def discover_reports() -> list[Report]:
    """Return all reports found under reports/. Used by the menu page (M3+).
    Excludes hidden reports (manifest hidden=true) and underscore-prefixed
    directories. Hidden reports remain runnable via direct URL."""
    if not REPORTS_ROOT.exists():
        return []
    out: list[Report] = []
    for child in sorted(REPORTS_ROOT.iterdir()):
        if not child.is_dir() or child.name.startswith("_"):
            continue
        try:
            r = load_report(child.name)
            if r.hidden:
                continue
            out.append(r)
        except (FileNotFoundError, ValueError, json.JSONDecodeError):
            continue
    return out
