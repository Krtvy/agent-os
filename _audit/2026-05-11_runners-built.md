# Runners-Build Phase — 2026-05-11

> Sahadeva runner shipped, Sanjaya runner wired into the trace pipeline. The single highest-value next action ("trigger Sahadeva's first run") is now executable as `./run_sahadeva.sh`.

This phase substituted for the literal "Phase 4" parked items (G7 + G1B), which were genuinely premature (triggers had not fired). Kartavya picked **"Build Sahadeva's runner + wire traces"** via AskUserQuestion when asked what "next phase" should actually do.

---

## What shipped

### `_meta/audit/run_sahadeva.sh` (new) ✓

Sahadeva had no runner before this. The agent existed as `agent.md` + `skill.md` + `inbox.md` + `test-set/` but nothing knew how to invoke it. Built modelled on `_meta/observer/run_observer.sh`:

- **Lockfile guard** at `_meta/audit/.run.lock` — overlapping runs are always a bug (Sahadeva is weekly).
- **ISO-week computation** for the report filename (`reports/<YYYY-WW>.md`), matching the spec in `skill.md` P8.
- **Current-quarter test-set lookup** — `test-set/<YYYY-Qn>.md` (e.g. `2026-Q2.md`). If absent, run continues with a warning and the report omits the P10 detection-rate metric.
- **Claude CLI invocation** with `--agent sahadeva --permission-mode bypassPermissions`.
- **Env-var exports** (`BHISHMA_AGENT=sahadeva`, `BHISHMA_RUN_ID=<YYYY-MM-DD>-sahadeva-<HHMMSS>`) so the Phase 3 hooks pick up the run identity when eventually wired in.
- **Best-effort trace recording** — `lib/trace-writer.sh init` at start, `finalise` at end. Failure here logs but does not abort.
- **Cron entry documented in the header**: `30 4 * * 0` (Sunday 04:30 UTC / 10:00 IST), matching `skill.md` § Cadence.

### `_meta/observer/run_observer.sh` (modified) ✓

Sanjaya's runner already existed but had no trace integration. Added:

- **Run-ID generation** — `${DATE_UTC}-sanjaya-${HHMMSS_UTC}` (sortable, sequenceable, matches the trace-schema naming convention).
- **Env-var exports** — `BHISHMA_AGENT=sanjaya` and `BHISHMA_RUN_ID` so the PostToolUse hook (when wired in) can attribute events.
- **`trace-writer.sh init`** before the Claude invocation, **`finalise`** after with outcome tracking (`completed` / `errored`).
- **Best-effort discipline** — trace failures log to stderr; the run continues. Narrative journal remains the trust layer; trace is the audit layer.

The PostToolUse hook (`lib/post-tool-hook.sh`) is still not wired into `.claude/settings.json` per R23 constitutional cooling-off. The env-var exports are harmless until then — they're picked up only when the hook fires.

---

## What this unblocks

| Capability                                                           | Before                           | After                                                          |
| -------------------------------------------------------------------- | -------------------------------- | -------------------------------------------------------------- |
| "Trigger Sahadeva's first run"                                       | Blocked — no runner              | `./run_sahadeva.sh`                                            |
| Structured traces from Sanjaya runs                                  | None                             | Auto-emitted to `_meta/observer/traces/sanjaya/`               |
| Empirical signal for G7 trigger (journal size growth rate)           | Unknown — no measurement         | Trace finalise records per-run duration; growth can be derived |
| Empirical signal for G1B trigger (violations declarative rules miss) | Impossible — no Sahadeva reports | Possible after 3+ weekly Sahadeva runs                         |
| Test-set detection rate (P10)                                        | Theoretical                      | Real — every Sahadeva run reports it                           |

---

## Sanity-check results

| Check                                                  | Result                                      |
| ------------------------------------------------------ | ------------------------------------------- |
| `run_sahadeva.sh` syntax                               | ✓ `bash -n` clean                           |
| `run_sahadeva.sh` executable bit                       | ✓                                           |
| `run_observer.sh` syntax after edit                    | ✓ `bash -n` clean                           |
| `run_observer.sh` executable bit                       | ✓ (unchanged)                               |
| Both runners reference real `lib/trace-writer.sh` path | ✓                                           |
| Both runners include the lockfile guard                | ✓                                           |
| Both runners are robust to `trace-writer.sh` missing   | ✓ — falls back to "no trace, run continues" |
| Both runners export the same env-var pair              | ✓ `BHISHMA_AGENT` + `BHISHMA_RUN_ID`        |

No regressions to existing behaviour. `run_observer.sh` adds new code paths but preserves its existing invocation; if the trace-writer is missing or fails, the runner falls back to its prior behaviour.

---

## Overshoot scan

No unauthorised work. Phase scope was "build Sahadeva's runner + wire traces"; the two artifacts touched match exactly:

- `_meta/audit/run_sahadeva.sh` — new file, named in scope.
- `_meta/observer/run_observer.sh` — modified file, named in scope.

CHANGELOG updates + this audit file are required by the discipline established earlier in the session; not in-scope overshoot.

**Not done in this phase, by design:**

