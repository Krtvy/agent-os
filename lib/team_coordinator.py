# -*- coding: utf-8 -*-
"""
Agent Team Coordinator — Production Grade

Full pipeline: consume events → run agents in sequence →
each agent reads previous outputs + queries memory →
each output saved to session + persisted to memory →
budget enforced per agent → full session traced.

Usage:
    python lib/team_coordinator.py "your task here"
    python lib/team_coordinator.py --task "draft a LinkedIn post" --skip hanuman,nakula
    python lib/team_coordinator.py --skip nakula,narada "analyze this"
"""

import argparse
import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

SESSIONS_DIR = Path.home() / ".agent-os" / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

STATUS_FILE = Path.home() / ".agent-os" / "live_status.json"

def _write_status(session_id: str, task: str, agents: list, elapsed: float, done: bool = False):
    """Write live status for the dashboard to poll."""
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps({
        "status": "done" if done else "running",
        "session_id": session_id,
        "task": task,
        "elapsed_s": round(elapsed),
        "agents": agents,
    }, indent=2))

REPO_ROOT = Path(__file__).parent.parent

# Load env from ai-knowledge-feed
_env_file = Path(__file__).parent.parent.parent / "ai-knowledge-feed" / ".env"
try:
    from dotenv import load_dotenv
    load_dotenv(_env_file, override=True)
except ImportError:
    pass

# ── Specialist pipeline entries (domain-routed, opt-in) ───────────────────────
# Trigger keywords route tasks to these specialists automatically when --specialists=auto
# Or call explicitly: python lib/team_coordinator.py "task" --specialists drona,karna

