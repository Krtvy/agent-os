"""
Traced wrapper for nakula-run.sh

Wraps every Nakula job with the Tracer so all runs appear
in ~/.agent-os/traces/ for observability.

Usage:
    python .claude/agents/nakula/scripts/nakula-traced.py <job-name> [--dry-run]
    python .claude/agents/nakula/scripts/nakula-traced.py sanjaya
    python .claude/agents/nakula/scripts/nakula-traced.py ai-knowledge-feed --dry-run
"""

import sys
import subprocess
import time
from pathlib import Path

# Add repo root to path for lib imports
REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from lib.tracer import Tracer
from lib.budget import check_agent_budget, record_request


def main():
    if len(sys.argv) < 2:
        print("Usage: nakula-traced.py <job-name> [--dry-run]")
        sys.exit(1)

    job_name = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    # Budget check
    ok, reason = check_agent_budget("nakula")
    if not ok:
        print(f"[nakula-traced] Budget exceeded: {reason}")
        sys.exit(1)

    shell_script = Path(__file__).parent / "nakula-run.sh"

    # Find bash on Windows (Git Bash) or use system bash on Unix
    import shutil, platform
    if platform.system() == "Windows":
        bash = shutil.which("bash") or r"C:\Program Files\Git\bin\bash.exe"
        # Prefer Git Bash over Windows Subsystem for Linux stub
        git_bash = r"C:\Program Files\Git\bin\bash.exe"
        if Path(git_bash).exists():
            bash = git_bash
    else:
        bash = "bash"

    with Tracer("nakula", task=f"job:{job_name}", budget={"max_seconds": 3600, "max_steps": 10}) as t:
        cmd = [bash, str(shell_script), job_name]
        if dry_run:
            cmd.append("--dry-run")

        t.log_step("job_start", input=job_name, tokens=0)

        start = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        elapsed_ms = int((time.time() - start) * 1000)

        success = result.returncode == 0
        output = result.stdout[-500:] if result.stdout else result.stderr[-500:]

        t.log_step(
            "job_complete",
            input=job_name,
            output=output,
            tokens=0,
            latency_ms=elapsed_ms,
            success=success,
        )

        record_request("nakula")

        if success:
            t.set_outcome("success", summary=f"{job_name} completed in {elapsed_ms}ms")
            print(f"[nakula-traced] {job_name}: OK ({elapsed_ms}ms)")
        else:
            t.set_outcome("failure", summary=f"{job_name} failed: exit {result.returncode}")
            print(f"[nakula-traced] {job_name}: FAILED (exit {result.returncode})")
            if result.stderr:
                print(result.stderr[-300:])
            sys.exit(result.returncode)


if __name__ == "__main__":
    main()
