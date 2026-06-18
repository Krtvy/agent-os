# Proposed Constitutional Change — POC Workspaces for Yudhishthira

**Date proposed:** 2026-05-13
**Proposer:** Kartavya (via Claude Code session)
**Risk tier:** **constitutional** (per Bhishma R23 — touches `write_scope`, adds a new procedure, changes session-start routing logic)
**Status:** **PROPOSED — NOT APPLIED.** Awaits Sahadeva endorsement (first audit Sunday 2026-05-17 10:00 IST) + Kartavya commit per the override-discipline line drawn in `_audit/2026-05-12_yudhishthira-sheets-fluency.md`.

---

## Why this is a proposal, not a direct change

Three Claude-Code-mediated constitutional overrides have already happened (R23 itself, hook wiring, Yudhishthira Sheets-fluency upgrade). The audit chain explicitly flagged: "Three is the line — next constitutional change goes through the strict R23 proposal path." This is that fourth change. It goes through the proposal flow instead of becoming override #4.

The operational artifacts (folders, registers, training README) **have been built** — that's pure file-system work, not constitutional. What's pending: Yudhishthira's `agent.md` and `skill.md` updates that would make him formally POC-aware.

---

## What's already on disk (operational, no decision needed)

```
pocs/
├── README.md
├── vansh/
│   ├── register.md
│   ├── sheets/         (.gitkeep)
│   ├── raw/            (.gitkeep)
│   ├── exports/        (.gitkeep)
│   ├── deliverables/   (.gitkeep)
│   └── tasks/          (.gitkeep)
├── trupti/   (same shape)
└── shivangi/ (same shape)

training/
├── README.md
├── examples/    (.gitkeep)
├── patterns/    (.gitkeep)
└── glossary/    (.gitkeep)
```

All folders exist, all registers have the same template shape, training has its README. Yudhishthira **can already use them informally** today — the human just has to dispatch a task with "this is for Vansh" and point him at `pocs/vansh/`. What he doesn't have yet is the formal procedural binding.

---

## What this proposal would change in Yudhishthira's spec

### Change 1 — `agent.md` frontmatter `read_scope`

**Current:**

```yaml
read_scope:
  - ~/projects/observer-test/.claude/agents/_meta/conductor/bhishma.md
  - hyperagent://playbook/cmp1f7kpo105407adc5ijk8r9
  - hyperagent://memories/yudhishthira/*
  - user-uploaded CSV/XLSX
  - Google Sheets (read-only, phase 1)
```

**Proposed addition:**

```yaml
- ~/projects/observer-test/pocs/*/register.md
- ~/projects/observer-test/pocs/<active-poc>/sheets/
- ~/projects/observer-test/pocs/<active-poc>/raw/
- ~/projects/observer-test/pocs/<active-poc>/exports/
- ~/projects/observer-test/pocs/<active-poc>/tasks/
- ~/projects/observer-test/training/
```

Where `<active-poc>` is set per-task by the dispatcher. The wildcard read on `pocs/*/register.md` is intentional — Yudhishthira can read every POC's register to know who they are, but cannot read other POCs' data folders during a task scoped to one POC.

### Change 2 — `agent.md` frontmatter `write_scope`

**Current:**

```yaml
write_scope:
  - hyperagent://playbook/cmp1f7kpo105407adc5ijk8r9
  - hyperagent://memories/yudhishthira/*
  - hyperagent://files/yudhishthira/*
```

**Proposed addition:**

```yaml
- ~/projects/observer-test/pocs/<active-poc>/deliverables/
- ~/projects/observer-test/.claude/agents/yudhishthira/deliverables/  (legacy — for ad-hoc non-POC tasks)
```

Cross-POC writes are explicitly excluded. If Yudhishthira (or any agent he delegates to) attempts to write to `pocs/<other-poc>/`, `lib/bhishma-check.sh` blocks it.

### Change 3 — `skill.md` new procedure: P1.5 (POC routing)

Inserted between P1 (Session bootstrap) and P2 (INSPECT):

```markdown
### P1.5 — POC routing

If the dispatched task names a POC ("Vansh task", "for Trupti", etc.) or is implicit-by-data-source (a sheet that lives in `pocs/<name>/sheets/`):

1. **Identify the active POC.** If the dispatcher named one explicitly, use it. If they didn't, ask before proceeding — never guess from creator-name patterns alone.
2. **Read the POC register** at `pocs/<active-poc>/register.md`. State out loud in the audit `.md`:
   - The POC's identity from the register
   - The data sources listed
   - Whether the task lines up with the register's declared scope (flag if not)
3. **Lock in the active POC for this session.** All subsequent reads and writes are scoped to this POC's folder. Deliverable file names are prefixed `<poc-name>_`.
4. **If the task is cross-POC** (e.g., "compare Vansh's GMV vs Trupti's"), escalate before proceeding. Cross-POC analysis requires explicit Kartavya authorisation and an expanded read_scope for the duration of that task.

For tasks NOT scoped to a POC (ad-hoc, exploratory, or pre-POC-assignment): skip P1.5 and proceed to P2. The legacy `.claude/agents/yudhishthira/deliverables/` directory remains valid for those.
```