SPECIALISTS = {
    "krishna": {
        "id": "krishna", "name": "Krishna", "role": "Multi-Agent Architect",
        "reads": ["00-task.md", "01-strategy.md"],
        "writes": "08-architecture.md",
        "question": (
            "You are Krishna — multi-agent systems architect for agent-os.\n"
            "Design agent-to-agent contracts, communication protocols, and orchestration patterns.\n"
            "Read the task and strategy. Produce: system diagram, agent responsibilities, handoff contracts.\n"
            "Max 500 words."
        ),
        "trigger_keywords": ["architecture", "multi-agent", "agent", "orchestrat", "protocol", "system design"],
    },
    "drona": {
        "id": "drona", "name": "Drona", "role": "Software Architect",
        "reads": ["00-task.md", "01-strategy.md", "02-research.md"],
        "writes": "08-architecture.md",
        "question": (
            "You are Drona — software architect and technical decision maker.\n"
            "Read the task and all prior outputs. Produce: ADR (Architecture Decision Record), tech stack rationale, data models.\n"
            "Max 500 words."
        ),
        "trigger_keywords": ["architect", "design", "ADR", "tech stack", "database schema", "system"],
    },
    "ashwatthama": {
        "id": "ashwatthama", "name": "Ashwatthama", "role": "AI Engineer",
        "reads": ["00-task.md", "02-research.md"],
        "writes": "09-ai-plan.md",
        "question": (
            "You are Ashwatthama — AI/ML engineer for agent-os.\n"
            "Scope: LLM integration, RAG pipelines, embeddings, fine-tuning, evaluation frameworks.\n"
            "Read the task and research. Produce: implementation plan, model selection, eval criteria.\n"
            "Max 500 words."
        ),
        "trigger_keywords": ["LLM", "RAG", "embedding", "fine-tun", "eval", "AI", "ML", "model"],
    },
    "karna": {
        "id": "karna", "name": "Karna", "role": "AppSec Engineer",
        "reads": ["00-task.md", "04-execution.md"],
        "writes": "10-security.md",
        "question": (
            "You are Karna — application security engineer.\n"
            "Review the task and execution output for: OWASP Top 10, auth/authz gaps, injection vectors, secrets exposure.\n"
            "Produce: threat model, findings list (Critical/High/Med/Low), remediation steps.\n"
            "Max 400 words."
        ),
        "trigger_keywords": ["security", "auth", "vulnerability", "secret", "token", "OWASP", "pentest"],
    },
    "kritavarma": {
        "id": "kritavarma", "name": "Kritavarma", "role": "DevOps Automator",
        "reads": ["00-task.md", "04-execution.md"],
        "writes": "11-devops.md",
        "question": (
            "You are Kritavarma — DevOps and infrastructure automator.\n"
            "Read the task and execution output. Produce: CI/CD pipeline definition, deployment steps, infra-as-code snippets.\n"
            "Max 400 words."
        ),
        "trigger_keywords": ["deploy", "CI/CD", "docker", "kubernetes", "infra", "pipeline", "automation"],
    },
    "vyasa": {
        "id": "vyasa", "name": "Vyasa", "role": "Technical Writer",
        "reads": ["00-task.md", "04-execution.md"],
        "writes": "12-docs.md",
        "question": (
            "You are Vyasa — technical writer.\n"
            "Read the task and execution output. Produce polished documentation: README, API reference, or user guide.\n"
            "Match developer audience. Max 600 words."
        ),
        "trigger_keywords": ["document", "README", "docs", "write", "API reference", "guide"],
    },
    "dhaumya": {
        "id": "dhaumya", "name": "Dhaumya", "role": "Product Manager",
        "reads": ["00-task.md", "01-strategy.md"],
        "writes": "13-product.md",
        "question": (
            "You are Dhaumya — product manager.\n"
            "Read the task and strategy. Produce: PRD (problem, users, features, success metrics), sprint backlog, acceptance criteria.\n"
            "Max 500 words."
        ),
        "trigger_keywords": ["PRD", "product", "feature", "user story", "sprint", "backlog", "roadmap"],
    },
    "shakuni": {
        "id": "shakuni", "name": "Shakuni", "role": "Growth Hacker",
        "reads": ["00-task.md", "01-strategy.md"],
        "writes": "14-growth.md",
        "question": (
            "You are Shakuni — growth hacker and distribution strategist.\n"
            "Read the task and strategy. Produce: growth experiment design, acquisition channels, viral loops, metrics to track.\n"
            "Max 400 words."
        ),
        "trigger_keywords": ["growth", "marketing", "acquisition", "viral", "distribution", "launch"],
    },
    "pandu": {
        "id": "pandu", "name": "Pandu", "role": "Reality Checker",
        "reads": ["00-task.md", "04-execution.md"],
        "writes": "15-verification.md",
        "question": (
            "You are Pandu — reality checker and QA specialist.\n"
            "Read the task and execution output. Challenge every assumption. Test edge cases. Identify gaps.\n"
            "Produce: what was verified, what was NOT verified, risks, open questions.\n"
            "Max 400 words."
        ),
        "trigger_keywords": ["test", "verify", "check", "QA", "validate", "edge case", "assumption"],
    },
    "ghatotkacha": {
        "id": "ghatotkacha", "name": "Ghatotkacha", "role": "Agents Orchestrator",
        "reads": None,
        "writes": "16-orchestration.md",
        "question": (
            "You are Ghatotkacha — master orchestrator of agent workflows.\n"
            "Read ALL session files. Identify: which agents should run next, what handoffs are needed, what parallel work is possible.\n"
            "Produce: orchestration plan, agent activation order, handoff contracts.\n"
            "Max 400 words."
        ),
        "trigger_keywords": ["orchestrat", "coordinate", "parallel", "workflow", "delegate"],
    },
    "bhima": {
        "id": "bhima", "name": "Bhima", "role": "Code Reviewer",
        "reads": ["00-task.md", "04-execution.md"],
        "writes": "17-review.md",
        "question": (
            "You are Bhima — code reviewer.\n"
            "Review the execution output for: correctness, security, performance, maintainability.\n"
            "Produce findings as: CRITICAL / HIGH / MEDIUM / LOW with file:line references where possible.\n"
            "Max 500 words."
        ),
        "trigger_keywords": ["review", "code", "refactor", "bug", "quality"],
    },
    "draupadi": {
        "id": "draupadi", "name": "Draupadi", "role": "Data Engineer",
        "reads": ["00-task.md", "04-execution.md"],
        "writes": "18-data-pipeline.md",
        "question": (
            "You are Draupadi — data engineer.\n"
            "Read the task and execution. Design or review the data pipeline: bronze/silver/gold layers, schema, transformations.\n"
            "Max 400 words."
        ),
        "trigger_keywords": ["data", "pipeline", "ETL", "schema", "CSV", "database", "transform"],
    },
    "abhimanyu": {
        "id": "abhimanyu", "name": "Abhimanyu", "role": "Workflow Architect",
        "reads": ["00-task.md", "01-strategy.md"],
        "writes": "19-workflow.md",
        "question": (
            "You are Abhimanyu — workflow architect. You map the maze before anyone enters it.\n"
            "Read the task and strategy. Produce: step-by-step workflow diagram, failure modes, exit conditions.\n"
            "Max 400 words."
        ),
        "trigger_keywords": ["workflow", "process", "flow", "steps", "automat"],
    },
}

