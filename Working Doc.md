# Thread Context

Key facts and notes for this thread. Updated by agent, survives context compaction.

## Plan Overview

Kartavya Joshi has designed a Mahabharata-themed multi-tier agent ecosystem for his Claude Code setup at Rootlabs. The system has Tier 0 workers (vidura, narada, hanuman, arjuna, nakula), a Tier 1 Observer (sanjaya), a Tier 2 Conductor (vyasa), an external weekly Auditor (sahadeva), and a constitution file (bhishma) that binds them all.

The user wants me to (1) analyze and improve the plan, (2) generate clean deployable files (agent.md, skill.md, scripts, docs) so he can drop them into his own system. Output is a downloadable bundle, not Hyperagent agents.

My approach: critique the existing prompts, identify gaps, propose system-level upgrades and per-agent improvements, then generate a complete deployment bundle (tarball + individual file placeholders) covering all 6 agents in the build batch plus the constitution, supporting docs, scripts, and a deploy.sh installer.

## Plan Tasks

- [x] Set up workspace directory structure for the bundle
- [x] Write bhishma.md constitution with R1-R20 (5 new rules added)
- [x] Write shared docs (SKILL_TEMPLATE.md, RUN_ID_SPEC.md, BOOTSTRAP.md, ARCHITECTURE.md)
- [x] Generate sanjaya agent.md and skill.md (Tier 1 Observer)
- [x] Generate vidura agent.md and skill.md (Tier 0 research, T1-T5 source tiering)
- [x] Generate vyasa agent.md and skill.md with drift metrics, loop detection, recovery clause
- [x] Generate sahadeva agent.md and skill.md with trend lines, silence detection, dependency hash
- [x] Generate hanuman agent.md and skill.md with cache layer, stale-data warnings, handle resolution
- [x] Generate narada agent.md and skill.md with voice fingerprinting, generic-reject, audience model
- [x] Generate arjuna agent.md and skill.md with idempotency keys, rollback plans, circuit breaker
- [x] Generate nakula agent.md and skill.md with log rotation, weekly self-summary, schema validator
- [x] Write run scripts (run_sanjaya.sh, run_vyasa.sh, run_sahadeva.sh, run_nakula.sh, jobs.yml.example, crontab.example)
- [x] Write README.md and deploy.sh installer
- [x] Bundle everything into observer-ecosystem.tar.gz, save tarball and key files with placeholders

## Plan Context

### Analysis — what's strong
- Strict tier separation (workers/observer/conductor/auditor) with clean read/write boundaries
- Constitutional governance via Bhishma — internalized constraints, not external supervision
- Approval gates prevent runaway self-modification
- Sahadeva is independently stateless — corruption-resistant cross-check
- Mythological framing gives each agent a memorable, distinct posture

### Analysis — gaps to fix at system level
1. Sanjaya itself is referenced but not in the build batch — Vyasa watches a non-existent agent unless sanjaya already exists locally
2. Vidura (Tier-0 research) is referenced by other prompts but not built
3. No "Krishna"/strategist role defined — Arjuna executes, but who plans? Currently implicit (Kartavya). Worth defining the planner interface formally.
4. Confidence-scoring formula is referenced (high/medium/low bands) but math is undefined anywhere
5. run_id schema is not standardized — Bhishma R10 requires "3 distinct example_run_ids" but no format spec
6. skill.md template not defined — every agent has one but no canonical shape
7. Bootstrap order undefined — what if sanjaya runs before bhishma exists?
8. Cross-tier conflict resolution unspecified — what if vyasa proposes a change while a sanjaya proposal is pending on the same target?
9. Time-zone inconsistency — IST mixed with implicit local. Recommend UTC-internal, IST-display.
10. Heartbeat ownership — multiple agents read logs/heartbeat.json; only nakula writes it. Should be enforced by file ACL or explicit rule.

### Per-agent improvements I'll bake in

Vyasa — quantitative drift metric (confidence variance, journal entropy threshold), explicit loop-detection (never reference own previous proposals), recovery clause (corrupt files → journal-and-exit, never auto-fix).

Sahadeva — multi-week trend lines (4-week rolling delta on calibration), agent-silence detection (no journal entry in N days = flag), quantitative miscalibration thresholds (high-band approval <70% → flag), dependency check (hash of bhishma.md as loaded by each agent matches current).

Hanuman — response cache layer (don't hammer Kalodata for same handle within 24h), stale-data banner (data >24h gets warning), handle-resolution check (creator may have renamed), batch deduplication.

Narada — voice fingerprint extraction (style markers from past samples, not just freeform read), hard generic-reject filter (template-matched output rejected before delivery), audience model section, length budget enforced before generation, not after.

Arjuna — idempotency keys for all state-changing calls, rate-limit backoff, rollback plan field per live action, circuit breaker (3 failures in a row on same target = pause that target).

Nakula — log rotation (daily compress), weekly self-summary heartbeat (so sahadeva can see the schedule healthy), public health endpoint (other agents can check heartbeat freshness via file read), jobs.yml schema validator on read.

Bhishma — add 5 rules: R16 git-tracked with rationale commits, R17 no recursive audit, R18 voice impersonation forbidden, R19 UTC-internal timestamps, R20 run_id format mandatory across ecosystem.

### Deliverables — bundle structure

```
observer-ecosystem/
├── README.md                              deployment instructions
├── deploy.sh                              one-shot installer
├── .claude/agents/
│   ├── _meta/
│   │   ├── conductor/                     vyasa + bhishma
│   │   │   ├── agent.md, skill.md, bhishma.md
│   │   │   ├── journal/, reports/, proposals/, approved/, rejected/
│   │   │   └── templates/proposal.md.tmpl
│   │   └── audit/                         sahadeva
│   │       ├── agent.md, skill.md
│   │       └── reports/
│   ├── hanuman/, narada/, arjuna/, nakula/
│   │   └── agent.md, skill.md per agent
│   └── *.md                               symlinks at top level
├── scripts/
│   ├── run_vyasa.sh, run_sahadeva.sh, run_nakula.sh
│   ├── jobs.yml.example
│   └── crontab.example
└── docs/
    ├── ARCHITECTURE.md                    tier diagram + data flow
    ├── SKILL_TEMPLATE.md                  canonical skill.md structure
    ├── RUN_ID_SPEC.md                     standardized run_id format
    └── BOOTSTRAP.md                       agent bring-up order
```

### Build sequence
1. Bhishma constitution + shared docs (skill template, run_id spec, bootstrap)
2. Each agent.md + skill.md with improvements baked in (vyasa → sahadeva → hanuman → narada → arjuna → nakula)
3. Run scripts, jobs.yml example, crontab.example
4. README + deploy.sh installer
5. Tarball the lot, save via SaveFile so user can download
6. Also save individual key files (bhishma.md, each agent.md) with their own placeholders for direct copy

### Open questions — please confirm before I start

1. **Sanjaya & Vidura** — do these already exist on your machine, or should I include them in this build batch too? (Important: Vyasa is meaningless without Sanjaya, and several prompts reference Vidura.)
2. **Project path** — `~/projects/observer-test/.claude/agents/` — is this still correct?
3. **Improvement adoption** — apply all proposed improvements wholesale, or do you want a pre-build pass where you accept/reject each?
4. **Krishna/strategist** — should I define this role too (interface-only, since you may play it yourself), or skip for now?
5. **Bundle format** — tarball + key file placeholders is my default. Any preference for ZIP, individual files only, or something else?
