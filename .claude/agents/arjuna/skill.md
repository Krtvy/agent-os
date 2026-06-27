# arjuna — Skill Manual

> Last updated: 2026-05-10 by bootstrap

## Purpose

Arjuna executes explicit, fully-parameterized instructions against connected MCPs and HTTP APIs. It refuses ambiguous instructions, defaults to dry-run for state-changing calls, enforces idempotency for destructive live calls, and respects per-target circuit breakers.

## Inputs

- `target` (required) — system + endpoint identifier.
- `parameters` (required) — full input payload.
- `expected_response_shape` (required) — success validator.
- `mode` (optional, default `dry-run`) — `live` or `dry-run`.
- `confirmation_required` (optional) — `true` or `false`.
- `idempotency_key` (required for destructive live calls) — caller-provided string.
- `rollback_plan` (recommended for destructive live calls) — text describing reversal steps.

## Outputs

A YAML response block. Format defined in `agent.md` § "Your outputs."

## Procedures

### P1. Bhishma load

- Read `bhishma.md`. Stop on missing file.

### P2. Instruction validation

- Verify all required fields present.
- Verify `target` resolves to a connected MCP or callable endpoint.
- If destructive live call without `idempotency_key`: refuse with `kind: missing-idempotency-key`.
- If ambiguous (multiple plausible interpretations): refuse with explanation.

### P3. Circuit-breaker check

- Read `.claude/agents/arjuna/circuit-breakers/<target>.json`.
- If `state: open`: refuse with reason `circuit-breaker open`. Surface `consecutive_failures` and `last_failure_at`.
- If `state: half-open`: allow this single probe.
- Else proceed.

### P4. Idempotency check

- If `idempotency_key` provided: read `.claude/agents/arjuna/idempotency-keys/<key>.json`.
- If a successful run exists within 30d: return that response, set `idempotency_hit: true`. Do not re-execute.
- Else: proceed.

### P5. Stale-data check (live state-changing only)

- For UPDATE-style calls: GET current state first. If already in the target state, abort with `status: success`, `summary: already in target state, no-op`.

### P6. Execute

- Execute via the appropriate MCP / WebFetch.
- Capture response.
- On 429 / rate-limit error: do not retry within `retry_after`. Return `status: failure` with rate-limit details.
- On other failure: retry up to 3 times with exponential backoff (1s, 4s, 9s).
- On 3rd consecutive failure: open the circuit breaker for this target.

### P7. Idempotency persist

- On success of a destructive live call: write `idempotency-keys/<key>.json` with the response and TTL.

### P8. Log

- Append to `logs/arjuna/<run_id>.log`: run_id, target, parameters (secrets redacted), response code, status, summary.

### P9. Return

- Compose the response block per `agent.md` § "Your outputs."
- Echo `rollback_hint` from input if `mode: live`.
- Include `circuit_breaker_state`.

### P10. Daily competitor video analysis (added 2026-05-11)

A second procedure path for the competitor content pipeline. Distinct from the P1–P9 generic-execution path above. Run on cron, NOT triggered per-instruction.

