# Self-Audit — 2026-05-11

> Findings only. No files modified by this audit. Approval-gated fixes follow in a separate change set.

Scope: every agent under `.claude/agents/` (arjuna, hanuman, nakula, narada, yudhishthira, research-agent/vidura, \_meta/observer, \_meta/conductor, \_meta/audit). Focused on frontmatter consistency, cross-reference integrity, Bhishma adherence, identity coherence, and observability.

Pairs with `2026-05-11_multi-agent-playbook.md` (Deep Research deliverable, in flight) — the playbook supplies external best practices; this file is the internal baseline they'll be compared against.

---

## Summary

| Severity     | Count | Examples                                                                                                                                                                                                                                                                                                           |
| ------------ | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 🔴 Critical  | 1     | Yudhishthira does not reference Bhishma in `read_scope`                                                                                                                                                                                                                                                            |
| 🟠 Important | 6     | `tools` field shape varies; observer's `name:` field disagrees with body identity; research-agent + observer missing `effort`/`icon`/`upstream`/`downstream`/`read_scope`/`write_scope`; model field naming inconsistent                                                                                           |
| 🟡 Cosmetic  | 4     | Yudhishthira frontmatter heavier than others (legitimate divergence — Hyperagent); research-agent body uses Hyperagent-platform format instead of Mahabharat "# Name — Tier-N Role" shape; Vidura alias is documented but the body still calls it "Research Agent"; `mcps` field present on some, absent on others |

Total fixes proposed: 11. Net risk: low. Total estimated work: ~45 min once approved.

---

## 🔴 Critical

### C1. Yudhishthira does not reference Bhishma

**Evidence.** Yudhishthira's `read_scope` lists `hyperagent://playbook/...`, `hyperagent://memories/...`, user uploads, and Google Sheets — but NOT `_meta/conductor/bhishma.md`. Every other Tier-0 agent (arjuna, hanuman, nakula, narada) reads Bhishma at session start.

**Why it matters.** Bhishma is the constitution. R1 forbids any agent from editing it; R2 forbids self-modification; R8 forbids cross-tier invocation. An agent that doesn't load Bhishma can violate these rules without knowing it has. This is the single most load-bearing rule in the system, and Yudhishthira currently has no obligation to it in declaration.

**Fix.** Add `bhishma.md` to Yudhishthira's `read_scope` (both in `agent.md` frontmatter and in `skill.md` § P1 session bootstrap). Since Yudhishthira runs on Hyperagent, mirror Bhishma into the Hyperagent file space so it can be read via `FetchStoredFile`, OR add a session-start step that reads it via the GitHub integration.

**Blast radius.** None (Yudhishthira has not run yet; no proposals exist).

---

## 🟠 Important

### I1. `tools` frontmatter shape varies

**Evidence.**

- List form `tools: [Read, Write, ...]` — arjuna, hanuman, nakula, narada, vyasa, sahadeva, yudhishthira (as `tools_hyperagent`)
- Scalar/CSV form `tools: Read, Write, ...` — research-agent, observer

**Why it matters.** YAML parses these differently. A scalar value is a string; a list value is a list of strings. Downstream tools (Sahadeva's audit script, Sanjaya's journal renderer) that read frontmatter via PyYAML or similar will hit type errors on whichever shape they don't expect.

**Fix.** Standardize on list form `tools: [Read, Write, ...]`. Update research-agent and observer.

### I2. Observer's `name:` field disagrees with body identity

**Evidence.** `_meta/observer/agent.md` frontmatter says `name: observer`. The agent's mythological name is **Sanjaya** — every other agent's body refers to it as Sanjaya, both symlinks (`observer.md` and `sanjaya.md`) point here, Bhishma R-rules name "Sanjaya" specifically.

**Why it matters.** Two-name ambiguity. A grep for `name: sanjaya` returns zero hits even though Sanjaya is everywhere in prose. Sahadeva's audit logic that joins frontmatter `name` to journal directory paths breaks if it expects `sanjaya`.

**Fix.** Update frontmatter to `name: sanjaya`. Keep symlinks both ways for human convenience. Update README accordingly.

### I3. research-agent and observer missing standard frontmatter keys

**Evidence.**