### Change 4 — `skill.md` P0 (Backup guardrail) — POC-aware copy semantics

P0's existing "always copy first" rule extends to POC sheets: any sheet from `pocs/<poc>/sheets/` is itself a local copy (placed there by `lib/yudhi-fetch.sh`, not the live Google Sheet). The discipline becomes: live Google Sheet → local copy in POC's `sheets/` → work happens against the copy. Two layers of always-copy.

### Change 5 — `skill.md` P7 (Deliver) — POC-aware output paths

Deliverable saves go to `pocs/<active-poc>/deliverables/<poc>_<task>_<YYYY-MM-DD>.csv` and `.md`. The file-naming prefix is enforced so cross-POC searches in the future find the right files cleanly.

### Change 6 — `skill.md` P8 (Learning capture) — training/ as third storage

When a pattern is reusable across POCs, P8 now has three storage targets to choose between:

- **POC-specific procedure:** append to `pocs/<active-poc>/register.md` (or a sub-doc within the POC's folder).
- **Yudhishthira-wide procedure:** append to `.claude/agents/yudhishthira/playbook.md` (or Hyperagent Playbook doc).
- **Training material reusable across POCs:** add to `training/patterns/<pattern-slug>.md` or `training/examples/...`.

Yudhishthira explicitly asks which scope when "remember this" is invoked — never silently assumes.

---

## What Sahadeva should verify before endorsing

When this proposal is reviewed during Sahadeva's first weekly audit:

1. **The folder structure on disk matches this proposal.** (Verifiable: walk `pocs/` and `training/` and confirm.)
2. **No POC folder has been written-to by an agent that shouldn't have.** Check git history for any writes into `pocs/<poc>/deliverables/` and confirm each was authored by a Yudhishthira run dispatched for that specific POC.
3. **No cross-POC writes have happened.** Same check, but specifically looking for writes to one POC's folder during a task scoped to another.
4. **The `lib/bhishma-check.sh` runtime gate is wired** (already done — see `_audit/2026-05-12_hooks-wired.md`) and would block a cross-POC write if attempted.
5. **The Yudhishthira `agent.md` updates correctly reflect Changes 1 + 2** (read_scope, write_scope additions) without unintended scope expansion.
6. **The `skill.md` procedural changes (P0, P1.5, P7, P8)** are coherent with the existing P3 UNDERSTAND step — the POC identity should appear in P3.2 as part of "the data we have."

## Failure modes to specifically watch for

1. **Cross-POC leakage.** Yudhishthira accidentally reading or writing into the wrong POC's folder. Mitigation: the runtime hook blocks it at the write level; the read side relies on the procedural discipline in P1.5 (which is auditable in the deliverable `.md`).
2. **POC ambiguity.** A task that touches both Vansh's and Trupti's creators arrives without explicit cross-POC authorisation. Mitigation: P1.5 step 4 forces escalation.
3. **Register staleness.** A POC's register lists data sources that no longer exist, or omits new ones. Mitigation: at each task's P3.2 step, Yudhishthira surfaces register-vs-actual mismatches.
4. **POC additions without proposal.** Adding a fourth POC (e.g., a new team member) is itself a constitutional change — adding a new sub-folder under `pocs/` and a register triggers an update to `read_scope` and `write_scope`. The strict R23 path applies. The `pocs/README.md` says this explicitly.

## Approval requirements per R23 (constitutional tier)

- ☐ Kartavya approval — to be given
- ☐ One-line rationale — "Per-POC workspaces let Yudhishthira scope data access by ownership, prevent cross-POC leakage, and create a clean home for raw exports + training material."
- ☐ Sahadeva endorsement — pending first audit Sunday 2026-05-17 10:00 IST
- ☐ 24-hour cooling-off — clock starts when this proposal is finalised; can complete after Sahadeva run

## What works today even without this proposal applied

The folder skeleton is real. Yudhishthira can be told "the data lives in `pocs/vansh/sheets/sheet-xyz.csv`, deliver to `pocs/vansh/deliverables/`" and he'll do it via Claude Code's existing tools. The procedural binding (P1.5, file-naming conventions, cross-POC escalation) is what's not yet enforced — but a human-dispatcher being explicit about scope is a fine substitute until Sahadeva endorses.

## Override count remains 3

This proposal explicitly does **not** apply itself. Override count stays at 3 (R23, hook wiring, Sheets-fluency upgrade with amendments). The line drawn last session is honoured.

---

_Proposal authored 2026-05-13 03:00 IST by Claude Code session (claude-opus-4-7) at Kartavya's explicit direction. To approve: Kartavya commits the changes to `agent.md` + `skill.md` manually after Sahadeva endorses Sunday._
