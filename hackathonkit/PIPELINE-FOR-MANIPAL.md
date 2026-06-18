# AUNTIE AT SCALE — Automation Pipeline Brief

## For Manipal — Use for PowerPoint slides

---

## THE 5-STAGE CONTENT MACHINE (Mosaic Wide-Brief Tasks 1-5)

```
[BRAND INPUT]
    │
    ▼
[1] CHARACTER ID
    LLM agent (Claude / GPT-4) classifies brand profile
    → proposes consumer persona (age, geo, pain point, voice)
    │
    ▼
[2] UNIVERSE
    LLM agent expands persona into family map, signature phrase,
    wardrobe rotation, 30-day emotional arc, recurring side characters
    │
    ▼
[3] SCRIPTS
    LLM agent produces 30-day arc with 4 plot beats:
    rejection → avoidance → curiosity → conversion
    Locks dialogue + signature-phrase inversion
    │
    ▼
[4] SCREENPLAY
    LLM agent breaks each day into 5-beat reel structure:
    Hook → Setup → Escalation → Twist → Cliffhanger
    │
    ▼
[5] CONTENT GENERATION (the AI tool stack)
    │
    ├─ STILLS:        Whisk / Google Flow  ($0, daily free tier)
    │
    ├─ VIDEO:         Higgsfield (Kling 3.0 with audio sync
    │                              + Cinema Studio Video 3.0 for cinematic hero shots
    │                              + Wan 2.7 for true audio-to-lipsync)
    │
    ├─ VOICE:         ElevenLabs (Indian English voices — "Tashi", "Laura")
    │
    ├─ LIPSYNC:       Wan 2.7 (Higgsfield)  — takes still + audio file → lipsynced MP4
    │
    ├─ EDIT:          CapCut Mac desktop ($0 — free)
    │
    └─ MUSIC / SFX:   YouTube Audio Library / Pixabay Music ($0, commercial-safe)
    │
    ▼
[OUTPUT]
    1 reel/day per channel × 50 channels per brand
    Scheduled to Meta via Meta Graph API
```

---

## THE TOOLS WE USED (Mosaic-replicable)

| Tool                        | What it does                                                                                | Cost                       | Why we picked it                         |
| --------------------------- | ------------------------------------------------------------------------------------------- | -------------------------- | ---------------------------------------- |
| **Whisk / Google Flow**     | Character + scene stills generation, identity-locked                                        | Free tier (50 credits/day) | Best free character consistency          |
| **Higgsfield Ultra**        | Multi-model video gen via single MCP — Kling 3.0, Cinema Studio Video 3.0, Wan 2.7, Veo 3.1 | $99/month                  | One subscription unlocks 7+ video models |
| **Kling 3.0**               | Video with built-in audio + generic lipsync                                                 | Higgsfield credits         | Fast for reaction shots                  |
| **Cinema Studio Video 3.0** | Premium cinematic quality                                                                   | Higgsfield credits         | Hero emotional moments                   |
| **Wan 2.7**                 | True audio-to-lipsync from external MP3 + still                                             | Higgsfield credits         | Perfect lipsync to ElevenLabs voice      |
| **ElevenLabs**              | Voice gen with Indian English voices                                                        | Free tier (10k chars/mo)   | Proper Hindi pronunciation               |
| **CapCut Mac**              | Timeline editing, captions, music layering                                                  | Free                       | Replaces Adobe Premiere                  |
| **YouTube Audio Library**   | Royalty-free music + SFX                                                                    | Free, commercial-safe      | Zero IP risk                             |
| **Meta Graph API**          | Auto-schedule to Instagram/Facebook                                                         | Free                       | Closes the loop                          |

**TOTAL MARGINAL COST PER REEL: ~$0**
**Total monthly tool cost per operator: $99 (Higgsfield Ultra, optional — sunk cost Mosaic already pays)**

---

## THE AUTOMATION ROADMAP — 4 PHASES

### Phase 1 — MANUAL LOOP (this hackathon — today)

- Operator drives each tool manually in browser/desktop
- Whisk → Kling → ElevenLabs → CapCut → export
- 1 reel produced in ~4 hours by 1 operator
- Proves the quality bar

### Phase 2 — SEMI-AUTOMATED (Week 2)

