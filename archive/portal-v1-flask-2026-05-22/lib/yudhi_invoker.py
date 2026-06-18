"""Headless Yudhi invocation via `claude --print --agent yudhishthira`.

Yudhi is instructed (via prompt) to write deliverables to exact paths
the portal controls. The portal then confirms those files exist.
"""
import subprocess
import time
from pathlib import Path


def build_prompt(
    *,
    kind: str,
    intent: str,
    template_path: Path | None,
    deliverable_dir: Path,
) -> str:
    csv_target = deliverable_dir / "result.csv"
    md_target = deliverable_dir / "audit.md"

    parts = [
        "You are Yudhishthira, invoked via the Rootlabs POC portal.",
        "",
        f"Task kind: {kind}",
        "",
        "Deliverables MUST be written to these exact paths:",
        f"  - CSV: {csv_target}",
        f"  - Audit MD: {md_target}",
        "",
        "Follow your standard loop (INSPECT → CLASSIFY → DECLARE FILTERS → COMPUTE → AUDIT → DELIVER).",
        "Skip the backup guardrail — this is a portal-initiated read-only task.",
        "",
    ]
    if template_path:
        parts += [
            f"Template uploaded by the POC: {template_path}",
            "Fill in the missing columns of the template, then write the result to the CSV target above.",
            "",
        ]
    parts += [
        "User request:",
        intent,
    ]
    return "\n".join(parts)


def invoke_yudhi(
    *,
    kind: str,
    intent: str,
    deliverable_dir: Path,
    template_path: Path | None = None,
    timeout: int = 90,
    claude_bin: str = "claude",
) -> dict:
    """Invoke Yudhi synchronously.

    Returns: {status, duration, csv_path, md_path, stdout, stderr}
    where status in {'success', 'timeout', 'error'}.
    """
    deliverable_dir.mkdir(parents=True, exist_ok=True)
    prompt = build_prompt(
        kind=kind, intent=intent, template_path=template_path, deliverable_dir=deliverable_dir
    )

    csv_target = deliverable_dir / "result.csv"
    md_target = deliverable_dir / "audit.md"

    # When claude runs as a subprocess (no interactive user to approve tools),
    # we must pre-allow the tools Yudhi needs. Narrow allowlist, not
    # --dangerously-skip-permissions, so the trust surface stays explicit.
    allowed_tools = (
        "Read Write Edit MultiEdit Glob Grep LS "
        "Bash(lib/yudhi-sql.sh *) "
        "Bash(lib/yudhi-fetch.sh *) "
        "Bash(lib/yudhi-py.sh *) "
        "Bash(cat *) Bash(head *) Bash(tail *) Bash(wc *) "
        "Bash(grep *) Bash(ls *) Bash(mkdir *) Bash(echo *)"
    )

    start = time.time()
    try:
        result = subprocess.run(
            [
                claude_bin,
                "--print",
                "--agent", "yudhishthira",
                "--allowedTools", allowed_tools,
            ],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        duration = time.time() - start
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "duration": time.time() - start,
            "csv_path": None,
            "md_path": None,
            "stdout": "",
            "stderr": f"Yudhi exceeded timeout of {timeout}s",
        }
    except FileNotFoundError as e:
        return {
            "status": "error",
            "duration": time.time() - start,
            "csv_path": None,
            "md_path": None,
            "stdout": "",
            "stderr": f"`{claude_bin}` not found on PATH: {e}",
        }
    except Exception as e:
        return {
            "status": "error",
            "duration": time.time() - start,
            "csv_path": None,
            "md_path": None,
            "stdout": "",
            "stderr": str(e),
        }

    csv_exists = csv_target.exists()
    md_exists = md_target.exists()
    if csv_exists and md_exists:
        status = "success"
    elif csv_exists or md_exists:
        status = "partial"  # got one but not both — POC should be told
    else:
        status = "error"

    return {
        "status": status,
        "duration": duration,
        "csv_path": csv_target if csv_exists else None,
        "md_path": md_target if md_exists else None,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
