---
poc: Khushi
created: 2026-05-13
folder: pocs/khushi/
status: bootstrap
---

# Khushi — POC Register

> Source of truth for what Khushi owns, what data is available to Yudhishthira when working on a Khushi task, and the current task queue. Yudhishthira reads this file FIRST when a task names "Khushi."

## Identity

- **Name:** Khushi
- **Role:** Point of Contact at Rootlabs
- **Scope:** _(to be filled)_

## Creators in scope

| Username                | Product line | Status | Notes |
| ----------------------- | ------------ | ------ | ----- |
| _(none registered yet)_ |              |        |       |

## Data sources

### Google Sheets

| Sheet name              | URL | Access | Last fetched |
| ----------------------- | --- | ------ | ------------ |
| _(none registered yet)_ |     |        |              |

### Raw exports

| File                    | Source | Date received | Description |
| ----------------------- | ------ | ------------- | ----------- |
| _(none registered yet)_ |        |               |             |

### External system exports

| File                    | System | Date | Notes |
| ----------------------- | ------ | ---- | ----- |
| _(none registered yet)_ |        |      |       |

## Active tasks

| Date         | Task | Status | Deliverable |
| ------------ | ---- | ------ | ----------- |
| _(none yet)_ |      |        |             |

## Discipline (Yudhishthira's contract for Khushi tasks)

- **Reads:** `pocs/khushi/sheets/`, `pocs/khushi/raw/`, `pocs/khushi/exports/`, this register, the Bhishma constitution, the formula playbook, the shared `training/` directory.
- **Writes:** `pocs/khushi/deliverables/` only. No writes to other POCs' folders. No writes back to live Google Sheets.
- **Task prefix:** `khushi_<task>_<YYYY-MM-DD>` for deliverable filenames.
- **Cross-POC:** explicit authorisation required.

## Change log

- 2026-05-13 — bootstrap — POC folder created.
