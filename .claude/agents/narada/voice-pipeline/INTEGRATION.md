# Voice Pipeline → Narada Integration

> **Status:** acquired 2026-05-11. Upstream: `aaddrick/written-voice-replication` (MIT, master branch, commit pulled via gh API on 2026-05-11). 44 files, all markdown skill/agent definitions. No executable code from upstream is in Narada's path (the optional `scripts/hydrate.py` Reddit hydrator was deliberately not pulled).

## What was acquired

The full Claude-native voice-replication pipeline:

- **5 upstream agents** under `voice-pipeline/.claude/agents/` — pipeline-orchestrator, data-prep, analysis-agent, profiling-agent, synthesis-agent
- **30 upstream skill directories** under `voice-pipeline/.claude/skills/` — covering 25 analysis dimensions plus helper categories (writing-agents, writing-skills, automated-orchestration, etc.)
- **Methodology** at `voice-pipeline/docs/analysis_methods.md`
- **Upstream README + CLAUDE.md** preserved at `voice-pipeline/README.md` / `voice-pipeline/CLAUDE.md` so the original instructions remain fully readable
- **Upstream LICENSE** preserved (MIT)

**Deliberately not acquired:**

- `scripts/hydrate.py` — Reddit-specific hydration; Narada uses Slack DMs instead (see `SLACK-CORPUS.md`)
- The example output files (`aaddrick-voice.md` agent, `aaddrick-voice-replication/` skill) — Narada generates its own `kartavya-voice` instead

## Why we have this

Narada was already designed around a `voice-fingerprint.json` (see `agent.md` § "Voice fingerprint"). The fingerprint schema was sketched but never had an engine producing it. The acquired pipeline IS that engine.

This is **not a replacement for Narada** — Narada's identity, character, modes, forbidden phrases, and generic-reject filter all stay intact. The pipeline becomes a tool Narada calls when (a) the corpus has changed or (b) the fingerprint is stale or default.

## Identity preservation

| Narada keeps                                                       | Pipeline provides                                                                  |
| ------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| Character (celestial messenger, mischief disabled)                 | —                                                                                  |
| Two primary modes (mayank-update, creator-dm) + rare third (other) | —                                                                                  |
| Forbidden phrase lists                                             | New phrases discovered via stylometric analysis can extend (not replace) the lists |
| Generic-reject filter                                              | Stylometric signature phrases feed the cosine-similarity threshold                 |
| Length budgets (200w mayank-update / 80w creator-dm)               | —                                                                                  |
| Audience-model frontmatter                                         | Pipeline's audience-aware register-variation outputs supply richer audience model  |
| Never decide subject matter, never send                            | —                                                                                  |
| Tier-0, watched by Sanjaya                                         | —                                                                                  |
| `voice-fingerprint.json` schema                                    | New populator with measurable validation targets                                   |

## How Narada invokes the pipeline

The pipeline's entry point is the `pipeline-orchestrator` agent in `voice-pipeline/.claude/agents/pipeline-orchestrator.md`. Narada calls it when the voice-fingerprint needs (re)building.

### Trigger conditions (in priority order)

1. `voice-samples/` directory has changed since `voice-fingerprint.json` was last written (mtime check)
2. `voice-samples/` contains ≥50 items but `voice-fingerprint.json` is missing or shows `voice_calibration: default`
3. Kartavya explicitly asks Narada to "rebuild the voice" or "refresh fingerprint"

### Pipeline invocation pattern

When triggered, Narada delegates to the orchestrator:

```
Use the pipeline-orchestrator agent (under voice-pipeline/) to run the
analysis pipeline on the corpus at voice-samples/. Kartavya is the subject.
Output to voice-pipeline/runs/<YYYYMMDD>-kartavya/ — produce voice agent at
runs/<YYYYMMDD>-kartavya/.claude/agents/kartavya-voice.md and voice skill at
runs/<YYYYMMDD>-kartavya/.claude/skills/kartavya-voice-replication/SKILL.md.
```

The orchestrator runs Data Prep → Analysis ∥ Profiling → Synthesis, writing 26 reports to `runs/<YYYYMMDD>-kartavya/docs/analysis/`.

### Folding the pipeline output into Narada's fingerprint

After the pipeline completes, Narada reads:

| Pipeline output                                                                                | Narada fingerprint field                                                                               |
| ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `analysis/18-stylometric-fingerprinting.md` → avg sentence length, comma rate, dash rate       | `avg_sentence_length`, `comma_density`, `dash_density`                                                 |
| `analysis/18-stylometric-fingerprinting.md` → top n-grams unique to subject vs corpus baseline | `top_signature_phrases`                                                                                |
| `analysis/19-readability-lexical-diversity.md` → Flesch-Kincaid, type-token ratio              | new field `readability`                                                                                |
| `analysis/16-liwc-psycholinguistic.md` → function-word rates, pronoun usage                    | new field `psycholinguistic_profile`                                                                   |
| `analysis/15-big-five-personality.md` → trait scores                                           | new field `personality_signal` (used to inform `register` description, not invoked directly in drafts) |
| `analysis/21-register-variation-code-switching.md` → audience-dependent register shifts        | extends `audience_model` per-recipient logic                                                           |
| `analysis/22-speech-act-pragmatic.md` → speech-act distribution                                | informs forbidden_phrase_observations and per-mode generation                                          |
| `analysis/24-style-specification.md` → consolidated style spec                                 | source-of-truth document referenced inline by Narada when drafting                                     |
| Generated `kartavya-voice` agent                                                               | invokable as a sub-agent in `mayank-update` and `other` modes for stylistic execution                  |