- **Wiring `bhishma-pretool-hook.sh` and `post-tool-hook.sh`** into `.claude/settings.json` — still constitutional per R23.
- **G7** (journal compaction) — trigger not fired; still parked.
- **G1B** (Haiku semantic validator) — trigger not fired; still parked.
- **Backfilling MAST codes** in existing journals — violates R5 (append-only); not done.
- **Re-exporting Vidura body to Hyperagent** — out of scope for runner work; remains on the watch-list.

---

## What's still needed before Sahadeva can run usefully

Kartavya can run `./run_sahadeva.sh` right now. It will:

1. Acquire the lockfile.
2. Compute the ISO week and check for the Q2 test set (it exists — Phase 2 G3 shipped it).
3. Initialise a trace at `_meta/observer/traces/sahadeva/<run_id>.json`.
4. Invoke Claude Code as the Sahadeva agent with the P1–P11 prompt.
5. Finalise the trace.
6. Drop the lockfile.

**What it will NOT do well on the first run:**

1. **P5 quantitative trend audit** will have nothing to compare to — there are no prior weeks of metrics. Sahadeva will produce a baseline row, not a delta. This is expected; the table becomes useful from week 2 forward.
2. **P10 test-set evaluation** depends on whether Sahadeva's runtime actually stages the 15 implanted-violation artifacts from the test set into the sandbox before running. The current runner does NOT do that staging — the test set is documented but not auto-injected. **First-run P10 will be a manual walk-through** (Sahadeva reads `test-set/2026-Q2.md` and checks each case against the real ecosystem, expecting most to be "not present, no violation detected, which is correct"). Automated injection is a future enhancement.
3. **P2 cross-agent hash audit** depends on agents recording the Bhishma hash they loaded. No agent currently does this in a structured way. Sahadeva's first report will note this as a configuration gap.

These are not blockers — they're things the first report will surface, which is itself the value of running.

---

## Watch-list updates

Carrying forward from `2026-05-11_post-phase-3-audit.md`, with updates:

| #   | Item                                                     | Status update                                                                   |
| --- | -------------------------------------------------------- | ------------------------------------------------------------------------------- |
| 1   | MAST FM-x.y code IDs unverified                          | Unchanged                                                                       |
| 2   | R23 attribution chain                                    | Unchanged                                                                       |
| 3   | `bhishma-pretool-hook.sh` not wired in                   | Unchanged                                                                       |
| 4   | Sahadeva has still never run                             | **Now runnable** — `./run_sahadeva.sh`                                          |
| 5   | Hyperagent drift (Vidura + Yudhishthira)                 | Unchanged                                                                       |
| 6   | Existing journals don't carry `mast_codes:`              | Unchanged                                                                       |
| 7   | `post-tool-hook.sh` not wired in                         | Unchanged                                                                       |
| 8   | No traces exist yet                                      | **About to change** — first Sanjaya OR Sahadeva run will create the first trace |
| 9   | `run_observer.sh` does not emit traces                   | **Resolved** — wired in this phase                                              |
| 10  | G7 trigger (journal >200 KB)                             | Unchanged                                                                       |
| 11  | G1B trigger (3 weeks Sahadeva + declarative-rule misses) | Unchanged                                                                       |

**New items added in this phase:**

| #   | Item                                                        | Why it matters                                                                                                                                                                                                                                                |
| --- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 12  | First-run P10 is manual, not auto-injected                  | `run_sahadeva.sh` does not stage test-set artifacts. Automated injection is the next-next enhancement; until then, Sahadeva reads the test set as a checklist against the real ecosystem (where most cases should NOT be present — that's the healthy state). |
| 13  | Cron not yet installed                                      | The runner has the cron entry in its header (`30 4 * * 0`) but no `crontab -e` was performed. Until that happens, Sahadeva runs only when manually triggered.                                                                                                 |
| 14  | P2 hash-recording discipline on Tier-0 agents not yet built | Sahadeva's P2 expects each agent to record the Bhishma hash loaded at session start. No agent currently does this in a machine-readable way. First Sahadeva report will surface this gap.                                                                     |

---

## Sign-off

| Phase                       | Status                                                             |
| --------------------------- | ------------------------------------------------------------------ |
| Phase 1 (G4 + G6 + G8 + G9) | ✅ Applied                                                         |
| Phase 2 (G1A + G2 + G3)     | ✅ Applied                                                         |
| Phase 3 — G5 + G1C          | ✅ Built (dormant, not wired)                                      |
| Phase 3 — G7                | ⏳ Parked (trigger: journal >200 KB)                               |
| Phase 4 — G1B               | ⏳ Parked (trigger: 3 weeks Sahadeva reports)                      |
| **Runners-build**           | ✅ This phase — Sahadeva runner shipped, Sanjaya trace wiring done |
| **Sahadeva's first run**    | ⏳ Kartavya's call                                                 |

The ecosystem is now **as ready as it can be without first-run feedback.** Any further structural work without running Sahadeva first is speculation.

---

_Runners-build phase recorded 2026-05-11 23:53 IST by Claude Code session (claude-opus-4-7). Session work ends here; next session should begin with whatever Sahadeva's first run reveals._
