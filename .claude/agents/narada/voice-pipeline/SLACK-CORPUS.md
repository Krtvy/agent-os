# Slack DM Corpus Extraction (for Narada voice training)

> Purpose: produce a CSV at `voice-samples/kartavya-corpus.csv` that the upstream pipeline's `csv-metadata-forensic` skill can ingest. Replaces the upstream Reddit hydration step entirely. (The filename was originally specified as `kartavya-slack-dms.csv` but the actual corpus contains email + Slack + course-correction samples, so the more general `kartavya-corpus.csv` was adopted on 2026-05-11.)

## Required output schema

The pipeline's data-prep skills look for a `body` or `text` column. Everything else is optional but improves analysis quality.

```csv
id,timestamp,recipient,thread_id,parent_ts,body,reactions,is_reply
slack-dm-001,2026-04-15T09:42:00+05:30,mayank,T01,—,"the actual message text here",0,false
slack-dm-002,2026-04-15T09:51:12+05:30,mayank,T01,2026-04-15T09:42:00,"reply text",2,true
...
```

| Column      | Required     | Used by                                                        |
| ----------- | ------------ | -------------------------------------------------------------- |
| `id`        | yes          | csv-metadata-forensic                                          |
| `timestamp` | recommended  | temporal-circadian-patterns, longitudinal-growth-curves        |
| `recipient` | helpful      | register-variation-code-switching (per-recipient voice shifts) |
| `thread_id` | optional     | network-social-graph                                           |
| `parent_ts` | optional     | network-social-graph (reply chains)                            |
| `body`      | **required** | every analysis skill                                           |
| `reactions` | optional     | weighted-engagement-scoring                                    |
| `is_reply`  | optional     | rhetorical-discourse-structure                                 |

## Volume targets

| Tier           | Item count | Quality of resulting voice                                         |
| -------------- | ---------- | ------------------------------------------------------------------ |
| Minimum viable | 50         | Default-leaning, may not capture nuanced register shifts           |
| Recommended    | 150–300    | Stable numeric profile, distinguishable from baseline              |
| Strong         | 500+       | Rich audience-aware register variation, reliable signature phrases |

**Only include messages authored by Kartavya.** Messages from Mayank or other recipients should be excluded from the body column — they're not the voice being trained. (You may include incoming messages in a separate `context_before` column if you want the pipeline to learn reply-style patterns, but the upstream pipeline doesn't currently use this.)

## Three extraction paths, in order of preference

### Path 1 — Slack MCP (preferred, on-demand, incremental)

The Slack MCP server is connected in this Claude Code setup. Use the `slack_search_*` and `slack_read_thread` tools to pull messages.

**Search query pattern (Kartavya → Mayank DMs):**

```
Use mcp__claude_ai_Slack__slack_search_users to find Mayank's user ID.
Then use mcp__claude_ai_Slack__slack_search_public_and_private with
the query: "from:@kartavya in:@mayank" — date range: last 12 months.
Page through results, extracting (ts, text, thread_ts, reactions).
```

**Pros:** No export approval needed, runs in the conversation, returns up to ~1000 messages per query.
**Cons:** Search has TODO upper bounds; ancient DMs may need workspace export instead.

### Path 2 — Slack workspace export (admin-approved, comprehensive)

If you have admin access, request a workspace export of Kartavya's DM history. Slack provides this as JSON files — one per channel (DMs are channels too) with messages.

**Workflow:**

1. Workspace admin → Settings → Workspace settings → Import/Export Data → Export
2. Select "Standard" or "Corporate" export depending on plan
3. Filter to DMs with Mayank
4. Download zip
5. Extract messages from `D<channel-id>.json` files, transform to CSV schema above

**Pros:** Complete history, no rate limits.
**Cons:** Needs admin approval; one-shot rather than incremental.

### Path 3 — Manual paste (bootstrap-only)

If neither MCP nor admin export is available, paste 50+ recent messages from Slack into a file (one per line, with rough timestamps if possible). Narada's data-prep wrapper can chunk and tag these into the CSV format.

**Pros:** Zero infrastructure.
**Cons:** Fragile, no metadata, manual work.

## Transformation script

Once raw messages are extracted (any of the three paths), normalize to the CSV schema. Place the script at `voice-pipeline/scripts/build-slack-corpus.py` (write only after Kartavya approves the data flow). The script must:

1. Filter to messages authored by Kartavya
2. Strip Slack-specific markup (channel mentions `<#C...>`, user mentions `<@U...>`, links `<https://...|label>` → `label`, emoji `:thumbsup:` → ` ` or kept depending on analysis)
3. Drop messages under 5 words (chat-noise threshold)
4. Drop messages that are quoted text only or attachment-only
5. Deduplicate by content hash (Kartavya sometimes resends the same message)
6. Preserve timestamps in ISO-8601 with TZ
7. Output one row per message to `voice-samples/kartavya-corpus.csv`

## Privacy and content classification

Before running the pipeline:

- **Redact PII** that's not Kartavya's own: phone numbers, email addresses, addresses, financial figures that aren't Kartavya's to share. (The pipeline doesn't need them; their absence doesn't affect voice analysis.)
- **Exclude any DM thread Mayank explicitly marked confidential** — review thread headers for any "do not share" language and drop those threads entirely.
- **Voice-train on register-stable content only** — exclude vacation/sick-day messages, emergency 1-liners ("on it"), and copy-paste forwards. These don't carry voice and dilute the analysis.

## How Narada knows the corpus is ready

The corpus is "ready for pipeline" when:

1. `voice-samples/kartavya-corpus.csv` exists
2. Row count ≥ 50 (minimum viable) — Narada logs a warning at <150
3. The CSV passes a basic schema check (all required columns present, no empty bodies, all timestamps parse)
4. The corpus has been written within the last 24h (so Narada doesn't run on stale data without confirmation)

When all four pass, Narada's skill.md procedure P2 (voice-fingerprint refresh) calls the pipeline-orchestrator. Otherwise, Narada falls back to `voice_calibration: default` and notes the reason in the output frontmatter.

## Multiple recipients (future)

If Kartavya wants Narada to draft messages to recipients beyond Mayank (e.g., creator DMs in mode 2, vendor emails in mode 3), the corpus extension is:

- Pull Kartavya's DMs to _that_ recipient or to recipients of the same role-class
- Tag each row's `recipient` column accordingly
- The pipeline's `register-variation-code-switching` skill produces per-recipient register profiles
- Narada's mode-specific drafting reads the matching register profile

This is **not required for v1**. The Mayank-DM corpus alone is sufficient to bootstrap. Multiple recipients become valuable when Narada's mode 3 (`other`) sees real volume.

## Refresh cadence

| Trigger                                      | Action                                                                                       |
| -------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Weekly (auto)                                | Re-pull last 7 days of DMs, append to corpus, re-run pipeline incrementally if ≥10 new items |
| Per Kartavya request                         | Full re-pull, full pipeline run                                                              |
| When generic-reject fires >3 times in a week | Force a refresh — the voice has likely drifted from the cached fingerprint                   |

## What this guide does not do

- Send anything anywhere
- Modify Slack messages
- Read DMs Kartavya didn't author (incoming messages are out of scope unless he explicitly opts in)
- Train any external model — the entire pipeline runs through Claude on the corpus locally
