"""
Free local observability tracer — no Docker, no cloud, no API key.

Writes JSON trace files to ~/.agent-os/traces/ that you can grep,
query, and analyze. Replaces Langfuse for zero-cost observability.

If you later want Langfuse UI, just point it at the same trace files.

Usage:
    from lib.tracer import Tracer

    with Tracer("hanuman", task="research langchain") as t:
        result = do_work()
        t.log_step("web_search", input="langchain site", output=result, tokens=1200)
        t.set_outcome("success", summary="Found 5 relevant repos")

    # View today's traces:
    # python lib/tracer.py --today
    # python lib/tracer.py --agent hanuman --last 5
"""

from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

TRACES_DIR = Path(os.environ.get("AGENT_OS_TRACES_DIR",
                                  Path.home() / ".agent-os" / "traces"))
TRACES_DIR.mkdir(parents=True, exist_ok=True)

# Free tier Gemini: 1,500 req/day = ~$0. Hard limits prevent surprises.
DEFAULT_BUDGET = {
    "max_tokens": 100_000,     # stop if estimated tokens exceed this
    "max_seconds": 300,        # 5 min wall clock
    "max_steps": 50,           # prevent infinite loops
    "max_requests": 20,        # max LLM/tool calls per run
}


class BudgetExceededError(Exception):
    pass


class Tracer:
    """
    Context manager that traces one agent run.
    Writes a structured JSON file per run.
    Enforces budgets to prevent runaway loops.
    """

    def __init__(
        self,
        agent: str,
        task: str = "",
        budget: Optional[dict] = None,
    ):
        self.agent = agent
        self.task = task
        self.run_id = f"{agent}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%SZ')}-{uuid.uuid4().hex[:6]}"
        self.budget = {**DEFAULT_BUDGET, **(budget or {})}
        self.trace_file = TRACES_DIR / f"{self.run_id}.json"

        self._start_time = time.time()
        self._steps: list[dict] = []
        self._total_tokens = 0
        self._total_requests = 0
        self._outcome: Optional[str] = None
        self._summary: Optional[str] = None
        self._error: Optional[str] = None

    def __enter__(self) -> "Tracer":
        self._write()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None and exc_type is not BudgetExceededError:
            self._error = f"{exc_type.__name__}: {exc_val}"
            self._outcome = "error"
        elif self._outcome is None:
            self._outcome = "completed"
        self._write()

    def log_step(
        self,
        tool: str,
        input: Any = None,
        output: Any = None,
        tokens: int = 0,
        latency_ms: int = 0,
        success: bool = True,
    ) -> None:
        """Log one tool call or LLM step."""
        self._check_budget(tokens)

        self._total_tokens += tokens
        self._total_requests += 1

        self._steps.append({
            "step": len(self._steps) + 1,
            "tool": tool,
            "tokens": tokens,
            "latency_ms": latency_ms,
            "success": success,
            "elapsed_s": round(time.time() - self._start_time, 2),
            "input_preview": str(input)[:200] if input else None,
            "output_preview": str(output)[:200] if output else None,
        })
        self._write()

    def set_outcome(self, outcome: str, summary: str = "") -> None:
        """Call when the agent task completes."""
        self._outcome = outcome
        self._summary = summary
        self._write()

    def _check_budget(self, new_tokens: int = 0) -> None:
        elapsed = time.time() - self._start_time

        if elapsed > self.budget["max_seconds"]:
            self._outcome = "budget_exceeded"
            self._error = f"Wall clock exceeded: {elapsed:.0f}s > {self.budget['max_seconds']}s"
            self._write()
            raise BudgetExceededError(self._error)

        if self._total_tokens + new_tokens > self.budget["max_tokens"]:
            self._outcome = "budget_exceeded"
            self._error = f"Token budget exceeded: {self._total_tokens + new_tokens} > {self.budget['max_tokens']}"
            self._write()
            raise BudgetExceededError(self._error)

        if len(self._steps) >= self.budget["max_steps"]:
            self._outcome = "budget_exceeded"
            self._error = f"Step limit exceeded: {len(self._steps)} >= {self.budget['max_steps']}"
            self._write()
            raise BudgetExceededError(self._error)

        if self._total_requests >= self.budget["max_requests"]:
            self._outcome = "budget_exceeded"
            self._error = f"Request limit exceeded: {self._total_requests} >= {self.budget['max_requests']}"
            self._write()
            raise BudgetExceededError(self._error)

    def _write(self) -> None:
        elapsed = time.time() - self._start_time
        trace = {
            "run_id": self.run_id,
            "agent": self.agent,
            "task": self.task,
            "started_at": datetime.fromtimestamp(
                self._start_time, tz=timezone.utc
            ).isoformat(),
            "elapsed_s": round(elapsed, 2),
            "outcome": self._outcome or "running",
            "summary": self._summary,
            "error": self._error,
            "totals": {
                "tokens": self._total_tokens,
                "steps": len(self._steps),
                "requests": self._total_requests,
            },
            "budget": self.budget,
            "steps": self._steps,
        }
        self.trace_file.write_text(json.dumps(trace, indent=2, default=str))


# ── CLI viewer ────────────────────────────────────────────────────────────────

def view_traces(agent: Optional[str] = None, last_n: int = 10, today_only: bool = False):
    """Print a summary table of recent traces."""
    files = sorted(TRACES_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)

    today = datetime.now().strftime("%Y%m%d")
    rows = []

    for f in files:
        try:
            t = json.loads(f.read_text())
        except Exception:
            continue

        if agent and t.get("agent") != agent:
            continue
        if today_only and today not in t.get("run_id", ""):
            continue

        rows.append(t)
        if len(rows) >= last_n:
            break

    if not rows:
        print("No traces found.")
        return

    print(f"\n{'Run ID':<45} {'Agent':<15} {'Outcome':<15} {'Tokens':<10} {'Steps':<8} {'Time'}")
    print("-" * 110)
    for t in rows:
        tokens = t.get("totals", {}).get("tokens", 0)
        steps = t.get("totals", {}).get("steps", 0)
        elapsed = t.get("elapsed_s", 0)
        print(f"{t['run_id']:<45} {t['agent']:<15} {t.get('outcome','?'):<15} {tokens:<10} {steps:<8} {elapsed:.1f}s")
    print()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", default=None)
    parser.add_argument("--last", type=int, default=10)
    parser.add_argument("--today", action="store_true")
    args = parser.parse_args()
    view_traces(agent=args.agent, last_n=args.last, today_only=args.today)
