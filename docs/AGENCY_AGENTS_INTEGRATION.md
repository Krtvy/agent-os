# Agency-Agents Integration

> Added 2026-06-27. Source repo: github.com/msitarzewski/agency-agents (116k+ stars, MIT license)

## TL;DR

Agency-agents provides 232 battle-tested specialist agents across 16 professional divisions. The observer-ecosystem provides governance, memory, observability, and scheduling. Combined with Hermes Agent for background automation, the three systems create a fully-governed, domain-rich, always-on agent platform.

---

## System Comparison

| Dimension | Observer-Ecosystem (Bhishma) | Agency-Agents | Hermes Agent |
|-----------|------------------------------|---------------|--------------|
| **Agent count** | 9 agents | 232 agents | Skill-based |
| **Domain breadth** | Narrow (data + ops) | Vast (16 divisions) | Execution-focused |
| **Governance** | Full (Bhishma R1–R20) | None | None |
| **Memory** | Playbook + memories.md | None | Persistent ~/.hermes/ |
| **Audit trail** | run_id + Sahadeva | None | Logs only |
| **Scheduling** | Nakula cron | None | Native cron |
| **Observability** | Sanjaya + Vyasa | None | health.json |
| **Tier structure** | Strict (0, 1, 2, audit) | None | N/A |
| **Success metrics** | Implicit | Explicit per agent | N/A |
| **Production-tested** | Custom-built | Yes (community) | Yes |

**Insight:** Agency-agents has the specialists; the observer-ecosystem has the governance; Hermes has the persistence. Together they cover everything.

---

## Architecture (Post-Integration)

```
Kartavya (human)
    │
    ├── Tier 2: Vyasa (conductor — enhanced with orchestration patterns)
    │       │
    │       └── Tier 1: Sanjaya (observer — now watches 12 agents)
    │               │
    │               ├── ORIGINAL Tier-0 (Mahabharata-named)
    │               │   ├── Yudhishthira   (data analyst)
    │               │   ├── Arjuna         (executor)
    │               │   ├── Hanuman        (scout / research)
    │               │   ├── Narada         (drafter)
    │               │   ├── Nakula         (automation)
    │               │   └── Vidura         (deep research)
    │               │
    │               └── ADOPTED Tier-0 (agency-agents, Bhishma-wrapped)
    │                   ├── Draupadi       (data engineer) ← engineering-data-engineer
    │                   ├── Abhimanyu      (workflow architect) ← specialized-workflow-architect
    │                   └── Bhima          (code reviewer) ← engineering-code-reviewer
    │
    ├── Tier-Audit: Sahadeva (weekly external audit — unchanged)
    │
    └── Parallel: Hermes Agent (background watchdog + slash commands)
                bound by
            Bhishma (constitution — R1–R20 + new R21–R23)
```

---

## The Bhishma-Wrapper Principle

Agency-agents are designed to be standalone — no governance, no tier, no run_id. Before any agency-agent enters the observer-ecosystem, it must be **Bhishma-wrapped**:

1. Add `tier: 0` in frontmatter
2. Declare explicit `write_scope` and `read_scope`
3. Declare `upstream` and `downstream`
4. Add a `source:` field pointing to the original agency-agents file
5. Prepend a Bhishma compliance block (R2, R5, R11, R19, R20)
6. Give the agent a Mahabharata name that fits its function

Use `scripts/adopt-agency-agent.sh` to automate this. See examples in the three pre-wrapped agents already deployed.

---

## New Bhishma Rules (R21–R23)

Add these to `_meta/conductor/bhishma.md`:

- **R21 — Source attribution**: Every adopted agency-agent must declare `source: agency-agents/<division>/<file>` in frontmatter. This enables traceability and upstream updates.
- **R22 — No personality drift**: Adopted agents keep the agency-agents workflow and success metrics verbatim. Personality sections may be localized to the Rootlabs context (POC names, data sources) but domain rules must not be weakened.
- **R23 — Sanjaya coverage**: Every new Tier-0 agent, whether original or adopted, must write to `logs/<agent-name>/` in the standard format. Sanjaya will add it to her monitoring roster.

---

## Priority Adoption Queue

Agents ranked by immediate value for Kartavya's Rootlabs work (creator data, GMV analysis, portal build):

### Wave 1 — Already deployed (2026-06-27)
| Mahabharata name | Agency-agents source | Why now |
|-----------------|---------------------|---------|
| **Draupadi** | `engineering/engineering-data-engineer.md` | Builds the Bronze→Silver→Gold data pipelines Yudhishthira consumes; owns ETL for Kalodata/Cruva |
| **Abhimanyu** | `specialized/specialized-workflow-architect.md` | Maps the portal workflows before a line of code is written (Phase 2 prerequisite) |
| **Bhima** | `engineering/engineering-code-reviewer.md` | Reviews all Python scripts, catches security/correctness issues before Arjuna executes |

