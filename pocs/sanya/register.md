---
poc: Sanya
created: 2026-05-13
folder: pocs/sanya/
status: bootstrap
---

# Sanya — POC Register

> Source of truth for what Sanya owns, what data is available to Yudhishthira when working on a Sanya task, and the current task queue. Yudhishthira reads this file FIRST when a task names "Sanya."

## Identity

- **Name:** Sanya
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

## Discipline (Yudhishthira's contract for Sanya tasks)

- **Reads:** `pocs/sanya/sheets/`, `pocs/sanya/raw/`, `pocs/sanya/exports/`, this register, the Bhishma constitution, the formula playbook, the shared `training/` directory.
- **Writes:** `pocs/sanya/deliverables/` only. No writes to other POCs' folders. No writes back to live Google Sheets.
- **Task prefix:** `sanya_<task>_<YYYY-MM-DD>` for deliverable filenames.
- **Cross-POC:** explicit authorisation required.

## Change log

- 2026-05-13 — bootstrap — POC folder created.