**Trigger.** Nightly at 01:00 IST via `scripts/video-analyze-batch.sh` (called by Nakula, downstream of Hanuman's P10 discovery).

**Inputs.**

- `raw_dir` — defaults to `competitor_content/raw/`
- `analyzed_dir` — defaults to `competitor_content/analyzed/`
- `date` — defaults to today in UTC
- `analyzer` — defaults to `gemini`. Possible values: `gemini` (direct API) or `video_analyzer_mcp` (Anthropic's MCP).

**Outputs.**

- Per video: `competitor_content/analyzed/<slug>/<video-id>.json` with this shape:

  ```json
  {
    "video_id": "7234567890",
    "brand_slug": "<entity-slug>",
    "analyzed_at_utc": "2026-05-11T01:14:00Z",
    "analyzer": "gemini",
    "analyzer_model": "gemini-2.0-flash",
    "tier": "deep",
    "transcript": "...",
    "hook_description": "<description of how the video opens>",
    "hook_type": "problem-led",
    "format_tags": ["talking-head", "single-shot", "on-screen-text"],
    "claims": [
      { "text": "improves sleep within 7 days", "category": "sleep" },
      { "text": "no morning grogginess", "category": "sleep" }
    ],
    "cta": "comment 'sleep' for the link",
    "duration_seconds": 23,
    "performance_signal": {
      "views": 84200,
      "view_velocity_per_hour": 2630,
      "baseline_multiplier": 2.4
    },
    "run_id": "arjuna-20260511-011400Z-c9d2a1"
  }
  ```

- Idempotency key per video at `.claude/agents/arjuna/idempotency-keys/video-analysis/<video-id>.json` so re-runs don't re-analyze.

**Two-tier analysis (cost control + signal filter):**

Per the plan refinement: only deeply analyze the videos that are actually performing. Lightweight pass for the rest.

| Tier            | When                                                              | What analyzer extracts                                                             |
| --------------- | ----------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **deep**        | `baseline_multiplier ≥ 2.0` (video at ≥2× brand's 30-day average) | Full transcript, hook description + type, format tags, claims with categories, CTA |
| **lightweight** | All other recent videos                                           | Metadata only: caption, hashtags, duration, view count. No video upload to Gemini. |

**Steps.**

1. Read `bhishma.md`.
2. Load Gemini keys from `.credentials.yml` (`gemini.keys` list). Filter out `REPLACE_ME` placeholders. If empty, run in stub mode (write empty analysis JSONs with `error: no_gemini_keys`).
3. Find all unanalyzed videos:
   - Read all `competitor_content/raw/<slug>/<date>.json` files newer than yesterday
   - For each video, check `.claude/agents/arjuna/idempotency-keys/video-analysis/<video-id>.json`
   - Skip if already analyzed
4. Compute per-brand baseline:
   - Look back at past 30 days of analyzed videos for that brand
   - Compute mean view count
   - For each new video, compute `baseline_multiplier = views / mean_views`
   - For brands with <10 prior videos analyzed, default `baseline_multiplier = 1.0` (no boost, no penalty — bootstrap phase)
5. For each unanalyzed video, decide tier:
   - `baseline_multiplier ≥ 2.0` → tier: deep
   - else → tier: lightweight
6. **Deep tier:** Upload video URL to Gemini's `generateContent` with a structured prompt that extracts transcript + hook + format + claims + CTA. Use `gemini-2.0-flash` or `gemini-2.5-flash` (cheaper than -pro, sufficient for this).
   - Try each Gemini key in order on 429/5xx.
   - On all keys exhausted: write `error: gemini_exhausted` to that video's analyzed JSON, continue with next.
7. **Lightweight tier:** Extract metadata fields directly from the raw JSON (no Gemini call). Write analyzed JSON with `tier: lightweight`, `transcript: null`, fields populated where available.
8. Write each analyzed JSON to `competitor_content/analyzed/<slug>/<video-id>.json`.
9. Write idempotency key.
10. Run summary:
    - Total videos discovered yesterday: N
    - Already analyzed (skipped): S
    - Deep analyzed this run: D
    - Lightweight processed: L
    - Errors: E
    - Gemini key used (last-4 only): K
    - run_id: `arjuna-<YYYYMMDD-HHMMSSZ>-<6char-hash>`

**Constraints (specific to P10):**

- Never re-analyze a video that has an idempotency key (saves cost + maintains audit trail).
- Per Bhishma R20, every video JSON carries the run_id that produced it.
- Per Bhishma R5, analyzed JSONs are write-once-then-rename-on-update. Never edit in place.
- Gemini calls are read-only on TikTok (we send video URLs; Gemini fetches publicly).
- Rate-limit awareness: Gemini free tier is 60 RPM. Batch with 1-sec delays between calls (defensive).

**Output written to:** `competitor_content/analyzed/<slug>/<video-id>.json` and `logs/arjuna/<run_id>-video-analysis.log`.

## Heuristics

- _(none yet — populated by Sanjaya proposals)_

## Confidence (read-only reference)

> Confidence weights are defined in `_meta/conductor/bhishma.md`.

## Run-id format (read-only reference)

> Run-id format is defined in `docs/RUN_ID_SPEC.md`.

## Change log

- 2026-05-10 — bootstrap — initial skill manual.
- 2026-05-11 — added P10 (daily competitor video analysis procedure) for the competitor content pipeline. Two-tier analysis (deep ≥2× baseline, lightweight otherwise), Gemini integration with key rotation, idempotency keys per video.