- n8n / LangGraph orchestrates the tool chain via APIs
- Whisk API → Higgsfield MCP → ElevenLabs API → ffmpeg auto-assembly
- Operator reviews + approves at 3 checkpoints:
  1. Character fidelity (does Pinky look right?)
  2. Brand-safety compliance (does it pass Mosaic legal?)
  3. Batch publish approval (greenlight the day's content)
- 5 reels/day per operator

### Phase 3 — FULL PIPELINE (Month 2)

- JSON brief (brand + product + persona) → automated pipeline
- LLM agent fills all 5 Tasks (Character → Universe → Scripts → Screenplay → Generation)
- Produces full 30-reel season from one operator briefing in ~24 hours
- Human approves at 3 gates only

### Phase 4 — CONTINUOUS (Quarter 2)

- 50 operators × 5 brands × 30 reels = 7,500 reels/month
- Auto-schedule via Meta Graph API
- Virality Predictor scores reels pre-publish; only top 70% goes live
- Adapts daily based on performance data

---

## COST STORY (FOR THE PITCH SLIDE)

| Metric                                  | Auntie at Scale Pipeline                              | Traditional UGC Creators        |
| --------------------------------------- | ----------------------------------------------------- | ------------------------------- |
| Per reel (marginal cost)                | **$0**                                                | **$1,500 – $3,000** (US market) |
| 30 reels/month (1 channel)              | **$0 – $99**                                          | **$45,000 – $90,000**           |
| 50 channels × 5 brands × 30 reels/month | **$5,000 / month max** (tool costs)                   | **$11.25M – $22.5M / month**    |
| Annual at scale                         | **$60K / year**                                       | **$135M – $270M / year**        |
| **Cost reduction**                      | —                                                     | **>99%**                        |
| Storytelling                            | **Stays human** (operator writes Universe + dialogue) | Same                            |

---

## BRAND-AGNOSTIC PROOF

Same pipeline. Different brand. Different character. Different journey stage.

| Pipeline run         | Brand       | Character                                       | Stage                       | Output                 |
| -------------------- | ----------- | ----------------------------------------------- | --------------------------- | ---------------------- |
| Run 1 (today's demo) | Root Labs   | Pinky Dadi (47, NRI mom, Edison NJ)             | Consideration               | 30 reels MagAshwa arc  |
| Run 2 (next week)    | Man Matters | Arjun "The Hair Guy" (26, Bangalore engineer)   | Consideration + Transaction | 30 reels hair-loss arc |
| Run 3                | BeBodywise  | Priya "The PCOS Diarist" (25, Chennai marketer) | Awareness + Consideration   | 30 reels PCOS-care arc |
| Run 4                | Little Joys | Nisha "The First-Time Mom"                      | Awareness                   | 30 reels parenting arc |
| Run 5                | OWN         | Custom persona TBD                              | TBD                         | 30 reels arc           |

---

## KEY TALKING POINTS FOR THE PITCH

1. **"The Machine doesn't replace creators — it replaces the cost of creators."**
2. **"Storytelling stays human. Production becomes free."**
3. **"One operator. 50 channels. Zero rate cards. Zero scheduling conflicts."**
4. **"Swap the brand. Swap the character. Run again."**
5. **"Today is the proof. Tomorrow it runs daily on its own."**

---

## TECHNICAL STACK SUMMARY (FOR DEVELOPER SLIDES IF NEEDED)

- **Orchestration:** n8n (no-code) OR LangGraph (Python) — operator's choice
- **LLM:** Claude API (for character/universe/script gen) or OpenAI
- **Image gen API:** Whisk / Google Imagen
- **Video gen API:** Higgsfield Ultra ($99/mo unlocks all models via single MCP)
- **Voice gen API:** ElevenLabs (Starter $5/mo for commercial-use API access)
- **Lipsync API:** Higgsfield Wan 2.7 (included in Ultra)
- **Edit:** CapCut Mac (manual) OR Remotion (programmatic at scale)
- **Publish:** Meta Graph API / TikTok Creator API

---

_Document generated: 2026-05-16 16:09 IST_
_For: Mosaic Wellness Content Hackathon presentation_
_Project: Auntie at Scale (Pinky Dadi for Root Labs)_
