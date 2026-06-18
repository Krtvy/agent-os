# Voice corpus — what to learn vs. what to outgrow

> **Author rating:** Kartavya himself rates this corpus **6/10** as of 2026-05-11.
> **Implication for Narada:** These 21 samples are real production voice — the most accurate signal we have about how Kartavya actually writes to Mayank. But they are also a _reactive_ baseline shaped by inconsistent prompts, late-night drafts, and weeks where AI work was thin. **Narada's job is to extract the load-bearing patterns and quietly elevate the weak ones — not to clone the average.**

---

## Patterns Narada should KEEP (the 6/10 strengths)

These are real and worth replicating.

| Pattern                                   | Example                                                                               | Why it works                                                  |
| ----------------------------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| **Plain-English over jargon**             | "Refuses to invent answers" instead of "implements hallucination guardrails"          | Mayank reads in 30 seconds; jargon costs comprehension        |
| **Specific numbers**                      | "$14.27M across that group", "8 commits", "554 of 1,384 creators"                     | Numbers > vague claims                                        |
| **Concrete shipped output**               | "The API call now auto-retries when something temporary fails"                        | Names what changed, not effort                                |
| **Brief mechanism explanations**          | "It cuts the extra words sent to the AI every time, so each chat costs a little less" | When jargon is unavoidable, immediate plain-English follow-up |
| **Tomorrow section with 2–3 items max**   | "Phase 2.B of the classifier (showing the model 2-3 example answer pairs)"            | Specific next step beats open-ended commitment                |
| **Inline-definition dash style**          | "Vidura - the truth-telling minister - does research..."                              | Compresses persona + role efficiently                         |
| **Repository links at end**               | `Repos: Classifier: https://github.com/Krtvy/LabeLLM`                                 | Audit trail, lets Mayank verify if he wants                   |
| **Honest acknowledgment of stuck points** | "Kept hitting the Gemini quota wall through the day"                                  | Real obstacles named — builds trust                           |
| **No emoji, no bold, no fake urgency**    | Throughout                                                                            | Mayank's voice is also flat-tone; matches register            |

---

## Patterns Narada should DROP (the 4-points-of-improvement)

These show up across multiple samples and mostly explain the 6/10 ceiling.

### 1. Inconsistent header format

The title line drifts wildly across samples:

- "AI Update Day 1" / "AI Update Day 2" (numbered, bad — implies a finite series)
- "AI Update 24 April" through "AI Update 6 May" (date-first format inside line — most common)
- "7 May / AI Update" (date moved above) — drift
- "Updates on what I've been working on recently" (sample-007 — no template at all)
- "Update for yesterday and today" (sample-006 — apologetic compensation header)

**Narada rule:** lock a single header format. Recommend:

```
Hey Mayank,
AI Update — <D MMM>

```

One blank line after greeting. One blank line after header. Date format always `D MMM` (e.g., "10 May"). No "Day N" numbering. No "Updates on what I've been..." wandering. No multi-day catch-up headers — if a day is missed, the next update is for the new day; previous gaps get one factual sentence in the body, not a header rewrite.

### 2. Apologetic / explanatory openers on light days

Several samples open with the day's _constraint_ rather than the day's _output_:

- "Today went into the move..." (sample-014)
- "Today was on internal data work, no AI side today" (sample-015)
- "Was not getting dedicated time to sit on AI because of the move" (sample-016)
- "Mom was visiting from Delhi after three months..." (sample-001 / 10-May reference)

**Mayank's response to this pattern was a course correction**: _"Even if there is no AI work, you should still learn"_ (recipient-signals.md, 2026-05-01).

**Narada rule:** never open with the constraint. Open with the **smallest concrete thing learned or shipped, however small.** The constraint can be one sentence in the body, not the headline. Example reframe:

> ❌ "Today went into the move. Did not get to the AI projects today."
> ✅ "Read the AlphaProof paper between packing rounds — RL on verifiable rewards, three takeaways below. Move ate the build hours."

### 3. Vague learning verbs

Words that signal _consumption_ not _production_:

- "Started looking at HyperAgent" (sample-009)
- "Trying to understand how AI agent tools work" (sample-009)
- "learned about building AI agents the introduction do's and dont's" (sample-006)
- "read the documentation today so I can code from tomorrow onwards" (sample-021)

**Mayank's response to this pattern was**: _"Don't want you to just listen to podcasts. Actually execute something daily. Move faster."_ (2026-04-22).

**Narada rule:** if a day was genuinely consumption-only, name **the one specific thing the consumption produced** (a decision, a plan, an experiment to run tomorrow) — never "learned about X" or "looking at Y" without an output. If there's truly no output, that's a missed day to acknowledge in one line, not pad over.

### 4. Performative commitment phrases

Phrases that promise future behavior to compensate for present gaps:

- "Will be sharing one of these every day" (sample-003)
- "From here on, daily updates without fail" (sample-007)
- "From the new place onwards, the AI updates will be richer" (sample-015)
- "Daily updates without fail" appears 3+ times across the corpus

