"""Background task runner — wraps yudhi_invoker in a daemon thread,
writes status.json so /result/<task_id> can poll for progress.

Design:
  - Submit returns immediately with task_id.
  - Background thread calls Yudhi, writes status.json updates.
  - /result page polls status.json every 2-3s.
  - When done, capture outcome to candidate .md + optional email.

Threading (not Celery/RQ) is fine for Phase 1B's expected concurrency
(~8 POCs, maybe 1-2 concurrent tasks). Phase 2 can swap if needed.
"""
import datetime as dt
import json
import logging
import threading
from pathlib import Path

from .capture import capture_outcome
from .email_notify import send_completion_email
from .yudhi_invoker import invoke_yudhi

log = logging.getLogger("portal.task_runner")


def _write_status(status_file: Path, task_id: str, status: str, extra: dict | None = None) -> None:
    payload = {
        "task_id": task_id,
        "status": status,
        "updated_at": dt.datetime.now().isoformat(),
    }
    if extra:
        payload.update(extra)
    status_file.write_text(json.dumps(payload, default=str, indent=2))


def get_task_status(deliverable_dir: Path) -> dict:
    """Read status.json; return {'status': 'unknown'} if missing."""
    status_file = deliverable_dir / "status.json"
    if not status_file.exists():
        return {"status": "unknown"}
    try:
        return json.loads(status_file.read_text())
    except Exception:
        return {"status": "unknown"}


def run_task_in_background(
    *,
    task_id: str,
    poc_email: str,
    kind: str,
    intent: str,
    template_path: Path | None,
    deliverable_dir: Path,
    candidate_path: Path,
    result_url: str,
    timeout: int = 90,
    claude_bin: str = "claude",
) -> threading.Thread:
    """Spawn daemon thread that runs Yudhi + writes status updates."""
    deliverable_dir.mkdir(parents=True, exist_ok=True)
    status_file = deliverable_dir / "status.json"

    _write_status(status_file, task_id, "running")
    log.info("task_start task_id=%s poc=%s kind=%s timeout=%d",
             task_id, poc_email, kind, timeout)

    def _worker():
        result = invoke_yudhi(
            kind=kind,
            intent=intent,
            deliverable_dir=deliverable_dir,
            template_path=template_path,
            timeout=timeout,
            claude_bin=claude_bin,
        )

        log.info("task_done task_id=%s poc=%s status=%s duration=%.1fs csv=%s md=%s",
                 task_id, poc_email, result["status"], result["duration"],
                 bool(result["csv_path"]), bool(result["md_path"]))

        _write_status(
            status_file,
            task_id,
            result["status"],
            {
                "duration_seconds": round(result["duration"], 1),
                "csv_path": str(result["csv_path"]) if result["csv_path"] else None,
                "md_path": str(result["md_path"]) if result["md_path"] else None,
                "stderr_tail": (result["stderr"] or "")[-500:] or None,
            },
        )

        try:
            capture_outcome(
                candidate_path=candidate_path,
                status=result["status"],
                duration_seconds=result["duration"],
                csv_path=result["csv_path"],
                md_path=result["md_path"],
                error=(result["stderr"] or "")[-500:] or None,
            )
        except Exception as e:
            log.warning("capture_outcome_failed task_id=%s err=%s", task_id, e)

        sent = send_completion_email(
            to=poc_email,
            task_id=task_id,
            status=result["status"],
            result_url=result_url,
        )
        if sent:
            log.info("email_sent task_id=%s poc=%s", task_id, poc_email)

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    return thread
