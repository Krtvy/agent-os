---
poc: Trupti
created: 2026-05-13
folder: pocs/trupti/
status: bootstrap # bootstrap | active | dormant
---

# Trupti — POC Register

> Source of truth for what Trupti owns, what data is available to Yudhishthira when working on a Trupti task, and the current task queue. Yudhishthira reads this file FIRST when a task names "Trupti."

## Identity

- **Name:** Trupti
- **Role:** Point of Contact at Rootlabs
- **Scope:** _(to be filled — which creators / campaigns / products fall under Trupti's ownership)_

## Creators in scope

_(populate from Creators Tagging tab or other authoritative source)_

| Username                | Product line | Status | Notes |
| ----------------------- | ------------ | ------ | ----- |
| _(none registered yet)_ |              |        |       |

## Data sources

### Google Sheets

_(Trupti's live working sheets — URL + sharing status. Yudhishthira fetches via `lib/yudhi-fetch.sh` into `sheets/`.)_

| Sheet name              | URL | Access | Last fetched |
| ----------------------- | --- | ------ | ------------ |
| _(none registered yet)_ |     |        |              |

### Raw exports

_(Files in `pocs/trupti/raw/` — populated by the human or via Hanuman scout reports. One row per file with: filename, source, date received.)_

| File                    | Source | Date received | Description |
| ----------------------- | ------ | ------------- | ----------- |
| _(none registered yet)_ |        |               |             |

### External system exports

_(Files in `pocs/trupti/exports/` — pulls from EUKA, Cruva, Kalodata, etc.)_

| File                    | System | Date | Notes |
| ----------------------- | ------ | ---- | ----- |
| _(none registered yet)_ |        |      |       |

## Active tasks

_(Briefs from Trupti — date, one-line task description, status, link to deliverable when complete.)_

| Date         | Task | Status | Deliverable |
| ------------ | ---- | ------ | ----------- |
| _(none yet)_ |      |        |             |

## Discipline (Yudhishthira's contract for Trupti tasks)

- **Reads:** `pocs/trupti/sheets/`, `pocs/trupti/raw/`, `pocs/trupti/exports/`, this register, the Bhishma constitution, the formula playbook, the shared `training/` directory.
- **Writes:** `pocs/trupti/deliverables/` only. No writes to other POCs' folders. No writes back to live Google Sheets (always-copy rule).
- **Task prefix:** when a Trupti task is dispatched, the deliverable file names start with `trupti_` so cross-POC searches are clean.
- **Cross-POC analysis:** if a task spans multiple POCs, Yudhishthira asks for explicit authorisation and surfaces the wider scope in the audit `.md`.

## Change log

- 2026-05-13 — bootstrap — POC folder created. Empty register pending data from Kartavya.