`voice-fingerprint.json` is rewritten with `voice_calibration: pipeline-derived` and a `pipeline_run_id` field pointing at the run directory.

## Adaptation: what Reddit-specific to ignore

The upstream pipeline assumes Reddit GDPR exports (posts.csv, comments.csv, account.csv, saved.csv, votes.csv). For Slack DM corpus:

| Pipeline skill                       | Reddit assumption       | Slack adaptation                                                                                                              |
| ------------------------------------ | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| 01 csv-metadata-forensic             | 5 cross-referenced CSVs | Single `slack-dms.csv` — relax the cross-ref check, log "single-file corpus"                                                  |
| 02b content-hydration                | Reddit API hydration    | **Skip** — Slack DMs already have full body text via the MCP export                                                           |
| 04 taxonomic-interest-classification | Subreddit hierarchy     | Skip if no equivalent topic labels — the pipeline degrades gracefully                                                         |
| 05 nmf-topic-modeling                | —                       | Works as-is on text                                                                                                           |
| 07 vader-sentiment                   | —                       | Works as-is on text                                                                                                           |
| 10 network-social-graph              | Parent-comment threads  | Map to Slack thread parent_ts; if 1:1 DMs only, this skill produces a degenerate "Kartavya ↔ Mayank" graph — log and continue |
| 12 temporal-circadian                | —                       | Works as-is on Slack timestamps                                                                                               |
| 18 stylometric-fingerprinting        | —                       | Works as-is — the meat of what Narada needs                                                                                   |
| 19 readability-lexical-diversity     | —                       | Works as-is                                                                                                                   |
| 21 register-variation                | Per-subreddit register  | Per-thread or per-DM-target register if more than one recipient corpus is provided                                            |

Narada's data-prep wrapper (see `SLACK-CORPUS.md`) produces a CSV the pipeline's `csv-metadata-forensic` skill can ingest. The pipeline's existing graceful-degradation handles missing metadata.

## Run isolation

Each pipeline run lives in its own directory:

```
voice-pipeline/runs/
  2026-05-11-kartavya-v1/
    .claude/agents/kartavya-voice.md
    .claude/skills/kartavya-voice-replication/SKILL.md
    docs/analysis/01-csv-metadata-forensic.md
    docs/analysis/02-tiered-processing-pipeline.md
    ... (26 reports)
    data/enriched/kartavya-corpus-cleaned.csv
    RUN_MANIFEST.md          # what corpus, what timestamp, what skipped
```

The `kartavya-voice.md` produced by each run is what Narada's `agent.md` § "Voice fingerprint" actually consumes. Older runs are kept (audit trail) but Narada always reads from the _latest_ run via a symlink at `voice-pipeline/runs/latest`.

## What's safe / what's gated

| Capability                                            | Status                                                                                       |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Reading pipeline skill/agent files                    | ✅ Safe — pure markdown                                                                      |
| Running analysis skills via Claude (no Python)        | ✅ Safe — Claude reads instructions and produces reports                                     |
| Auto-rebuilding voice-fingerprint.json                | ✅ On `voice-samples/` change                                                                |
| Auto-overwriting Narada's identity (modes, character) | ❌ Forbidden — pipeline outputs feed _into_ Narada's existing fields, never replace agent.md |
| Generating a `kartavya-voice` sub-agent               | ✅ Lives in `voice-pipeline/runs/<id>/.claude/agents/`, not in `narada/` directly            |
| Pipeline calling external services                    | ❌ None — pipeline is offline-only on the staged data                                        |
| Sending any message                                   | ❌ Narada doesn't send. Sub-agents don't send. Pipeline doesn't send.                        |

## Provenance

- **Source repo:** https://github.com/aaddrick/written-voice-replication
- **License:** MIT (preserved at `voice-pipeline/LICENSE`)
- **Acquired:** 2026-05-11 via `gh api` per-file pulls (no git clone — file-level audit trail)
- **Files:** 44 markdown + 1 LICENSE + 1 README + 1 CLAUDE.md + 1 .gitignore (= 48 total, 1.2MB)
- **Excluded from acquisition:** `scripts/hydrate.py`, `aaddrick-voice` example agent, `aaddrick-voice-replication` example skill, render-graph helpers (.dot, .js)

## Next steps owned by Narada

1. Build the Slack corpus → see `SLACK-CORPUS.md`
2. Run the pipeline on the corpus → produces first `kartavya-voice` agent
3. Refresh `voice-fingerprint.json` from pipeline outputs → first non-default calibration
4. Use `kartavya-voice` agent inside `mayank-update` and `other` modes for stylistic execution
5. Sanjaya watches first 20 outputs for drift; proposes heuristics if generic-reject fires too often
