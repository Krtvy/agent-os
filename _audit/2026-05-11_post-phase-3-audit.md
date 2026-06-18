# Closing Audit — Post-Phase-3 — 2026-05-11

> Sign-off after Phase 3 (scoped — G5 schema + writer, G1C post-tool hook; G7 and G1B explicitly skipped with reasoning). Companion to `2026-05-11_post-phase-2-audit.md`.

Pairs with: all earlier `_audit/` files for the day. This is the final closing audit of the session.

---

## Phase 3 scope decision

The closing audit at end-of-Phase-2 recommended waiting for Sahadeva's first weekly report before building Phase 3 trace infrastructure. Kartavya replied "continue", overriding that recommendation. The honest middle path applied this session:

- **Build the foundations** (schema, writer, hook) so they exist and are tested.
- **Do not wire them in** — wiring is constitutional per R23 and requires Sahadeva endorsement + cooling-off.
- **Skip pre-emptive work** (G7 compaction, G1B semantic validator) where the trigger genuinely hasn't fired.

This trades "everything's plumbed and live" for "everything's plumbed and dormant." When the first Sahadeva run lands, wiring is a one-paragraph edit to `.claude/settings.json` rather than a one-day build.

---

## What shipped in Phase 3

### G5 — Trace schema + writer ✓

