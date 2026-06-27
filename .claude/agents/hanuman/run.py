"""
Hanuman runner — wraps every research task with tracing + budget.

Usage:
    python .claude/agents/hanuman/run.py "research LangGraph latest features"
    python .claude/agents/hanuman/run.py "find top AI agent repos on GitHub" --depth full
    python .claude/agents/hanuman/run.py --task "scan vercel-labs/agent-browser repo"

What it does:
    1. Checks Hanuman's daily budget (100 requests/day)
    2. Sanitizes the query
    3. Invokes Claude Code with Hanuman's agent context
    4. Traces the run to ~/.agent-os/traces/
    5. Checks for pending events from the event bus
    6. Emits actionable findings back to the event bus
"""

import sys
import subprocess
import time
import os
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from lib.tracer import Tracer, BudgetExceededError
from lib.budget import check_agent_budget, record_request
from lib.event_bus import consume_events, emit_event

AGENT_DIR = Path(__file__).parent
HANUMAN_PROMPT_PREFIX = """You are Hanuman — a general-purpose web research and reconnaissance agent.
Read your agent spec first: .claude/agents/hanuman/agent.md
Read your skill manual: .claude/agents/hanuman/skill.md
Read your platform knowledge: .claude/agents/hanuman/platforms/

Task: """


def main():
    parser = argparse.ArgumentParser(description="Run Hanuman research agent")
    parser.add_argument("query", nargs="?", help="Research query")
    parser.add_argument("--task", help="Research task (alternative to positional)")
    parser.add_argument("--depth", choices=["shallow", "full"], default="shallow")
    parser.add_argument("--model", default="claude-sonnet-4-6")
    parser.add_argument("--max-turns", type=int, default=15)
    args = parser.parse_args()

    task = args.task or args.query
    if not task:
        print("Usage: hanuman/run.py '<research query>'")
        sys.exit(1)

    # Budget check
    ok, reason = check_agent_budget("hanuman")
    if not ok:
        print(f"[hanuman] Budget exceeded: {reason}")
        sys.exit(1)

    # Check for pending events (tasks queued by other agents)
    pending = consume_events("hanuman", "research_request")
    if pending:
        print(f"[hanuman] {len(pending)} pending event(s) from event bus:")
        for e in pending:
            print(f"  - {e['payload'].get('description', e['id'])}")

    full_prompt = HANUMAN_PROMPT_PREFIX + task
    if args.depth == "full":
        full_prompt += "\n\nDepth: full — use multiple sources, cross-reference claims."

    with Tracer("hanuman", task=task[:80]) as t:
        t.log_step("start", input=task, tokens=0)

        start = time.time()
        result = subprocess.run(
            [
                "claude",
                "-p", full_prompt,
                "--model", args.model,
                "--max-turns", str(args.max_turns),
            ],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=270,  # 4.5 min (under 5 min wall clock limit)
        )
        elapsed_ms = int((time.time() - start) * 1000)

        # Estimate tokens from output length (rough: 4 chars ≈ 1 token)
        estimated_tokens = len(result.stdout) // 4 + len(full_prompt) // 4

        success = result.returncode == 0
        output = result.stdout

        t.log_step(
            "research_complete",
            input=task,
            output=output[:300],
            tokens=estimated_tokens,
            latency_ms=elapsed_ms,
            success=success,
        )

        record_request("hanuman")

        if success:
            t.set_outcome("success", summary=f"Research complete ({estimated_tokens} est. tokens)")
            print(output)

            # Emit actionable findings to event bus if output mentions APIs/actions
            action_keywords = ["api", "endpoint", "github issue", "deploy", "run", "execute"]
            if any(kw in output.lower() for kw in action_keywords):
                emit_event("hanuman", "actionable_finding", {
                    "query": task,
                    "output_preview": output[:500],
                    "hint": "May require Arjuna action",
                }, target_agent="arjuna")
                print(f"\n[hanuman] Emitted actionable_finding event to Arjuna")
        else:
            t.set_outcome("failure", summary=f"Research failed: exit {result.returncode}")
            print(f"[hanuman] FAILED: {result.stderr[:300]}", file=sys.stderr)
            sys.exit(result.returncode)


if __name__ == "__main__":
    main()
