"""
Lightweight agent-to-agent event bus for agent-os.

Allows agents to emit events and consume them without direct coupling.
Hanuman can trigger Arjuna automatically when it finds something actionable.

Future upgrade path: swap EVENTS_DIR for Redis Streams (one line change).

Usage:
    # Hanuman emits
    from lib.event_bus import emit_event
    emit_event("hanuman", "actionable_finding", {
        "target_agent": "arjuna",
        "action": "post to GitHub issue",
        "priority": "high",
        "data": {...}
    })

    # Arjuna consumes at session start
    from lib.event_bus import consume_events
    for event in consume_events("arjuna", "actionable_finding"):
        process(event["payload"])
"""

import json
import uuid
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

EVENTS_DIR = Path(os.environ.get(
    "AGENT_OS_EVENTS_DIR",
    Path.home() / ".agent-os" / "events"
))
EVENTS_DIR.mkdir(parents=True, exist_ok=True)

AGENT_CAPABILITIES = {
    "hanuman":      ["research", "web_recon", "github_scan"],
    "narada":       ["draft_email", "draft_message", "draft_cover_letter"],
    "yudhishthira": ["analyze_data", "reconcile_sheets", "compute_stats"],
    "arjuna":       ["api_call", "webhook_post", "github_action"],
    "nakula":       ["schedule_job", "run_script", "cron_trigger"],
    "vidura":       ["deep_research", "source_verification"],
}


def emit_event(
    source_agent: str,
    event_type: str,
    payload: dict,
    priority: str = "normal",
    target_agent: Optional[str] = None,
) -> str:
    """
    Emit an event from source_agent for target_agent (or broadcast if None).
    Returns the event ID.
    """
    event = {
        "id": str(uuid.uuid4()),
        "source": source_agent,
        "target": target_agent,
        "type": event_type,
        "priority": priority,
        "payload": payload,
        "emitted_at": datetime.now(timezone.utc).isoformat(),
        "consumed": False,
        "consumed_by": None,
        "consumed_at": None,
    }
    event_file = EVENTS_DIR / f"{event['id']}.json"
    event_file.write_text(json.dumps(event, indent=2))
    return event["id"]


def consume_events(
    consumer_agent: str,
    event_type: Optional[str] = None,
    max_events: int = 50,
) -> list[dict]:
    """
    Consume pending events addressed to consumer_agent.
    Marks them consumed so they aren't re-processed.
    """
    consumed = []
    event_files = sorted(EVENTS_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime)

    for event_file in event_files:
        if len(consumed) >= max_events:
            break
        try:
            event = json.loads(event_file.read_text())
        except (json.JSONDecodeError, OSError):
            continue

        if event.get("consumed"):
            continue
        if event.get("target") and event["target"] != consumer_agent:
            continue
        if event_type and event.get("type") != event_type:
            continue

        # Mark consumed
        event["consumed"] = True
        event["consumed_by"] = consumer_agent
        event["consumed_at"] = datetime.now(timezone.utc).isoformat()
        event_file.write_text(json.dumps(event, indent=2))
        consumed.append(event)

    return consumed


def peek_events(agent: str, event_type: Optional[str] = None) -> list[dict]:
    """List pending events without consuming them — for status checks."""
    pending = []
    for event_file in EVENTS_DIR.glob("*.json"):
        try:
            event = json.loads(event_file.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        if event.get("consumed"):
            continue
        if event.get("target") and event["target"] != agent:
            continue
        if event_type and event.get("type") != event_type:
            continue
        pending.append(event)
    return pending


def list_capabilities(agent: str) -> list[str]:
    """What can this agent do? Used for routing decisions."""
    return AGENT_CAPABILITIES.get(agent, [])


def route_to_agent(task_description: str) -> Optional[str]:
    """Simple keyword-based routing — which agent should handle this task?"""
    task_lower = task_description.lower()
    routing_rules = [
        (["research", "search", "find", "scout", "scan", "look up"], "hanuman"),
        (["draft", "write message", "email", "cover letter", "outreach"], "narada"),
        (["analyze", "data", "csv", "spreadsheet", "calculate", "stats"], "yudhishthira"),
        (["api", "post", "call", "execute", "send request", "webhook"], "arjuna"),
        (["schedule", "cron", "run daily", "automate", "pipeline"], "nakula"),
        (["deep research", "verify source", "paper", "academic"], "vidura"),
    ]
    for keywords, agent in routing_rules:
        if any(kw in task_lower for kw in keywords):
            return agent
    return None


if __name__ == "__main__":
    # Quick test
    print("Testing event bus...")
    eid = emit_event("hanuman", "actionable_finding", {
        "description": "Found new LangGraph paper on arxiv",
        "url": "https://arxiv.org/abs/test",
        "action_needed": "create GitHub issue for review"
    }, target_agent="arjuna")
    print(f"Emitted event: {eid}")

    events = consume_events("arjuna", "actionable_finding")
    print(f"Arjuna consumed {len(events)} events")
    for e in events:
        print(f"  - {e['payload']['description']}")
