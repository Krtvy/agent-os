---
poc: Vansh
created: 2026-05-13
folder: pocs/vansh/
status: bootstrap # bootstrap | active | dormant
---

# Vansh — POC Register

> Source of truth for what Vansh owns, what data is available to Yudhishthira when working on a Vansh task, and the current task queue. Yudhishthira reads this file FIRST when a task names "Vansh."

## Identity

- **Name:** Vansh
- **Role:** Point of Contact at Rootlabs
- **Scope:** _(to be filled — which creators / campaigns / products fall under Vansh's ownership)_

## Creators in scope

_(populate from Creators Tagging tab or other authoritative source)_

| Username                | Product line | Status | Notes |
| ----------------------- | ------------ | ------ | ----- |
| _(none registered yet)_ |              |        |       |

## Data sources

### Google Sheets

_(Vansh's live working sheets — URL + sharing status. Yudhishthira fetches via `lib/yudhi-fetch.sh` into `sheets/`.)_

| Sheet name              | URL | Access | Last fetched |
| ----------------------- | --- | ------ | ------------ |
| _(none registered yet)_ |     |        |              |

### Raw exports

_(Files in `pocs/vansh/raw/` — populated by the human or via Hanuman scout reports. One row per file with: filename, source, date received.)_

| File                    | Source | Date received | Description |
| ----------------------- | ------ | ------------- | ----------- |
| _(none registered yet)_ |        |               |             |

### External system exports

_(Files in `pocs/vansh/exports/` — pulls from EUKA, Cruva, Kalodata, etc.)_

| File                    | System | Date | Notes |
| ----------------------- | ------ | ---- | ----- |
| _(none registered yet)_ |        |      |       |

## Active tasks

_(Briefs from Vansh — date, one-line task description, status, link to deliverable when complete.)_

| Date         | Task | Status | Deliverable |
| ------------ | ---- | ------ | ----------- |
| _(none yet)_ |      |        |             |

## Discipline (Yudhishthira's contract for Vansh tasks)

- **Reads:** `pocs/vansh/sheets/`, `pocs/vansh/raw/`, `pocs/vansh/exports/`, this register, the Bhishma constitution, the formula playbook, the shared `training/` directory.
- **Writes:** `pocs/vansh/deliverables/` only. No writes to other POCs' folders. No writes back to live Google Sheets (always-copy rule).
- **Task prefix:** when a Vansh task is dispatched, the deliverable file names start with `vansh_` so cross-POC searches are clean.
- **Cross-POC analysis:** if a task spans multiple POCs (e.g. compare Vansh's creators vs Trupti's), Yudhishthira asks for explicit authorisation and surfaces the wider scope in the audit `.md`.

## Change log

- 2026-05-13 — bootstrap — POC folder created. Empty register pending data from Kartavya.