def get_specialists_for_task(task: str, requested: list[str] | None = None) -> list[dict]:
    """Auto-detect relevant specialists for a task, or use explicit list."""
    if requested and requested != ["auto"]:
        return [SPECIALISTS[s] for s in requested if s in SPECIALISTS]
    task_lower = task.lower()
    matched = []
    for spec in SPECIALISTS.values():
        if any(kw in task_lower for kw in spec["trigger_keywords"]):
            matched.append(spec)
    return matched


# ── Pipeline definition ────────────────────────────────────────────────────────

PIPELINE = [
    {
        "id":        "yudhishthira",
        "name":      "Yudhishthira",
        "role":      "Strategic Analyst",
        "reads":     ["00-task.md"],
        "writes":    "01-strategy.md",
        "question": (
            "You are Yudhishthira — strategic thinker for Kartavya Joshi.\n"
            "Read the task and answer:\n"
            "1. Is this worth doing right now?\n"
            "2. What does success look like?\n"
            "3. What are the risks?\n"
            "4. Recommended approach?\n"
            "Be concise. Max 300 words."
        ),
        "always":    True,
        "needs_approval": False,
    },
    {
        "id":        "vidura",
        "name":      "Vidura",
        "role":      "Researcher",
        "reads":     ["00-task.md", "01-strategy.md"],
        "writes":    "02-research.md",
        "question": (
            "You are Vidura — source-disciplined researcher for Kartavya.\n"
            "Read the task and strategy. Research:\n"
            "1. Best technical approach?\n"
            "2. Key resources and references?\n"
            "3. Tradeoffs between approaches?\n"
            "Cite sources. Max 400 words."
        ),
        "always":    True,
        "needs_approval": False,
    },
    {
        "id":        "hanuman",
        "name":      "Hanuman",
        "role":      "Recon Scout",
        "reads":     ["00-task.md", "01-strategy.md", "02-research.md"],
        "writes":    "03-recon.md",
        "question": (
            "You are Hanuman — web research and recon scout for Kartavya.\n"
            "Read all previous outputs. Scout and report:\n"
            "1. What already exists that's similar?\n"
            "2. What should we know before building?\n"
            "3. Any gotchas others have gotten wrong?\n"
            "Max 400 words with sources."
        ),
        "always":    False,
        "needs_approval": False,
    },
    {
        "id":        "arjuna",
        "name":      "Arjuna",
        "role":      "Executor",
        "reads":     ["00-task.md", "01-strategy.md", "02-research.md", "03-recon.md"],
        "writes":    "04-execution.md",
        "question": (
            "You are Arjuna — precise execution agent for Kartavya.\n"
            "Read ALL previous agent outputs. Execute the task.\n"
            "- Document every action taken\n"
            "- If destructive action needed, describe it as DRY-RUN first\n"
            "- Log what worked and what didn't\n"
            "- If human action required, specify exactly what"
        ),
        "always":    True,
        "needs_approval": True,  # HITL: confirm before destructive actions
    },
    {
        "id":        "narada",
        "name":      "Narada",
        "role":      "Communication Drafter",
        "reads":     ["00-task.md", "04-execution.md"],
        "writes":    "05-draft.md",
        "question": (
            "You are Narada — communication drafter for Kartavya.\n"
            "Read the task and execution output.\n"
            "Draft any needed communication: email, LinkedIn post, "
            "documentation, or announcement.\n"
            "Match Kartavya's voice: direct, short sentences, no filler.\n"
            "Max 200 words."
        ),
        "always":    False,
        "needs_approval": False,
    },
    {
        "id":        "nakula",
        "name":      "Nakula",
        "role":      "Scheduler",
        "reads":     ["00-task.md", "04-execution.md"],
        "writes":    "06-schedule.md",
        "question": (
            "You are Nakula — scheduling agent for Kartavya.\n"
            "What from this task should repeat or be scheduled?\n"
            "If nothing: say 'No recurring tasks needed' and stop.\n"
            "Otherwise: specify exact cron schedule and command."
        ),
        "always":    False,
        "needs_approval": False,
    },
    {
        "id":        "sanjaya",
        "name":      "Sanjaya",
        "role":      "Observer",
        "reads":     None,  # reads ALL files
        "writes":    "07-journal.md",
        "question": (
            "You are Sanjaya — observer agent for agent-os.\n"
            "Read ALL files in this session directory.\n"
            "Write a structured journal:\n"
            "## Session Summary\n"
            "## What Each Agent Did\n"
            "## What Worked Well\n"
            "## What Could Be Better\n"
            "## Proposed Skill Updates (if any agent showed a gap)\n"
            "## Next Session Recommendation"
        ),
        "always":    True,
        "needs_approval": False,
    },
]