| Agent                  | icon | effort | upstream | downstream | read_scope | write_scope |
| ---------------------- | ---- | ------ | -------- | ---------- | ---------- | ----------- |
| arjuna                 | ✓    | ✓      | ✓        | ✓          | ✓          | ✓           |
| hanuman                | ✓    | ✓      | ✓        | ✓          | ✓          | ✓           |
| nakula                 | ✓    | ✓      | ✓        | ✓          | ✓          | ✓           |
| narada                 | ✓    | ✓      | ✓        | ✓          | ✓          | ✓           |
| yudhishthira           | ✓    | ✓      | ✓        | ✓          | ✓          | ✓           |
| **research-agent**     | ✗    | ✗      | ✗        | ✗          | ✗          | ✗           |
| **observer (sanjaya)** | ✗    | ✗      | ✗        | ✗          | ✗          | ✗           |
| vyasa                  | ✓    | ✓      | ✓        | ✓          | ✓          | ✓           |
| sahadeva               | ✓    | ✓      | ✓        | ✓          | ✓          | ✓           |

**Why it matters.** Frontmatter is the structured contract Sahadeva audits against. Missing keys means missing audit surface — Sahadeva can't check "does research-agent's write-scope match what it actually wrote this week?" if write_scope is undeclared.

**Fix.** Add the missing keys to research-agent and observer (sanjaya). For research-agent: scope is declared in body text, just lift it into frontmatter. For observer: body declares "may READ / may WRITE" explicitly — same lift.

### I4. `model` field naming inconsistent

**Evidence.**

- Full ID: `claude-sonnet-4-6` (arjuna, hanuman, narada, yudhishthira), `claude-haiku-4-5` (nakula), `claude-opus-4-6` (vyasa, sahadeva)
- Short form: `sonnet` (research-agent, observer)

**Why it matters.** Same downstream-parsing problem as I1. If something reads `model` and expects a full ID, "sonnet" is undefined — which Sonnet? 4.6? 4.5? Defaults are dangerous for a system that's supposed to be auditable.

**Fix.** Standardize on full model IDs. research-agent should be `claude-opus-4-6` per its own body ("Model: claude-opus-4-6"). Observer should be set explicitly — likely `claude-sonnet-4-6` based on its workload.

### I5. Yudhishthira's `read_scope` is Hyperagent-URI-shaped, not filesystem-path-shaped

**Evidence.** Yudhishthira's read_scope uses `hyperagent://playbook/cmp1f7kpo105407adc5ijk8r9` and `hyperagent://memories/yudhishthira/*`. Every other agent uses `~/projects/observer-test/...` filesystem paths.

**Why it matters.** Sanjaya's auditing scripts (and Sahadeva's) probably expect filesystem paths. Hyperagent URIs won't resolve. But the divergence is _legitimate_ — Yudhishthira genuinely doesn't have a filesystem footprint at runtime.

**Fix (two options).**

- **(a) Accept the divergence.** Add a `runtime: hyperagent` field that signals "filesystem scope rules don't apply." Update Sahadeva's audit to handle both.
- **(b) Mirror Hyperagent artifacts back to filesystem.** Pipe the Playbook + memories back to `.claude/agents/yudhishthira/state/` so the audit chain works uniformly.

Recommend (a) for now; revisit if Hyperagent agents proliferate.

### I6. research-agent body uses Hyperagent-export format instead of Mahabharat shape

**Evidence.** research-agent's `agent.md` opens with `# Research Agent — Agent Configuration` and dumps `## Identity`, `## System Prompt`, `## Tools Enabled` table — the format Hyperagent generates when you export an agent. Every other agent opens with `# <Name> — Tier-N <Role>` and a `## Your character` section grounding it in Mahabharat.

**Why it matters.** Two issues compound: (a) the file is a Hyperagent dump, not a curated agent doc, so updates require re-exporting rather than editing; (b) Vidura's character is only mentioned in passing ("also addressed as 'vidura' via symlink") rather than embraced like Arjuna/Hanuman/Yudhishthira embrace theirs. The Mahabharat theme is the system's coherence layer — research-agent breaks it.

**Fix.** Rewrite research-agent's `agent.md` in the Mahabharat shape:

- Title `# Vidura — Tier-0 Researcher`
- `## Your character` section: Vidura the wise counselor, source-disciplined, tells truth to power, never flatters.
- Move the Hyperagent export contents into an appendix or a separate `hyperagent-export.md`.
- Keep the actual system-prompt content intact — only the framing changes.

