# Sahadeva Cron Scheduled — 2026-05-12

> First weekly audit fires **Sunday 2026-05-17 at 10:00 IST**. The latent investment from Phases 1–3 + the runners-build phase converts at that moment.

---

## What was installed

```
0 10 * * 0 cd /Users/mosaic/projects/observer-test && .claude/agents/_meta/audit/run_sahadeva.sh >> .claude/agents/_meta/audit/run.log 2>&1
```

- Host: this Mac, TZ `Asia/Kolkata` (IST).
- Cron uses host TZ, so `0 10 * * 0` = Sunday 10:00 IST (= Sunday 04:30 UTC).
- Cadence: every Sunday, indefinitely, until removed via `crontab -e`.
- Output: stdout + stderr appended to `.claude/agents/_meta/audit/run.log`.

The existing observer (Sanjaya) cron entry is preserved:

```
0 2 * * * cd /Users/mosaic/projects/observer-test && .claude/agents/_meta/observer/run_observer.sh >> .claude/agents/_meta/observer/run.log 2>&1
```

— so Sanjaya continues to run daily at 02:00 IST, journalling each watched agent's previous-24h activity.

## What I got wrong before getting it right

The runner's header had a cron-entry example reading `30 4 * * 0` (Sunday 04:30 UTC). That entry is **only correct on a UTC-local host**. This host runs IST. Cron uses the host's TZ — not UTC by default — so `30 4 * * 0` on an IST system fires at 04:30 IST (which is 23:00 UTC the previous day), not the intended 10:00 IST.

The cron install pass got the time fields right (`0 10 * * 0`) but I dropped the `cd /Users/mosaic/projects/observer-test &&` prefix four times in a row in my shell typing — once because I echoed the same broken string twice, twice more from inattention even after announcing the fix, and finally got it right by writing the line to a file via Write and `cat`-ing into `crontab -`. The broken entries never had the chance to fire because each was overwritten by the next attempt, but the typing failure was real and worth recording so the failure mode is visible to Sahadeva on first run.

Runner header now shows both IST and UTC forms with the note "pick by `date +%Z`."

## Watch-list updates

Carrying forward from `2026-05-11_runners-built.md`, with the cron-scheduling item resolved:

| #   | Item                   | Status                                                                                         |
| --- | ---------------------- | ---------------------------------------------------------------------------------------------- |
| 13  | Cron not yet installed | **Resolved** — `0 10 * * 0` installed for Sahadeva, alongside existing `0 2 * * *` for Sanjaya |

All other watch-list items unchanged.

## What happens at 10:00 IST on 2026-05-17

If everything works:

1. Cron fires `.claude/agents/_meta/audit/run_sahadeva.sh`.
2. The runner acquires `_meta/audit/.run.lock`.
3. Generates a run_id `2026-05-17-sahadeva-043000` (give or take a few seconds).
4. Initialises a trace at `_meta/observer/traces/sahadeva/2026-05-17-sahadeva-043000.json`.
5. Looks for `_meta/audit/test-set/2026-Q2.md` (present — Phase 2 G3 shipped it).
6. Invokes Claude Code with `--agent sahadeva --permission-mode bypassPermissions`, telling Sahadeva to run P1–P11 against the audit-week ending 2026-05-17 UTC.
7. Sahadeva writes its report to `_meta/audit/reports/2026-W20.md`.
8. Critical findings (if any) get appended to `_meta/audit/inbox.md`.
9. Trace is finalised, lockfile is dropped.
10. Console output goes to `_meta/audit/run.log`.

If something breaks, the run.log captures stderr — `tail -50 _meta/audit/run.log` after the firing is the first thing to check.

## What the first report will probably look like

Honest expectations from `2026-05-11_runners-built.md`:

- **P3 R23 compliance**: clean (no proposals exist yet — `_meta/observer/proposals/` is empty).
- **P4 Bhishma compliance**: probably clean. No agents have run with the new Bhishma R23 loaded yet (Sanjaya last ran 2026-05-11 02:05, before R23 was added). Sahadeva might flag a hash mismatch — that's correct behaviour.
- **P5 quantitative trends**: baseline-only (no prior weeks). Useful from week 2.
- **P10 test-set**: manual walk-through against the 15 cases. Most should be "not present in live ecosystem, no false-positive detection" = healthy.
- **P11 metric snapshot**: emptyish table (just the baselines).
- **Sanjaya hash audit**: will surface that no agent currently records the Bhishma hash they loaded — this is a known configuration gap (watch-list item #14), and Sahadeva flagging it is the _point_.

Most likely overall verdict: **amber** (some configuration gaps, no actual violations).

The value is in surfacing the gaps, not in finding violations. Both are signal.

## What Kartavya should do between now and Sunday

Nothing required. Optionally:

- Verify the cron entry survived by running `crontab -l` tomorrow.
- Consider whether to wire `bhishma-pretool-hook.sh` and `post-tool-hook.sh` into `.claude/settings.json` _before_ the Sunday firing. Doing so would give Sahadeva real `logs/bhishma-blocks.log` data on P4 and real traces on P5. Trade-off: it's a constitutional change per R23, so strictly the cooling-off+endorsement should come _from_ Sahadeva, not _before_ it runs. Pick one.
- Re-export Vidura's body to Hyperagent (watch-list #5) so the runtime copy matches the local source-of-truth.

## Sign-off

| Phase              | Status                                                    |
| ------------------ | --------------------------------------------------------- |
| Phase 1            | ✅ Applied 2026-05-11                                     |
| Phase 2            | ✅ Applied 2026-05-11                                     |
| Phase 3 — G5 + G1C | ✅ Built dormant 2026-05-11                               |
| Runners-build      | ✅ Applied 2026-05-11                                     |
| **Cron scheduled** | ✅ This file — Sahadeva fires Sunday 2026-05-17 10:00 IST |
| Phase 3 — G7       | ⏳ Trigger: journal >200 KB                               |
| Phase 4 — G1B      | ⏳ Trigger: 3 weeks Sahadeva reports                      |

The next real signal in the system arrives at 10:00 IST on Sunday. Until then, the ecosystem is quiet.

---

_Cron scheduled 2026-05-12 00:02 IST by Claude Code session (claude-opus-4-7), preserving the existing Sanjaya entry. Verified via `crontab -l` after install._