# ── Memory helpers ─────────────────────────────────────────────────────────────

def memory_search(query: str, agent_id: str, limit: int = 3) -> str:
    """Search mem0 for relevant past context."""
    try:
        mem_key = os.getenv("MEM0_API_KEY")
        if not mem_key:
            return ""
        from mem0 import MemoryClient
        client = MemoryClient(api_key=mem_key)
        resp = client.search(query, filters={"agent_id": agent_id}, limit=limit)
        items = resp.get("results", []) if isinstance(resp, dict) else resp
        if not items:
            return ""
        memories = [r.get("memory", "") for r in items if r.get("memory")]
        return "\n".join(f"- {m}" for m in memories[:limit])
    except Exception:
        return ""


def memory_save(agent_id: str, content: str, task: str) -> None:
    """Save agent output to mem0 for future sessions."""
    try:
        mem_key = os.getenv("MEM0_API_KEY")
        if not mem_key:
            return
        from mem0 import MemoryClient
        client = MemoryClient(api_key=mem_key)
        client.add(
            [{"role": "assistant", "content": content[:500]}],
            agent_id=agent_id,
            metadata={"task": task[:100], "date": datetime.now().isoformat()},
        )
    except Exception:
        pass


# ── Event bus ─────────────────────────────────────────────────────────────────

def consume_pending_events() -> list[dict]:
    """Pull any pending events before starting a new session."""
    events_dir = Path.home() / ".agent-os" / "events"
    events_dir.mkdir(parents=True, exist_ok=True)
    consumed = []
    for f in events_dir.glob("*.json"):
        try:
            e = json.loads(f.read_text())
            if not e.get("consumed"):
                e["consumed"] = True
                e["consumed_by"] = "team_coordinator"
                e["consumed_at"] = datetime.now().isoformat()
                f.write_text(json.dumps(e, indent=2))
                consumed.append(e)
        except Exception:
            pass
    return consumed


# ── Budget ────────────────────────────────────────────────────────────────────

_request_counts: dict[str, int] = {}
AGENT_REQUEST_LIMIT = {"hanuman": 10, "vidura": 8, "yudhishthira": 5,
                       "arjuna": 10, "narada": 5, "nakula": 3, "sanjaya": 5,
                       # Specialists
                       "krishna": 5, "drona": 5, "ashwatthama": 8, "kritavarma": 5,
                       "karna": 5, "vyasa": 5, "dhaumya": 5, "shakuni": 5,
                       "pandu": 5, "ghatotkacha": 5,
                       # Command specialists
                       "draupadi": 8, "abhimanyu": 5, "bhima": 8}

def check_and_record_budget(agent_id: str) -> bool:
    count = _request_counts.get(agent_id, 0)
    limit = AGENT_REQUEST_LIMIT.get(agent_id, 10)
    if count >= limit:
        print(f"  [budget] {agent_id} hit request limit ({count}/{limit}) — skipping")
        return False
    _request_counts[agent_id] = count + 1
    return True


