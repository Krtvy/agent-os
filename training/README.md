# `training/` — Shared training material for Yudhishthira

Cross-POC training material. Yudhishthira reads everything here regardless of which POC he's serving. This is where canonical examples, terminology, and reusable task patterns live.

**Not POC-specific.** Per-POC data lives under [`pocs/<name>/`](../pocs/). If something only matters for one POC, it goes in their folder, not here. If it's reusable across POCs, it goes here.

## Layout

```
training/
├── README.md          ← this file
├── examples/          ← past good deliverables, anonymised if needed
├── patterns/          ← reusable task patterns (the "when X, do Y" playbook entries)
└── glossary/          ← terminology, what each term means in this org's context
```

## What goes where

### `examples/`

Past completed deliverables that demonstrate "this is what a good answer looks like for this task type." Examples worth keeping:

- A reconciliation deliverable where the matched / mismatched / a_only / b_only breakdown was done well
- A tracker setup that the recipient actually used for weeks (vs one that got abandoned)
- A breakdown report that the manager called out as useful
- A failure example with the post-mortem — what was wrong, what should have been done

Format: `<YYYY-MM-DD>_<short-slug>_<task-type>.md` plus the original `.csv` if there was one.

### `patterns/`

Reusable task patterns — the "when the intern asks for X, here's the shape of the answer" library. Each pattern is a single file describing:

- **Trigger phrases** — words/intents the user might use that map to this pattern
- **Deliverable shape** — what the output looks like
- **Source data needed** — what Yudhishthira needs to ask for
- **Common pitfalls** — known failure modes
- **Worked example** — at least one concrete past instance

Naming: `<pattern-slug>.md`. Suggested starter patterns:

- `gmv-by-creator.md` — "give me each creator's GMV for product X in period Y"
- `cross-source-reconciliation.md` — "do the numbers in source A match source B?"
- `new-video-attribution.md` — "which videos drove the new-video GMV?"
- `tracker-setup.md` — "build me a live scoreboard that auto-updates"

### `glossary/`

Terminology specific to this org. Each term gets its own file or a section in a single `glossary.md`. Examples:

- **POC** — Point of Contact at Rootlabs (Vansh, Trupti, Shivangi, etc.)
- **GMV** — Gross Merchandise Value
- **New Video** — a video whose content_id is registered in the `Video Data` tab (per the MAP+LAMBDA+VLOOKUP formula verified 2026-05-13)
- **HGR** — one of Rootlabs' product lines (and the only product Main PoC aggregates)
- **EUKA** — external creator-marketplace / contract platform
- **Locked video** — _(needs definition — flagged for owner clarification in workbook report)_

## Discipline

- **Append-only at the document level.** Once an example or pattern is in here, fix errors by adding a follow-up dated file, not by editing in place. Mirrors Bhishma R5.
- **No raw data.** Training material describes _patterns_; the actual data examples should be anonymised or live as small extracts only.
- **Cross-link to the formula playbook.** When a pattern uses a Sheets formula, cite the section in `_audit/2026-05-12_sheets-formula-playbook.md` — that's the canonical formula reference.

## How Yudhishthira uses this

Today (Phase 1 — informal): Yudhishthira reads this directory at P1 (Session bootstrap) alongside the per-POC register and the Playbook.

Future (Phase 2 — formalised via the POC-workspace proposal at `_audit/2026-05-13_proposed-poc-workspace.md`): a P1 step explicitly cites which `training/` patterns are relevant before declaring filters in P4.

## Adding new training material

1. Drop the file into the right subfolder (`examples/`, `patterns/`, or `glossary/`).
2. If it's a pattern: link from this README's "starter patterns" list above.
3. If it's an example: add a one-line index to a future `examples/INDEX.md` (not yet created — defer until enough examples exist to warrant it).
4. No special review process — training material is fair game for anyone to add; quality is governed by usefulness, not gatekeeping.
