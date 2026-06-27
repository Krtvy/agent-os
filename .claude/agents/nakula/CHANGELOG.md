# Nakula — Changelog

Append-only log of **agent-level** changes (identity, file structure, scope, tooling). Skill-level changes track in `skill.md` § "Change log".

## 2026-05-11

- Added `README.md` and `CHANGELOG.md` per agent-template standard. No identity or scope changes.

## 2026-05-10

- Bootstrap — initial agent definition committed.

## 2026-06-17
- Approved proposal 20260528-nakula-adaptation-skills: annotated K8 weekly-summary branch as unimplemented. Root cause: cron fires at 20:30 UTC, K8 needs 23:55 UTC — separate jobs.yml entry required.
- Repurposed example jobs in agent.md from Kalodata/Cruva → ai-knowledge-weekly-digest, github-trending-daily, job-market-weekly-scan.
