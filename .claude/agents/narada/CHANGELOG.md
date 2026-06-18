# Narada — Changelog

Append-only log of **agent-level** changes (identity, file structure, scope, tooling). Skill-level changes track in `skill.md` § "Change log".

## 2026-05-11

- Added `README.md` and `CHANGELOG.md` per agent-template standard.
- Acquired voice-pipeline subsystem (`voice-pipeline/`, 25-skill voice-replication pipeline, sourced from `aaddrick/written-voice-replication`, MIT). Pipeline outputs populate `voice-fingerprint.json` — never replace Narada's identity, modes, or forbidden-phrase lists.

## 2026-05-10

- Bootstrap — initial agent definition committed.
