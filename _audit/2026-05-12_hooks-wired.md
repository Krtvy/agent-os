# Hooks Wired Into Harness — 2026-05-12 00:05 IST

> Constitutional override #2. `lib/bhishma-pretool-hook.sh` and `lib/post-tool-hook.sh` are now active via `.claude/settings.json`. Sahadeva's first audit (Sunday 2026-05-17 10:00 IST) will assess whether the override pattern is becoming a habit.

---

## What got wired

A new `.claude/settings.json` file (the project-shared settings — `settings.local.json` was already present for permissions). Contents:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit|NotebookEdit",
        "hooks": [
          { "type": "command", "command": "lib/bhishma-pretool-hook.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [{ "type": "command", "command": "lib/post-tool-hook.sh" }]
      }
    ]
  }
}
```

Both scripts use the same opt-in env-var discipline:

- `$BHISHMA_AGENT` unset → hook exits 0 (Kartavya's interactive sessions are unaffected by design).
- `$BHISHMA_AGENT=<name>` + `$BHISHMA_RUN_ID=<id>` set → hook activates.

The agent runners (`run_observer.sh`, `run_sahadeva.sh`) export both env vars before invoking `claude`. So:

- Daily Sanjaya cron firing (`0 2 * * *`) — now gets write_scope enforcement on every Edit/Write tool call, plus structured trace recording.
- Weekly Sahadeva cron firing (`0 10 * * 0`) — same, with `BHISHMA_AGENT=sahadeva`.
- Kartavya's interactive sessions — unchanged.

## The constitutional override

R23 explicitly classifies wiring `.claude/settings.json` hooks as `constitutional` (it touches approval-gate logic — runtime enforcement of `write_scope`, which is referenced by Bhishma R3 and R11). The R23 approval path requires:

1. Kartavya approval — ✓ given at 2026-05-12 00:04 IST.
2. One-line rationale — "wire the hooks in" (Kartavya, verbatim).
3. **Sahadeva endorsement** — **not available.** Sahadeva has never run. First audit fires 2026-05-17.
4. 24-hour cooling-off window — bypassed under explicit auto-mode direction.

Conditions 3 and 4 were overridden. This is the second time Claude Code-mediated work has bypassed the strict R23 path:

1. **Override #1 (2026-05-11 ~22:50 IST):** R23 itself was added to `bhishma.md` under "Kartavya via Claude Code" attribution. Documented in `bhishma.md` § "Last reviewed" and in `_audit/2026-05-11_phase-1-applied.md`.
2. **Override #2 (this file):** Hook wiring documented here.

Two overrides in the first week is a pattern worth watching, not yet a habit worth changing. The honest framing: both were defensible bootstrap decisions made before the audit infrastructure existed to evaluate them. Going forward, the discipline should tighten — Sahadeva's first audit is the natural moment for that recalibration.

## What Sahadeva should specifically check on first run

R23 is now actually enforceable. Sahadeva should:

1. **Audit both Override #1 and Override #2 retroactively.** Verify the rationale, the attribution, and the scope. Confirm that no behavioural change crept in beyond what was authorised.
2. **Decide whether to ratify or roll back.** Possible outcomes:
   - **Ratify** — both overrides were sensible bootstrap moves; document them as "exception-with-justification" and move on.
   - **Soft rollback** — keep the artifact but require an explicit Sahadeva endorsement line in `bhishma.md` § Last reviewed and in this file's frontmatter.
   - **Hard rollback** — recommend reverting one or both changes via a proper R23 proposal flow. Kartavya decides.
3. **Set the pattern threshold.** If a third override happens before the rollback decision, flag as `severity: critical` in the inbox. Two is a coincidence; three is a habit.

## Verification

| Check                                             | Result                                                                               |
| ------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `.claude/settings.json` parses as valid JSON      | ✓ via `python3 -c "import json; json.load(open(...))"`                               |
| `lib/bhishma-pretool-hook.sh` exists + executable | ✓                                                                                    |
| `lib/post-tool-hook.sh` exists + executable       | ✓                                                                                    |
| Hook scripts no-op when `$BHISHMA_AGENT` unset    | ✓ tested 2026-05-11                                                                  |
| Hook scripts activate when env set                | ✓ tested 2026-05-11                                                                  |
| Existing `.claude/settings.local.json` preserved  | ✓ — separate file, untouched                                                         |
| Kartavya's current session still works            | ✓ — no `BHISHMA_AGENT`, hook no-ops; this audit file itself was written after wiring |

## Watch-list updates

Carrying forward from `2026-05-12_cron-scheduled.md`:

| #   | Item                                                        | Status                                              |
| --- | ----------------------------------------------------------- | --------------------------------------------------- |
| 3   | `bhishma-pretool-hook.sh` not wired in                      | **Resolved** — wired this commit                    |
| 7   | `post-tool-hook.sh` not wired in                            | **Resolved** — wired this commit                    |
| 12  | First-run P10 is manual (no test-set auto-injection)        | Unchanged — orthogonal to hooks                     |
| 14  | P2 hash-recording discipline on Tier-0 agents not yet built | Unchanged — Sahadeva will surface this on first run |

**New item added:**

| #   | Item                                                                  | Why it matters                                                                                                                                                                   |
| --- | --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 15  | Two constitutional overrides in first week (R23 itself + hook wiring) | If a third override happens before Sahadeva ratifies or rolls back these two, the pattern has shifted from bootstrap exception to habit. R23's whole purpose is preventing this. |

## Sign-off

| Phase                                                        | Status                               |
| ------------------------------------------------------------ | ------------------------------------ |
| Phase 1 / Phase 2 / Phase 3 / Runners-build / Cron-scheduled | ✅ All applied                       |
| **Hooks wired**                                              | ✅ This file                         |
| Phase 3 — G7                                                 | ⏳ Trigger: journal >200 KB          |
| Phase 4 — G1B                                                | ⏳ Trigger: 3 weeks Sahadeva reports |
| **First Sahadeva run**                                       | ⏳ Sunday 2026-05-17 10:00 IST       |

Everything that can be built without first-run feedback has now been built. The system is fully instrumented and ready. Sunday's audit is the moment of truth.

---

_Hooks wired 2026-05-12 00:05 IST by Claude Code session (claude-opus-4-7), at Kartavya's explicit auto-mode direction. R23 cooling-off + Sahadeva endorsement bypassed; documented here for retrospective audit on first Sahadeva firing._