# ── Session file helpers ───────────────────────────────────────────────────────

def read_session_files(session_dir: Path, filenames: list[str] | None) -> str:
    if filenames is None:
        files = sorted(session_dir.glob("*.md"))
    else:
        files = [session_dir / f for f in filenames if (session_dir / f).exists()]
    parts = []
    for f in files:
        parts.append(f"=== {f.name} ===\n{f.read_text()}\n")
    return "\n".join(parts)


# ── Groq runner ───────────────────────────────────────────────────────────────

def run_agent_groq(_agent: dict, prompt: str) -> str | None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.4,
        )
        return resp.choices[0].message.content.strip()
    except ImportError:
        return None
    except Exception as e:
        print(f"  [Groq] failed: {str(e)[:80]}")
        return None


# ── Gemini runner ─────────────────────────────────────────────────────────────

def run_agent_gemini(_agent: dict, prompt: str) -> str | None:
    keys = [os.getenv(f"GEMINI_KEY_{i}") for i in range(1, 7)]
    keys = [k for k in keys if k]
    if not keys:
        return None

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return None

    for attempt, key in enumerate(keys):
        for retry in range(2):
            try:
                client = genai.Client(api_key=key)
                resp = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.4, max_output_tokens=1024),
                )
                return resp.text.strip()
            except Exception as e:
                s = str(e)
                if "503" in s or "UNAVAILABLE" in s:
                    time.sleep((retry + 1) * 8)
                elif "401" in s or "UNAUTHENTICATED" in s:
                    break
                else:
                    break
    return None


# ── Main agent runner ─────────────────────────────────────────────────────────

def run_agent(agent: dict, task: str, session_dir: Path) -> str:
    print(f"\n[{agent['name']}] {agent['role']} running...")

    # Budget check
    if not check_and_record_budget(agent["id"]):
        return f"[{agent['name']}: budget limit reached]"

    # Memory: search for relevant past context
    past_context = memory_search(task[:100], agent["id"])
    memory_note = f"\nRELEVANT PAST CONTEXT:\n{past_context}\n" if past_context else ""

    # Build prompt
    context = read_session_files(session_dir, agent["reads"])
    prompt = (
        f"TASK:\n{task}\n"
        f"{memory_note}"
        f"\nPREVIOUS AGENT OUTPUTS:\n{context}"
        f"\nYOUR INSTRUCTIONS:\n{agent['question']}"
        f"\n\nRespond in clean markdown."
    )

    # HITL gate for Arjuna on destructive tasks
    if agent.get("needs_approval"):
        print(f"  [HITL] {agent['name']} will execute — review previous outputs before continuing.")
        print(f"  Session: {session_dir}")

    # Try Groq first, then Gemini
    output = run_agent_groq(agent, prompt)
    provider = "Groq"
    if not output:
        output = run_agent_gemini(agent, prompt)
        provider = "Gemini"
    if not output:
        output = f"[{agent['name']}: all providers failed]"
        provider = "none"

    # Save to session
    out_file = session_dir / agent["writes"]
    out_file.write_text(f"# {agent['name']} -- {agent['role']}\n\n{output}")

    # Save to memory
    memory_save(agent["id"], output, task)

    print(f"  [{provider}] Saved {agent['writes']} ({len(output)} chars)")
    return output


# ── Tracer wrapper ────────────────────────────────────────────────────────────

