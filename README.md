# observer-ecosystem

Multi-tier agent ecosystem for Kartavya Joshi at Rootlabs. Mahabharata-themed: workers, observer, conductor, auditor, all bound by a constitution.

```
Kartavya (human)
    │
    ├── Tier 2: Vyasa            (watches Sanjaya)
    │       │
    │       └── Tier 1: Sanjaya  (watches all Tier-0 workers)
    │               │
    │               ├── Tier 0: Vidura     (research)
    │               ├── Tier 0: Hanuman    (scout)
    │               ├── Tier 0: Narada     (drafter)
    │               ├── Tier 0: Arjuna     (executor)
    │               └── Tier 0: Nakula     (automation)
    │
    └── Tier-Audit: Sahadeva      (weekly external audit, reports direct to Kartavya)
                  bound by
              Bhishma (constitution)
```

## What's in this bundle

```
observer-ecosystem/
├── README.md                       (this file)
├── deploy.sh                       one-shot installer
├── dot-claude/agents/              renamed to .claude/agents/ on install
│   ├── _meta/
│   │   ├── conductor/              vyasa + bhishma.md
│   │   ├── observer/               sanjaya
│   │   └── audit/                  sahadeva
│   ├── vidura/, hanuman/, narada/, arjuna/, nakula/
│   └── (top-level .md symlinks created by deploy.sh)
├── scripts/                        run_*.sh, jobs.yml.example, crontab.example
├── docs/                           ARCHITECTURE, BOOTSTRAP, RUN_ID_SPEC, SKILL_TEMPLATE
├── logs/                           empty, populated at runtime
└── research/                       empty, populated at runtime
```

## Quick install

```bash
# Extract the tarball wherever you keep agent projects
mkdir -p ~/projects && cd ~/projects
tar -xzf observer-ecosystem.tar.gz
cd observer-ecosystem

# Run the installer (renames dot-claude → .claude, makes scripts executable,
# creates symlinks at top level of .claude/agents/, copies to ~/projects/observer-test/)
bash deploy.sh ~/projects/observer-test
```

After install:

```bash
cd ~/projects/observer-test
git init && git add . && git commit -m "bhishma: initial constitution + 8 agents"
```

Then follow `docs/BOOTSTRAP.md` for the phased bring-up (foundation → Tier-0 → Tier-1 → Tier-2 → audit).

## What was added beyond the original prompts

This bundle implements your seven prompts plus:

- **Sanjaya and Vidura** — the Tier-1 Observer and Tier-0 research agent. Both were referenced everywhere but not in the original build batch. Built here so the supervisory chain is complete from day one.
- **Bhishma R16–R20** — five new constitutional rules: git-tracked constitution with rationale commits (R16), no recursive audit (R17), no voice impersonation (R18), UTC-internal timestamps (R19), standardized run_id format (R20).
- **`docs/RUN_ID_SPEC.md`** — canonical run_id format `<agent>-<YYYYMMDD-HHMMSSZ>-<6char-hash>`. Bash + Python reference implementations. Bhishma R10 (≥3 example_run_ids) only works because this format is uniform.
- **`docs/SKILL_TEMPLATE.md`** — canonical `skill.md` structure so Sanjaya proposals diff against a known shape rather than freeform manuals.
- **`docs/BOOTSTRAP.md`** — bring-up order with promotion gates (Phase 0 → 1 → 2 → 3 → 4).
- **`docs/ARCHITECTURE.md`** — tier diagram, directory layout, data flows.
- **Confidence-scoring weights** in `bhishma.md` — formerly implicit, now explicit. Sanjaya and Vyasa read but do not modify (R9).
- **Per-agent improvements**, baked into each agent's `agent.md` and `skill.md`:

  | Agent     | Improvements added |
  |-----------|--------------------|
  | Sanjaya   | Quantitative drift metrics, loop-detection clause, recovery clause, change-log enforcement on applied diffs |
  | Vyasa     | Drift signals (5 named indicators), R14 self-check, loop-detection, recovery clause |
  | Sahadeva  | 4-week rolling calibration trend, agent-silence detection, bhishma hash cross-agent check, run_id format conformance, multi-week comparison |
  | Hanuman   | Per-source TTL cache layer, stale-data warning section, handle-resolution check, batch dedup |
  | Narada    | Voice-fingerprint extraction, generic-reject filter (cosine similarity ≤0.85 vs. last 30d), audience model line, length budget enforced before generation |
  | Arjuna    | Idempotency keys for destructive live calls, per-target circuit breakers (3 fails → 30min open), rate-limit awareness, rollback-plan field |
  | Nakula    | Log rotation (compress >24h, delete .gz >90d), weekly self-summary heartbeat, jobs.yml schema validator, single-writer enforcement on heartbeat.json |
  | Vidura    | T1–T5 source tiering, mandatory counter-evidence section, mandatory gaps section, tier_floor input |

- **Proposal templates** at `_meta/observer/templates/proposal.md.tmpl` and `_meta/conductor/templates/proposal.md.tmpl` so Sanjaya and Vyasa start from the same frontmatter shape.
- **`scripts/`** — `run_sanjaya.sh`, `run_vyasa.sh`, `run_sahadeva.sh`, `run_nakula.sh` (all with stale-lock cleanup, PID-based locking, and EXIT traps), plus `jobs.yml.example` and `crontab.example`.
- **`deploy.sh`** — one-shot installer that renames `dot-claude → .claude`, sets executable bits, creates the top-level `.md` symlinks, and copies into your target path.

## What was deliberately not added

- **Krishna (strategist).** You asked to skip for now. The role is currently played by Kartavya directly handing instructions to Arjuna. The architecture doc has a stub note in case you formalize it later.
- **Drona (trainer), Drupada (recruiter), etc.** Not needed for the current scope.
- **Hyperagent agent configs.** This is a Claude Code bundle (file-based agents under `.claude/agents/`). It is not designed to be imported as Hyperagent agents.

## Bhishma compliance notes

Every agent in this bundle:

- Declares a `tier` in its `agent.md` frontmatter (R13).
- Declares `write_scope` and `read_scope` in its frontmatter (supports R11 enforcement).
- References `bhishma.md` as the first read on every run.
- References `docs/RUN_ID_SPEC.md` for run_id format (R20).
- References `bhishma.md` for confidence weights rather than duplicating them (R9).

The constitution itself (`bhishma.md`) lives in `_meta/conductor/` because Vyasa is the agent most often consulting it during proposal review. It is read by everyone; written by no one but Kartavya (R1).

## Next steps after install

1. Read `docs/BOOTSTRAP.md` end-to-end.
2. Drop 2–3 sample Mayank-update messages into `~/projects/observer-test/.claude/agents/narada/voice-samples/` so Narada has voice calibration data.
3. Edit `~/projects/observer-test/.claude/agents/nakula/jobs.yml` (start from `scripts/jobs.yml.example`) to match your actual data sources.
4. Write the per-job scripts referenced in `jobs.yml` — these are bespoke to your stack (Kalodata MCP shape, Cruva endpoints, etc.).
5. Install the crontab from `scripts/crontab.example`.
6. Smoke-test each Tier-0 agent before bringing Sanjaya online.
