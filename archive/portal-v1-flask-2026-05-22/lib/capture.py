"""Pattern candidate writer for build-as-capture.

Writes one .md per task in CANDIDATES_DIR. Two phases:
  - capture_request: before Yudhi runs, captures intent + inputs.
  - capture_outcome: after Yudhi runs (or times out), appends result.

Promotion: weekly review by Kartavya — any shape appearing >=3 times gets
promoted into training/patterns/<slug>.md.
"""
import datetime as dt
import re
from pathlib import Path

PENDING_MARKER = "_pending — Yudhi has not finished yet_"


def _slugify(text: str, maxlen: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:maxlen] or "untitled"


def candidate_path(candidates_dir: Path, task_id: str, poc_email: str, intent: str) -> Path:
    date = dt.date.today().isoformat()
    poc = poc_email.split("@")[0]
    slug = _slugify(intent)
    return candidates_dir / f"{date}-{poc}-{slug}-{task_id[:8]}.md"


def capture_request(
    *,
    candidates_dir: Path,
    task_id: str,
    poc_email: str,
    kind: str,
    intent: str,
    template_filename: str | None = None,
) -> Path:
    """Write a candidate .md BEFORE invoking Yudhi.

    kind: 'ask' or 'upload'
    intent: the user's question (ask) or instructions textarea (upload)
    """
    candidates_dir.mkdir(parents=True, exist_ok=True)
    path = candidate_path(candidates_dir, task_id, poc_email, intent)
    body = f"""---
task_id: {task_id}
poc: {poc_email}
kind: {kind}
created_at: {dt.datetime.now().isoformat()}
status: pending
---

## Intent

{intent}

## Inputs

- kind: {kind}
- template_file: {template_filename or 'N/A'}

## Outcome

{PENDING_MARKER}
"""
    path.write_text(body)
    return path


def capture_outcome(
    *,
    candidate_path: Path,
    status: str,
    duration_seconds: float | None = None,
    csv_path: Path | None = None,
    md_path: Path | None = None,
    error: str | None = None,
) -> None:
    """Append outcome to an existing candidate .md."""
    dur = f"{duration_seconds:.1f}s" if duration_seconds is not None else "N/A"
    block = f"""## Outcome (updated {dt.datetime.now().isoformat()})

- status: {status}
- duration: {dur}
- deliverable_csv: {csv_path or 'N/A'}
- deliverable_md: {md_path or 'N/A'}
- error: {error or 'N/A'}"""

    text = candidate_path.read_text()
    text = text.replace(f"## Outcome\n\n{PENDING_MARKER}", block)
    text = text.replace("status: pending", f"status: {status}", 1)
    candidate_path.write_text(text)