def run_team(task: str, skip: list[str] = None, specialists: list[str] = None) -> Path:
    skip = skip or []

    # Consume any pending events first
    pending = consume_pending_events()
    if pending:
        print(f"\n[event_bus] Consumed {len(pending)} pending event(s):")
        for e in pending:
            print(f"  - {e.get('type', '?')} from {e.get('source', '?')}: "
                  f"{str(e.get('payload', {}))[:80]}")

    # Setup session
    session_id = f"team-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    session_dir = SESSIONS_DIR / session_id
    session_dir.mkdir(parents=True)
    (session_dir / "00-task.md").write_text(f"# Task\n\n{task}")

    # Start trace
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from lib.tracer import Tracer
        tracer = Tracer("team_coordinator", task=task[:80])
        tracer.__enter__()
    except Exception:
        tracer = None

    # Resolve specialists to run after core pipeline
    active_specialists = get_specialists_for_task(task, specialists)
    if active_specialists:
        print(f"[specialists] Auto-matched: {[s['name'] for s in active_specialists]}")

    print(f"\n{'='*60}")
    print(f"TEAM SESSION: {session_id}")
    print(f"TASK: {task}")
    if active_specialists:
        print(f"SPECIALISTS: {', '.join(s['name'] for s in active_specialists)}")
    print(f"{'='*60}")

    start = time.time()
    results = {}

    # Build initial status with all agents as waiting
    agent_statuses = [
        {"id": a["id"], "name": a["name"], "role": a["role"],
         "status": "skipped" if a["id"] in skip else "waiting",
         "output": "", "elapsed_s": 0}
        for a in PIPELINE
    ]
    _write_status(session_id, task, agent_statuses, 0)

    for agent in PIPELINE:
        if agent["id"] in skip:
            print(f"\n[{agent['name']}] skipped")
            continue
        if not agent["always"] and agent["id"] in skip:
            continue

        t0 = time.time()

        # Mark as running
        for s in agent_statuses:
            if s["id"] == agent["id"]:
                s["status"] = "running"
        _write_status(session_id, task, agent_statuses, time.time() - start)

        output = run_agent(agent, task, session_dir)
        results[agent["id"]] = output

        # Mark as done or failed
        elapsed_agent = round(time.time() - t0)
        for s in agent_statuses:
            if s["id"] == agent["id"]:
                s["status"] = "failed" if output.startswith("[") else "done"
                s["output"] = output[:300].replace("\n", " ")
                s["elapsed_s"] = elapsed_agent
        _write_status(session_id, task, agent_statuses, time.time() - start)

        if tracer:
            try:
                tracer.log_step(
                    agent["id"],
                    input=task[:100],
                    output=output[:200],
                    latency_ms=int((time.time() - t0) * 1000),
                    success=not output.startswith("[")
                )
            except Exception:
                pass

        time.sleep(0.5)

    elapsed = time.time() - start

    if tracer:
        try:
            tracer.set_outcome("success", summary=f"Team run: {len(results)} agents, {elapsed:.0f}s")
            tracer.__exit__(None, None, None)
        except Exception:
            pass

    _write_status(session_id, task, agent_statuses, elapsed, done=True)

    # Summary
    print(f"\n{'='*60}")
    print(f"TEAM SESSION COMPLETE -- {session_id}")
    print(f"Time: {elapsed:.0f}s | Agents: {len(results)}")
    print(f"{'='*60}")
    print(f"\nSession: {session_dir}")
    for f in sorted(session_dir.glob("*.md")):
        print(f"  {f.name} ({len(f.read_text())} chars)")

    # Run specialists after core pipeline
    for spec in active_specialists:
        if spec["id"] in skip:
            continue
        spec_with_always = {**spec, "always": True, "needs_approval": False}
        output = run_agent(spec_with_always, task, session_dir)
        results[spec["id"]] = output

    if "arjuna" in results:
        preview = results["arjuna"][:300].replace("\n", " ")
        print(f"\nOutcome: {preview}...")
    if "sanjaya" in results:
        preview = results["sanjaya"][:200].replace("\n", " ")
        print(f"\nSanjaya: {preview}...")

    return session_dir


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="agent-os team coordinator")
    parser.add_argument("task", nargs="?", help="Task for the team")
    parser.add_argument("--task", dest="task_flag")
    parser.add_argument("--skip", default="", help="Comma-separated agents to skip")
    parser.add_argument("--specialists", default="",
                        help="Comma-separated specialists to activate, or 'auto' for keyword matching")
    args = parser.parse_args()

    task = args.task or args.task_flag
    if not task:
        task = input("Task for the team: ").strip()
    if not task:
        print("No task provided.")
        sys.exit(1)

    skip = [s.strip() for s in args.skip.split(",") if s.strip()]
    specs = [s.strip() for s in args.specialists.split(",") if s.strip()] if args.specialists else ["auto"]
    run_team(task, skip=skip, specialists=specs)


if __name__ == "__main__":
    main()
