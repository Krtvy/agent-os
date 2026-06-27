# Agent-OS — Full Roster
> Last updated: 2026-06-27
> 26 operational agents across 3 tiers. Built on agency-agents (msitarzewski/agency-agents).
> Adopt new agents: `.\adopt.ps1 -Source "division/file.md" -Name "Name" -Emoji "E"`

---

## Tier Structure

```
Meta Layer     — Governance, audit, observation (always running)
Command Layer  — Core 9 + 3 already-adopted specialists (called on every team run)
Specialist Layer — 10 domain experts (called on-demand by task type)
```

---

## Meta Layer (3 agents)

| Agent | Icon | Role | Location |
|-------|------|------|----------|
| **Bhishma** | 📜 | Constitution & governance — 23 rules all agents obey | `_meta/conductor/` |
| **Sahadeva** | ⭐ | Weekly audit — health checks every Sunday | `_meta/audit/` |
| **Observer** | 👁 | Meta-observation — watches agent patterns, proposes upgrades | `_meta/observer/` |

---

## Command Layer (12 agents)

These run in the default `team_coordinator.py` pipeline or are called directly.

| Agent | Icon | Role | Source | Pipeline Step |
|-------|------|------|--------|---------------|
| **Yudhishthira** | ⚖️ | Strategy & decision — worth doing? how? risks? | Native | `01-strategy.md` |
| **Vidura** | 📚 | Research — best approach, refs, tradeoffs | Native | `02-research.md` |
| **Hanuman** | 🐒 | Recon — web intelligence, what already exists | Native (Apify/agent-browser) | `03-recon.md` |
| **Arjuna** | 🏹 | Execution — code, build, ship | Native | `04-execution.md` |
| **Narada** | 🪶 | Writing & voice — drafts, posts, announcements | Native (voice pipeline) | `05-draft.md` |
| **Nakula** | 🐎 | Scheduling — cron, automation, followups | Native | `06-schedule.md` |
| **Sanjaya** | 👁️ | Journaling — session observer, logs everything | Native | `07-journal.md` |
| **Draupadi** | 🔥 | Data engineering — bronze/silver/gold ETL pipelines | `engineering/engineering-data-engineer` | on-demand |
| **Abhimanyu** | 🌀 | Workflow architecture — maps complex processes | `specialized/specialized-workflow-architect` | on-demand |
| **Bhima** | 💪 | Code review — correctness, security, quality | `engineering/engineering-code-reviewer` | on-demand |

> `research-agent/` dir = Vidura. Rename pending.

---

## Specialist Layer (10 agents — adopted 2026-06-27)

Called when a task matches their domain. Add to `--skip` if not needed.

### Engineering Corps (reports to Arjuna)

| Agent | Icon | Role | Source |
|-------|------|------|--------|
| **Krishna** | 🪷 | Multi-agent systems architect — designs agent-to-agent contracts | `engineering/engineering-multi-agent-systems-architect` |
| **Drona** | 🎯 | Software architect — system design, ADRs, tech decisions | `engineering/engineering-software-architect` |
| **Ashwatthama** | ⚡ | AI engineer — LLM integration, RAG, fine-tuning, evals | `engineering/engineering-ai-engineer` |
| **Kritavarma** | 🛡️ | DevOps automator — CI/CD, infra, deployment pipelines | `engineering/engineering-devops-automator` |
| **Vyasa** | ✍️ | Technical writer — docs, READMEs, API references | `engineering/engineering-technical-writer` |

### Security Corps (cross-cutting)

| Agent | Icon | Role | Source |
|-------|------|------|--------|
| **Karna** | ⚔️ | AppSec engineer — threat modeling, OWASP, secure code review | `security/security-appsec-engineer` |

### Product & Strategy Corps (reports to Yudhishthira)

| Agent | Icon | Role | Source |
|-------|------|------|--------|
| **Dhaumya** | 📿 | Product manager — PRDs, sprint planning, feature prioritization | `product/product-manager` |
| **Shakuni** | 🎲 | Growth hacker — distribution, virality, acquisition experiments | `marketing/marketing-growth-hacker` |

### Testing Corps (reports to Sahadeva)

| Agent | Icon | Role | Source |
|-------|------|------|--------|
| **Pandu** | 🔍 | Reality checker — validates claims, tests assumptions, QA | `testing/testing-reality-checker` |

### Orchestration (meta-specialist)

| Agent | Icon | Role | Source |
|-------|------|------|--------|
| **Ghatotkacha** | 👾 | Agents orchestrator — coordinates multi-agent workflows | `specialized/agents-orchestrator` |

---

## How to Call Specialists

```python
# team_coordinator.py — pass specialist IDs in skip to exclude, or route explicitly
python lib/team_coordinator.py "design the architecture for creator-intel v2" --specialists drona,krishna
python lib/team_coordinator.py "security review the auth module" --specialists karna
python lib/team_coordinator.py "write docs for the API" --specialists vyasa
python lib/team_coordinator.py "plan the growth experiment" --specialists shakuni,dhaumya
```

Or directly in Claude Code:
```
@krishna design the agent communication protocol for rootlabs-portal
@karna review this auth module for security issues
@ashwatthama set up the evaluation framework for the RAG pipeline
@vyasa write the README for creator-intel
```

---

## How to Adopt More Agents

```powershell
# From C:\Users\Rawdy — runs in observer-test automatically
.\adopt.ps1 -Source "division/agent-file.md" -Name "MahabharataName" -Emoji "E"

# Examples
.\adopt.ps1 -Source "security/security-penetration-tester.md" -Name "Parashurama" -Emoji "🪓"
.\adopt.ps1 -Source "marketing/marketing-seo-specialist.md" -Name "Ulupi" -Emoji "🌊"
.\adopt.ps1 -Source "marketing/marketing-content-creator.md" -Name "Chitrangada" -Emoji "🌺"
.\adopt.ps1 -Source "engineering/engineering-prompt-engineer.md" -Name "Shukracharya" -Emoji "🔮"
```

Full catalog: https://github.com/msitarzewski/agency-agents (232 agents, 16 divisions)

---

## Suggested Next Adoptions

| Priority | Mahabharata Name | Agency-Agent | Why |
|----------|-----------------|--------------|-----|
| HIGH | Parashurama 🪓 | `security/security-penetration-tester` | For security audits on all projects |
| HIGH | Chitrangada 🌺 | `marketing/marketing-content-creator` | Narada's content sidekick |
| HIGH | Shukracharya 🔮 | `engineering/engineering-prompt-engineer` | Prompt optimization for all LLM calls |
| MED | Ulupi 🌊 | `marketing/marketing-seo-specialist` | SEO for job-scout, cottageai, rootlabs-portal |
| MED | Kripacharya 🧪 | `testing/testing-api-tester` | API testing for rootlabs-portal |
| MED | Uttara 📋 | `project-management/project-management-meeting-notes-specialist` | Session note synthesis |
| LOW | Subhadra 📊 | `support/support-analytics-reporter` | Analytics reports across projects |
| LOW | Jayadratha 🔒 | `security/security-cloud-security-architect` | Cloud infra security |

---

## Full Count

| Layer | Count |
|-------|-------|
| Meta | 3 |
| Command | 10 |
| Specialist | 10 |
| **Total** | **23** |

Plus 3 meta = **26 agents in the ecosystem.**
