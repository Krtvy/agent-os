"""
Hard budget limits for all agent runs.
Free tier Gemini = $0, but we still limit to prevent infinite loops
and excessive API usage that could exhaust daily quotas.

Import this at the top of any script that calls Gemini or runs agents.
"""

# ── Gemini free tier limits ────────────────────────────────────────────────
GEMINI_FREE_TIER = {
    "requests_per_day":    1_500,   # per key
    "requests_per_minute": 15,      # per key
    "tokens_per_minute":   1_000_000,
}

# ── Per-agent daily request budgets (out of 7,500 total across 5 keys) ────
AGENT_DAILY_BUDGETS = {
    "discover":   200,   # GitHub discovery pipeline
    "youtube":    100,   # YouTube transcripts
    "papers":     50,    # ArXiv papers
    "feeds":      50,    # RSS articles
    "digest":     10,    # Weekly digest (single call)
    "hanuman":    100,   # Research runs
    "arjuna":     50,    # API execution
    "narada":     30,    # Drafting
    "yudhishthira": 50,  # Data analysis
    "nakula":     10,    # Scheduling
}

# ── Per-run hard limits (prevent the $4,200 incident on free tier) ─────────
PER_RUN_LIMITS = {
    "max_tokens":   50_000,   # stop if token estimate exceeds this
    "max_seconds":  300,      # 5 min wall clock per run
    "max_steps":    50,       # max tool calls per agent run
    "max_requests": 20,       # max LLM calls per run
}

# ── Budget tracker (in-memory, resets per process) ─────────────────────────
_usage: dict[str, int] = {}

def check_agent_budget(agent: str) -> tuple[bool, str]:
    """Returns (within_budget, reason). Call before each agent run."""
    used = _usage.get(agent, 0)
    limit = AGENT_DAILY_BUDGETS.get(agent, 100)
    if used >= limit:
        return False, f"{agent} exhausted daily budget ({used}/{limit} requests)"
    return True, ""

def record_request(agent: str, count: int = 1) -> None:
    """Call after each Gemini request to track usage."""
    _usage[agent] = _usage.get(agent, 0) + count

def usage_report() -> None:
    """Print current usage across all agents."""
    print("\nAgent budget usage (this process):")
    for agent, limit in AGENT_DAILY_BUDGETS.items():
        used = _usage.get(agent, 0)
        pct = (used / limit * 100) if limit else 0
        bar = "#" * int(pct / 5) + "." * (20 - int(pct / 5))
        print(f"  {agent:<15} [{bar}] {used}/{limit} ({pct:.0f}%)")
    print()
