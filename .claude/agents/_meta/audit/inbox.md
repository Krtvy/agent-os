# Audit Inbox

Critical findings from Sahadeva, surfaced separately from the weekly report so they don't sit dormant.

Append-only. One line per finding, format:
`<ISO timestamp> · <severity> · <one-line finding> · ref: reports/<YYYY-WW>.md`

---

2026-05-17T04:37:00Z · critical · Heartbeat infrastructure absent — logs/heartbeat.json does not exist, Nakula has never run, no jobs.yml configured · ref: reports/2026-W20.md
2026-05-17T04:37:00Z · critical · Vyasa (Tier-1 conductor) completely dormant — zero journals, zero proposals, zero approvals since ecosystem creation · ref: reports/2026-W20.md
2026-05-22T09:48:00Z · resolved · Vyasa dormancy — deferred by decision; Kartavya is direct approver until Sanjaya calibration data exists. See \_meta/conductor/README.md "Deferral decision — 2026-05-22"
2026-05-22T10:55:00Z · resolved · Heartbeat infrastructure — jobs.yml + nakula-run.sh wrapper wired; crontab now invokes Nakula. First real-run heartbeat written 2026-05-22T10:33:49Z (sanjaya, exit 0). TC-15 will pass next audit.