**Narada rule:** never promise consistency in the message. Demonstrate it. If consistency has been a problem, do not announce the fix — just send the next day's update on time.

### 5. Hedging chattiness

- "Let me know if you need any other update cause the context I understood this is the update for yesterday" (sample-005)
- "Cause the context I understood..." patterns elsewhere
- Asking Mayank to validate the format mid-message

**Narada rule:** if uncertain about whether the update format is right, do not ask inside the update. The update commits to a format. Format questions are out-of-band (a separate brief Slack message, not embedded).

### 6. Buried structure in prose

Sample-007, sample-014 paragraph 2, sample-020's AI section — these read as brain-dumps where the structural beats (what shipped, what's blocked, what's next) are scattered through dense prose.

**Narada rule:** every `mayank-update` has at most 4 sections, in this order, each with a hard label:

1. **Shipped today** (or "Yesterday") — concrete output, bulleted
2. **Blocked** (only if real) — one line
3. **Tomorrow** — 2–3 numbered items, each specific enough to verify
4. **Repos / links** — only if changed

Section 2 ("Blocked") is omitted if nothing is blocked. Don't manufacture friction.

### 7. Soft sign-off

"Good night." appears at the end of most updates. Mayank's responses are "thanks" or "Thanks" — no return greeting. The "Good night" is dead weight.

**Narada rule:** end with the last substantive line. No sign-off, no "Good night," no "Let me know if..."

### 8. Multi-day aggregation when a day is missed

"Update for yesterday and today" (sample-006), "Updates on what I've been working on recently" (sample-007) are compensatory headers — they admit a missed day in the format itself.

**Narada rule:** if a day is missed, the next update is dated the current day. The missed day's output (if any) gets one inline sentence in the body. The header doesn't apologize.

### 9. Inconsistent repository link placement

- Sometimes "Repos:" section at end
- Sometimes inline links in the body
- Sometimes both (links in body PLUS a "Repos:" section at end — duplication)
- Sample-006 and sample-007 (first version) have no link section

**Narada rule:** repos go in a single "Repos:" section at the end, only if the repo content changed today. If unchanged, omit. Never duplicate a link inline + in the section.

### 10. Plain-English explanations going too explanatory

"It cuts the extra words sent to the AI every time, so each chat costs a little less" (sample-017) — by week 3, Mayank knows what tokens and prompts are. The explanation reads as condescension or padding.

**Narada rule:** plain-English the _first time_ a concept appears in the corpus. After Mayank has seen it once, use the technical term cleanly.

---

## Target voice profile (what 9/10 looks like)

Putting all the corrections above into a positive description:

- **Length budget**: 120–250 words for daily, up to 350 for major-launch days (the May-10 update is the model for an expanded day)
- **Header**: single canonical format `Hey Mayank,` newline `AI Update — D MMM`
- **Opening line**: the most important thing shipped today. Never the day's constraints.
- **Body**: 2–4 hard-labeled sections, scannable in 20 seconds
- **Numbers**: every claim that has a number gets the number
- **Vocabulary**: one plain-English explanation per new concept, then technical thereafter
- **Tomorrow**: 2–3 items, each specific enough that "did it ship?" is a yes/no question
- **No**: emojis, bold, urgency theater, performative commitments, soft sign-offs, hedging questions, multi-day aggregation headers
- **Yes**: concrete numbers, real obstacles named, repo links when relevant, terse honesty about light days

---

## How Narada uses this file

P2 of skill.md (voice-fingerprint refresh) reads `voice-samples/` to extract style markers via the upstream pipeline. **Narada additionally reads this file** at draft time to apply the _qualitative corrections_ the pipeline cannot extract numerically. Specifically:

1. After the pipeline produces the numeric `voice-fingerprint.json`, Narada runs the draft through the **DROP-pattern checks** above (`drop_check_1` through `drop_check_10`) before delivering. Each failure is a regenerate trigger, just like the existing forbidden-phrase filter.
2. The 9/10 target profile becomes the **aspirational anchor** that the pipeline-derived fingerprint should be measured against — Narada flags drift toward the 6/10 patterns even when the pipeline alone wouldn't catch them.
3. As the corpus grows past the 6/10 baseline (newer Kartavya updates that were drafted with these corrections in mind), the pipeline's signature-phrase extraction will naturally pick up cleaner patterns. This file becomes less load-bearing over time.

---

## Provenance

- **Corpus source**: Slack DM history Kartavya → Mayank, late April through 8 May 2026, plus the 10 May agent ecosystem update
- **Captured**: 2026-05-11 by paste from Slack
- **Self-rating provided by**: Kartavya
- **Sample count**: 22 (1 reference, 20 historical Mayank updates, 1 course-correction acknowledgment)
- **Recipient signals**: 15 Mayank messages saved separately for context (not training data)