- `lib/trace-schema.md` (v1, ~280 lines). JSON schema for run-level traces with fields for run metadata, tool calls, decision points, MAST codes, Bhishma blocks, token/cost totals, final outcome. Field sanitisation rules explicit ("trace is for shape, not substance"). Consumers enumerated against Sahadeva's P2/P3/P4/P5/P7/P10 procedures.
- `lib/trace-writer.sh` (~280 lines). Five subcommands — `init`, `tool-call`, `bhishma-block`, `decision`, `finalise`. In-process Python `fcntl.LOCK_EX` for cross-platform locking (macOS doesn't have the `flock` binary; the first cut hit this and was rewritten). Trace files land at `.claude/agents/_meta/observer/traces/<agent>/<run_id>.json`. Smoke-tested with all five subcommands.

### G1C — Post-tool hook ✓

- `lib/post-tool-hook.sh` (~85 lines). Reads tool-result JSON from Claude Code stdin, sanitises (drops full payloads, credentials, PII), writes a tool-call event via `trace-writer.sh`. Same opt-in env-var discipline as `bhishma-pretool-hook.sh`: requires both `$BHISHMA_AGENT` and `$BHISHMA_RUN_ID` to be set.
- Uses `set -uo pipefail` (deliberately not `-e`) — trace failures must never bubble back to Claude Code and interrupt the agent's primary work. Trace is best-effort by design.
- Smoke-tested: no-op when env unset; records event correctly when env set.

### G7 — Skipped, reasoned ✓

Documented in `lib/README.md` § "Phase 3 deliberate skips." The largest existing journal (`research-agent.md`) is 49 KB; the playbook recommends compaction around 200 KB; extrapolating, the trigger is ~3 months away. Watch-list item.

### G1B — Skipped, reasoned ✓

Documented in `lib/README.md` § "Phase 3 deliberate skips." Conditional on Phase 2-3 signal warranting it. Until G1A + G1C are wired in and Sahadeva has produced 3 weeks of reports showing recurring violations that declarative rules cannot catch, the semantic validator is over-engineering against a hypothetical.

---

## Sanity-check results

| Check                                                               | Result              | Notes                                                                                                                                           |
| ------------------------------------------------------------------- | ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `lib/` script inventory                                             | ✓                   | 4 executables (`bhishma-check.sh`, `bhishma-pretool-hook.sh`, `post-tool-hook.sh`, `trace-writer.sh`) + 2 docs (`README.md`, `trace-schema.md`) |
| `lib/trace-writer.sh` smoke test                                    | ✓                   | All five subcommands; trace JSON conforms to v1 schema; tokens_total accumulates correctly                                                      |
| `lib/post-tool-hook.sh` smoke test                                  | ✓                   | No-op when `$BHISHMA_AGENT` unset; records event when set                                                                                       |
| Trace storage directory                                             | ⏳ lazy-created     | `.claude/agents/_meta/observer/traces/` does not yet exist; `trace-writer.sh init` creates it on demand                                         |
| Hook wiring in `.claude/settings.json`                              | ⏳ deliberate-defer | `bhishma-pretool-hook.sh` and `post-tool-hook.sh` both unwired per R23 cooling-off                                                              |
| Sanjaya CHANGELOG records Phase 3                                   | ✓                   | Added entries for G5 + G1C + skip-reasoning                                                                                                     |
| `_audit/README.md` file index includes this audit                   | ✓                   | Added row for `2026-05-11_post-phase-3-audit.md`                                                                                                |
| `_audit/README.md` related-artifacts table includes Phase 3 scripts | ✓                   | Added rows for `trace-schema.md` + `trace-writer.sh` + `post-tool-hook.sh`                                                                      |
| Test artifacts cleaned up                                           | ✓                   | `traces/sanjaya/test-*.json` and `traces/smoke/*` removed after smoke tests                                                                     |

## Regression scan

No regressions detected. Phase 3 work is purely additive — new files in `lib/`, no edits to existing agent code paths beyond the documentation in CHANGELOG and `_audit/README.md`. The only behaviour change that could occur from Phase 3 is wiring the hooks into `.claude/settings.json`, which was deliberately not done.

Specifically checked:

- All 11 agent symlinks still resolve.
- `bhishma-check.sh` still passes the same 4 test scenarios from Phase 2.
- No edits made to `bhishma.md`, agent `agent.md`s, or `skill.md`s during Phase 3.

## Overshoot scan

Walked every artifact created in Phase 3 against the gap-analysis scope:

| Artifact                   | Mapped to                     | Justified? |
| -------------------------- | ----------------------------- | ---------- |
| `trace-schema.md`          | G5                            | ✓          |
| `trace-writer.sh`          | G5                            | ✓          |
| `post-tool-hook.sh`        | G1C                           | ✓          |
| `lib/README.md` additions  | G5 + G1C + skip docs          | ✓          |
| Sanjaya CHANGELOG entries  | Required by template standard | ✓          |
| `_audit/README.md` updates | File index discipline         | ✓          |
| This audit file            | Closing-audit discipline      | ✓          |

No unauthorised work. No premature optimisation (G7 and G1B explicitly skipped with reasoning). No dead code (every script tested before commit).

The closest call: **trace-schema.md is ~280 lines.** Is it too detailed for a v1 schema that's not wired in yet? Honest answer: yes, slightly — the consumer table mapping to Sahadeva's P2/P3/P4/P5/P7/P10 could have been a one-liner pointer to `sahadeva/skill.md` instead of being expanded inline. The redundancy is mild and self-correcting (if Sahadeva's skill.md procedures change, the redundancy will get noticed during the next audit). Leaving as-is.

---

## Watch-list (carries forward from Phase 2 + adds Phase 3 items)

### Continuing from Phase 2

1. MAST FM-x.y code IDs unverified against Cemri et al. — fix on first proposal cite.
2. R23 attribution via Claude Code is a one-time exception; future Bhishma edits should be Kartavya-committed manually.
3. `bhishma-pretool-hook.sh` not wired in.
4. **Sahadeva has still never run** — single highest-value next action.
5. Hyperagent drift for Vidura + Yudhishthira — re-export when convenient.
6. Sanjaya's existing journals don't carry `mast_codes:` (by design — R5).

### New from Phase 3

7. **`post-tool-hook.sh` not wired in.** Same reasoning as G1A — wiring is constitutional per R23 cooling-off. The hook is opt-in via env vars and is dormant until both `.claude/settings.json` wires it and a runner sets `$BHISHMA_AGENT` + `$BHISHMA_RUN_ID`.
8. **No traces exist yet.** `.claude/agents/_meta/observer/traces/` directory is uncreated. Sahadeva's P5/P10 procedures handle empty inputs gracefully (documented in `sahadeva/skill.md`), but the value of Phase 3 is unrealised until at least one trace lands.
9. **`run_observer.sh` does not yet emit traces.** When wiring lands, Sanjaya's runner needs an `init` call at run-start and a `finalise` call at run-end, plus env-var exports for the hooks. This is the smallest concrete step to make traces real.
10. **G7 trigger is ~200 KB journal size.** Currently 49 KB max. Re-check at end-of-Q2.
11. **G1B trigger is "3 weeks of Sahadeva reports showing recurring violations declarative rules can't catch."** Implies Sahadeva must run weekly for 3+ weeks first. Don't revisit until then.

---

## Sign-off

| Phase                       | Status               | Notes                                                                           |
| --------------------------- | -------------------- | ------------------------------------------------------------------------------- |
| Phase 1 (G4 + G6 + G8 + G9) | ✅ Applied           | Recorded in `_audit/2026-05-11_phase-1-applied.md`                              |
| Phase 2 (G1A + G2 + G3)     | ✅ Applied           | Recorded in `_audit/2026-05-11_post-phase-2-audit.md`                           |
| Phase 3 — G5 + G1C          | ✅ Built (not wired) | This file                                                                       |
| Phase 3 — G7                | ⏳ Parked            | Trigger: any journal >200 KB                                                    |
| Phase 4 — G1B               | ⏳ Parked            | Trigger: 3 weeks Sahadeva reports + recurring violations declarative rules miss |
| Closing audit               | ✅ This file         | No regressions, no overshoot, 11 watch-list items recorded                      |

## Lifetime stats for the session (informational)

Files created:

- 10 in Phase 1 (`_audit/README.md`, Bhishma R23 addition, MAST skill, body reframes, CHANGELOG updates).
- 11 in Phase 2 (`lib/bhishma-check.sh`, `lib/bhishma-pretool-hook.sh`, `lib/README.md`, Sahadeva skill rewrite, Q2 test set, vyasa + sahadeva body R-rule fixes, CHANGELOG updates, post-phase-2 audit).
- 5 in Phase 3 (`lib/trace-schema.md`, `lib/trace-writer.sh`, `lib/post-tool-hook.sh`, `lib/README.md` additions, this audit file).

Total: ~26 files touched. Bhishma rules added: 1 (R23). Skill manuals rewritten: 1 (Sahadeva). Body reframes: 2 (Vidura, Sanjaya). Adversarial test cases pre-registered: 15. Runtime enforcement scripts shipped: 4.

System now in a **stable instrumented dormant state** — every layer of the playbook's defense-in-depth recommendation has a corresponding artifact, and none of the new artifacts have been activated. Activation is gated on Sahadeva's first run, which is Kartavya's call.

---

_Closing audit recorded 2026-05-11 23:46 IST by Claude Code session (claude-opus-4-7). Session ends here unless extended; the ecosystem is ready for Sahadeva's first cron firing._