---

## 🟡 Cosmetic

### Co1. Yudhishthira frontmatter has more keys than others (legitimate)

`platform: hyperagent`, `playbook_doc_id`, `tools_hyperagent`, `disabled_tools`, `integrations`, `learning`, `phase`, `phase_notes` — these are Hyperagent-specific. Either accept the divergence (recommended — research-agent should grow these same keys) or strip them. **Leave as-is** and consider adopting some of them for research-agent in fix I6.

### Co2. `mcps` field present on some, absent on others

Arjuna and Hanuman declare `mcps: [...]`. Others don't. Either every agent declares the field (empty list if none) or none do. **Recommend** standardizing on "declare it always; empty list `mcps: []` means none."

### Co3. Yudhishthira's `tools_hyperagent` field name vs `tools`

The Hyperagent agent uses `tools_hyperagent` because the Claude Code `tools` field has different semantics. Cleaner: `tools: [...]` for the runtime that actually applies, plus a `runtime: hyperagent` discriminator.

### Co4. Sahadeva's `read_scope` is too broad

`read_scope: ~/projects/observer-test/ # everything, read-only` is a valid choice (Sahadeva audits the whole ecosystem) but it's the only agent with a wildcard scope. Worth a Bhishma comment that wildcards are reserved for the audit tier.

---

## What's GOOD (don't touch)

- **Bhishma constitution is solid.** 201 lines, 17+ rules, well-rationalized. Every Tier-0 agent except Yudhishthira already reads it.
- **Symlinks all resolve.** Every short-name (`arjuna.md`, `vidura.md`, etc.) points to a real `agent.md`.
- **The tier hierarchy is internally consistent.** Tier 0 → Sanjaya (1) → Vyasa (2) ← Sahadeva (Audit) sideways. The supervisory invariants match Bhishma R3 and R8.
- **README + CHANGELOG template now uniform** across all 9 agents (just shipped this session).
- **Sanjaya is journaling.** 5 agents have non-trivial journals (research-agent has 49 KB after 13 runs). Bootstrap mode active, no thresholds crossed yet — exactly the expected state.
- **The Mahabharat theme works.** Each character's archetype reinforces their agent role (Arjuna = single-minded execution, Hanuman = scout, Sahadeva = silent astrologer, etc.). Vidura is the one weak link (see I6).

---

## Proposed fix order (impact-to-effort)

| Rank | Fix                                                                        | Estimated time | Risk                                                                   |
| ---- | -------------------------------------------------------------------------- | -------------- | ---------------------------------------------------------------------- |
| 1    | **C1** — Add Bhishma to Yudhishthira's read_scope + P1                     | 5 min          | none                                                                   |
| 2    | **I2** — Rename observer's `name:` to `sanjaya`                            | 5 min          | low                                                                    |
| 3    | **I1** — Standardize `tools:` to list form everywhere                      | 10 min         | none                                                                   |
| 4    | **I4** — Standardize `model:` to full IDs                                  | 5 min          | none                                                                   |
| 5    | **I3** — Backfill missing frontmatter on research-agent + observer         | 15 min         | none                                                                   |
| 6    | **I6** — Rewrite research-agent's `agent.md` in Mahabharat shape as Vidura | 30 min         | medium (changes system prompt framing — re-deploy to Hyperagent after) |
| 7    | **I5** — Add `runtime:` discriminator field, update Sahadeva audit         | 10 min         | low                                                                    |
| 8    | **Co1–Co4** — Cosmetic field consistency                                   | 15 min         | none                                                                   |

**Recommendation:** Approve 1–5 as a batch (45 min, low risk, no behavior change). Defer 6 until the Deep Research playbook returns — it may suggest a different framing for the rewrite. Defer 7–8 until Sahadeva's first run reveals which keys it actually consumes.

---

## What this audit deliberately did NOT check

- **Does each agent's `skill.md` match its `agent.md` description?** Important but takes longer; defer to Sahadeva's first run.
- **Are there missing capabilities?** Deferred to the Deep Research playbook gap analysis.
- **Are confidence weights well-calibrated?** Bhishma R9 puts these out of agent scope; only Kartavya tunes.
- **Are journals factual?** Defer to Sahadeva.

---

_Audit generated 2026-05-11 22:42 IST. Author: Claude Code session (claude-opus-4-7). Reviewed by: pending Kartavya._
