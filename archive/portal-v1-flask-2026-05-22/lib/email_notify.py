"""Optional email notification when Yudhi completes a task.

Skips silently if SMTP_HOST is not configured. Phase 1B local dev runs without
email; Phase 1C VPS deployment wires SMTP creds.
"""
import os
import smtplib
from email.message import EmailMessage


def send_completion_email(*, to: str, task_id: str, status: str, result_url: str) -> bool:
    """Send completion email. Returns True if sent, False if skipped or failed."""
    smtp_host = os.environ.get("SMTP_HOST")
    if not smtp_host:
        return False  # email not configured, skip silently

    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASSWORD")
    from_addr = os.environ.get("SMTP_FROM", smtp_user)

    if not (smtp_user and smtp_pass and from_addr):
        return False

    msg = EmailMessage()
    msg["Subject"] = f"Rootlabs Data Portal — Task {task_id[:8]} {status}"
    msg["From"] = from_addr
    msg["To"] = to
    msg.set_content(
        f"Your Rootlabs data task has finished.\n"
        f"\n"
        f"Status: {status}\n"
        f"Task ID: {task_id}\n"
        f"View result: {result_url}\n"
    )

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as s:
            s.starttls()
            s.login(smtp_user, smtp_pass)
            s.send_message(msg)
        return True
    except Exception:
        return False
