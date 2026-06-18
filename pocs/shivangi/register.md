---
poc: Shivangi
created: 2026-05-13
folder: pocs/shivangi/
status: bootstrap # bootstrap | active | dormant
---

# Shivangi — POC Register

> Source of truth for what Shivangi owns, what data is available to Yudhishthira when working on a Shivangi task, and the current task queue. Yudhishthira reads this file FIRST when a task names "Shivangi."

## Identity

- **Name:** Shivangi
- **Role:** Point of Contact at Rootlabs
- **Scope:** _(to be filled — which creators / campaigns / products fall under Shivangi's ownership)_

## Creators in scope

_(Note from May workbook: the `Creators Tagging` tab shows Shivangi as one of the active POCs handling several creators including `thehuntervance`, `flawkolito`, `asadfinds`. Populate fully from that tab once it's confirmed authoritative.)_

| Username                           | Product line | Status | Notes |
| ---------------------------------- | ------------ | ------ | ----- |
| _(populate from Creators Tagging)_ |              |        |       |

## Data sources

### Google Sheets

_(Shivangi's live working sheets — URL + sharing status. Yudhishthira fetches via `lib/yudhi-fetch.sh` into `sheets/`.)_

| Sheet name              | URL | Access | Last fetched |
| ----------------------- | --- | ------ | ------------ |
| _(none registered yet)_ |     |        |              |

### Raw exports

_(Files in `pocs/shivangi/raw/` — populated by the human or via Hanuman scout reports. One row per file with: filename, source, date received.)_

| File                    | Source | Date received | Description |
| ----------------------- | ------ | ------------- | ----------- |
| _(none registered yet)_ |        |               |             |

### External system exports

_(Files in `pocs/shivangi/exports/` — pulls from EUKA, Cruva, Kalodata, etc.)_

| File                    | System | Date | Notes |
| ----------------------- | ------ | ---- | ----- |
| _(none registered yet)_ |        |      |       |

## Active tasks

_(Briefs from Shivangi — date, one-line task description, status, link to deliverable when complete.)_

| Date         | Task | Status | Deliverable |
| ------------ | ---- | ------ | ----------- |
| _(none yet)_ |      |        |             |

## Discipline (Yudhishthira's contract for Shivangi tasks)

- **Reads:** `pocs/shivangi/sheets/`, `pocs/shivangi/raw/`, `pocs/shivangi/exports/`, this register, the Bhishma constitution, the formula playbook, the shared `training/` directory.
- **Writes:** `pocs/shivangi/deliverables/` only. No writes to other POCs' folders. No writes back to live Google Sheets (always-copy rule).
- **Task prefix:** when a Shivangi task is dispatched, the deliverable file names start with `shivangi_` so cross-POC searches are clean.
- **Cross-POC analysis:** if a task spans multiple POCs, Yudhishthira asks for explicit authorisation and surfaces the wider scope in the audit `.md`.

## Change log

- 2026-05-13 — bootstrap — POC folder created. Empty register pending data from Kartavya. Pre-populated note: visible in Creators Tagging tab as active POC for several creators.