### Wave 2 — Next (adopt when portal work begins)
| Mahabharata name | Agency-agents source | Why |
|-----------------|---------------------|-----|
| **Karna** | `security/security-application-security.md` | Portal auth + data exposure review |
| **Shakuni** | `product/product-manager.md` | Sprint prioritization for portal Phase 2 |
| **Kunti** | `support/support-customer-service.md` | POC-facing support patterns for the portal |

### Wave 3 — When team scales
| Mahabharata name | Agency-agents source | Why |
|-----------------|---------------------|-----|
| **Drona** | `specialized/corporate-training-designer.md` | Train POCs to use the portal autonomously |
| **Drupada** | `specialized/recruitment-specialist.md` | If Rootlabs hires data ops staff |
| **Duryodhana** | `specialized/business-strategist.md` | Competitive strategy for the creator economy |

---

## How Draupadi + Yudhishthira Work Together

This is the most important pairing:

```
Raw data (CSV / Sheets / API)
        │
        ▼
   Draupadi (data engineer)
   - Builds the pipeline: ingest → clean → deduplicate
   - Outputs: Bronze → Silver → Gold CSVs
   - Owns: schema contracts, null handling, audit timestamps
        │
        ▼
   Yudhishthira (data analyst)
   - Reads from Gold layer only
   - Does: breakdown, reconciliation, time-series, GMV calc
   - Outputs: .csv + .md deliverable pair for POCs
```

Previously Yudhishthira was doing both engineering AND analysis. Draupadi takes the engineering half, making Yudhishthira's analysis more reliable and faster.

---

## How Abhimanyu + Arjuna Work Together

```
   Abhimanyu (workflow architect)
   - Maps EVERY portal workflow before implementation
   - Outputs: workflow registry (by workflow, by component, by user journey)
   - Rule: no code, only specs
        │
        ▼
   Arjuna (executor)
   - Reads Abhimanyu's spec
   - Implements against the spec
   - Circuit breakers still apply (R_arjuna)
```

This prevents the Portal Phase 2 anti-pattern: "don't build the portal tonight" (VISION.md). Abhimanyu forces spec-first before Arjuna touches code.

---

## How Bhima + Arjuna Work Together

```
   Arjuna (executor) writes code
        │
        ▼
   Bhima (code reviewer)
   - 🔴 Blockers: security, data corruption, race conditions
   - 🟡 Suggestions: validation gaps, naming, missing tests
   - 💭 Nits: style
   - Outputs: review report in logs/bhima/
        │
        ▼
   Arjuna revises (if blockers) or Kartavya decides (if suggestions only)
```

---

## Adopting More Agents

To add a new agency-agent in the future:

```bash
cd ~/projects/observer-test
bash scripts/adopt-agency-agent.sh \
  --source "engineering/engineering-senior-developer.md" \
  --name "Krishna" \
  --tier 0 \
  --emoji "🎯"
```

This will:
1. Download the source file from the agency-agents repo
2. Apply the Bhishma wrapper (tier, write_scope, read_scope, run_id, R2/R5/R11/R19/R20)
3. Create `~/.claude/agents/<name>/agent.md` and `skill.md`
4. Append to Sanjaya's monitoring list

Review the output before committing — always verify the `write_scope` is correctly scoped to the agent's own directory.

---

## What NOT to Import

Some agency-agents conflict with existing roles:

| Agency-agents agent | Why to skip |
|--------------------|-------------|
| `agents-orchestrator` | Vyasa already does this |
| `specialized/chief-of-staff` | Vyasa + Bhishma already cover this |
| Any agent duplicating Yudhishthira's analysis | Preserve Yudhishthira's GMV specialization |
| `engineering/engineering-incident-response-commander` | Arjuna handles incident-class tasks |

---

## Full Stack Summary

```
┌─────────────────── GOVERNANCE ────────────────────────┐
│  Bhishma constitution (R1–R23)                        │
│  Sahadeva weekly audit                                │
└───────────────────────────────────────────────────────┘
┌─────────────────── INTELLIGENCE ──────────────────────┐
│  Observer-ecosystem Claude Code agents (12 total)     │
│  9 original + 3 agency-adopted (Wave 1)               │
│  All governed, all audited, all logged                │
└───────────────────────────────────────────────────────┘
┌─────────────────── PERSISTENCE ───────────────────────┐
│  Hermes Agent (background daemon)                     │
│  - Health watchdog cron every 6h                      │
│  - /observer-status, /nakula-trigger slash commands   │
└───────────────────────────────────────────────────────┘
```

This is the full stack. Three systems, each doing what it does best, none duplicating the others.
