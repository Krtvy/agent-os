# 🐎 Nakula — Automation Pipeline Owner

> Tier 0 · Mahabharat: Nakula, the disciplined twin

Automation/pipeline owner. Reads `jobs.yml`, runs scheduled jobs (Kalodata syncs, Cruva rollups, competitor refreshes), emits heartbeats, alerts on failures. Reliable and silent — failures are loud, successes are quiet.

## Capabilities

- Scheduled-job runner driven by `jobs.yml`.
- Lockfiles (`locks/`) prevent overlapping runs of the same job.
- Heartbeat emission to `logs/heartbeat.json` for Sanjaya / Sahadeva.
- Log rotation per job.
- Weekly self-summary report.
- Failure alerts via configured channels; successes stay silent.

## Files

| File / dir     | Purpose                              |
| -------------- | ------------------------------------ |
| `agent.md`     | Identity + system prompt             |
| `skill.md`     | Operational procedures               |
| `README.md`    | This file                            |
| `CHANGELOG.md` | Append-only agent-level history      |
| `scripts/`     | Job scripts referenced by `jobs.yml` |
| `locks/`       | Per-job lockfiles (auto-managed)     |

## Upstream / Downstream

- **Upstream:** kartavya (rare manual trigger), cron
- **Downstream:** per-job scripts, hanuman/cache (refresh trigger)

## Watched by

- Sanjaya at `_meta/observer/journal/nakula.md`

## See also

- `agent.md` — full identity and scope
- `skill.md` — job-runner procedures
- `jobs.yml` — scheduled-job manifest
