# Video Content Extraction Research Brief

**Date:** 2026-05-13
**Requested by:** Kartavya
**Researcher:** Vidura (research-agent)
**Scope:** Tools and workflows for extracting full granular context from YouTube (primary) and Twitter/X (secondary) videos without watching them.

---

## TL;DR Recommendation

**Top 3 tools, ranked by fit for Kartavya's use case (60-min AI/Claude Code content, Mac, CLI-friendly, free/cheap):**

1. **Fabric + yt-dlp** (CLI, free, open-source) -- The single best tool. One command pulls a YouTube transcript and pipes it through 140+ AI patterns (extract_wisdom, summarize, analyze_claims). Produces structured output with key ideas, insights, quotes, habits, facts, and references. Works with any LLM backend (Claude, GPT, Ollama local). Copy-paste command: `fabric -y "URL" --transcript-with-timestamps --pattern extract_wisdom --stream`

2. **Glasp Chrome extension** (browser, free) -- For when you want a quick sanity check before committing to Fabric. Shows the transcript sidebar with timestamps while you're on YouTube. One click copies the full transcript to clipboard. Supports Claude/GPT/Gemini summarization. Free for desktop, no API key needed.

3. **youtube-transcript-api + Claude Code** (Python, free, scriptable) -- For building a custom Claude Code skill. `pip install youtube-transcript-api`, pull the transcript in Python, pipe to Claude with a custom prompt that asks for minute-by-minute breakdown. Maximum control over output format.

**If you have 5 minutes, do this:** Install Fabric (`go install github.com/danielmiessler/fabric@latest`), run `fabric --setup` with your Anthropic or OpenAI key, then for any YouTube video: `fabric -y "URL" --transcript-with-timestamps --pattern extract_wisdom -o notes.md`. You now have structured notes in under 30 seconds.

---

## The Recommended Workflow

### Primary: Fabric Pipeline (YouTube, 60-min video)

**Prerequisites (one-time, ~10 min):**

```bash
# 1. Install Go if not present
brew install go

# 2. Install fabric
go install github.com/danielmiessler/fabric@latest

# 3. Add Go bin to PATH (add to ~/.zshrc)
export GOPATH=$HOME/go
export PATH=$GOPATH/bin:$PATH

# 4. Install yt-dlp (fabric's YouTube backend)
brew install yt-dlp

# 5. Run setup — paste your API key when prompted
fabric --setup
```

**Per-video workflow (~30 seconds):**

```bash
# Full structured extraction with timestamps
fabric -y "https://www.youtube.com/watch?v=VIDEO_ID" \
  --transcript-with-timestamps \
  --pattern extract_wisdom \
  --stream \
  -o ~/notes/video-name.md

# Alternative: just the raw transcript (for custom processing)
fabric -y "URL" --transcript-with-timestamps > transcript.txt

# Alternative: pipe to Claude Code for custom analysis
fabric -y "URL" --transcript-with-timestamps | claude --print "Produce a minute-by-minute breakdown of this transcript. For each segment, list: timestamp range, key claim or demo step, any code/commands mentioned, and whether this is opinion or fact."
```

**What extract_wisdom produces:**

- SUMMARY (2-3 paragraphs)
- IDEAS (bulleted, with original phrasing)
- INSIGHTS (synthesized from ideas)
- QUOTES (verbatim notable quotes)
- HABITS (actionable practices mentioned)
- FACTS (verifiable claims)
- REFERENCES (papers, tools, links mentioned)
- ONE-SENTENCE TAKEAWAY
- RECOMMENDATIONS

**Other useful patterns:**

- `summarize` -- shorter, more traditional summary
- `analyze_claims` -- fact-checks claims made in the video
- `create_study_notes` -- educational format
- `extract_concepts` -- pulls terminology and definitions
- `extract_action_items` -- tasks and next steps

**Time per 60-min video:** ~30 seconds for transcript pull + LLM processing
**Cost per 60-min video:** A 60-min video at ~150 WPM = ~9,000 words = ~12,000 tokens input. With Claude Sonnet 4.6 ($3/M input, $15/M output), assuming ~3,000 tokens output: $0.036 input + $0.045 output = ~$0.08 per video. With Gemini 2.5 Flash ($0.15/M input): ~$0.004. Effectively free.

### Secondary: Twitter/X Video Workflow

```bash
# 1. Download the video
yt-dlp -o "%(title)s.%(ext)s" "https://x.com/user/status/123456789"

# 2. Extract audio
ffmpeg -i video.mp4 -vn -acodec pcm_s16le -ar 16000 audio.wav

# 3. Transcribe locally with whisper.cpp
./main -m models/ggml-medium.bin -f audio.wav --output-txt

# 4. Summarize
cat audio.txt | fabric --pattern extract_wisdom --stream
```

**Or, one-liner if you have Fabric + Whisper set up:**

```bash
yt-dlp -o "/tmp/xvideo.mp4" "TWITTER_URL" && \
ffmpeg -i /tmp/xvideo.mp4 -vn -ar 16000 /tmp/xaudio.wav -y && \
whisper /tmp/xaudio.wav --model medium --output_format txt && \
cat /tmp/xaudio.txt | fabric --pattern extract_wisdom --stream
```

**Time:** ~2-5 min (download + local transcription + LLM)
**Cost:** Free if using local Whisper + local Ollama, or ~$0.02 with Claude API.

---

## Per-Tool Deep Dive

### Layer 1: Transcript Extraction

#### yt-dlp (CLI)

- **What:** Open-source CLI that downloads videos and subtitles from YouTube (and 1000+ other sites including Twitter/X).
- **Cost:** Free, open-source.
- **Granularity:** Extracts the raw caption track (VTT/SRT format) with full timestamps. Not summarized — this is the raw material.
- **Key commands:**
  - `yt-dlp --write-auto-sub --sub-lang en --skip-download --convert-subs srt URL` (auto-generated captions)
  - `yt-dlp --write-sub --sub-lang en --skip-download URL` (manual/creator captions)
  - Prefers manual subs over auto-generated when both exist.
- **Failure modes:** Some videos have no captions at all. Auto-generated captions have ~85-95% accuracy for clear English, dropping to ~78-82% for noisy audio or heavy accents. No punctuation/capitalization in auto-captions.
- **Best fit:** Foundation layer. Every other tool either uses this under the hood or should.
- **Source:** [yt-dlp GitHub][1] `[T1 — primary source, open-source project]`

#### youtube-transcript-api (Python library)

- **What:** Python library that pulls YouTube transcripts without needing an API key or headless browser. Returns structured data with text + start time + duration per segment.
- **Cost:** Free, open-source. v1.2.4 (Jan 2026).
- **Granularity:** Each transcript segment is a dict with `text`, `start` (seconds), `duration`. Typically 3-10 second segments.
- **Key usage:**
  ```python
  from youtube_transcript_api import YouTubeTranscriptApi
  api = YouTubeTranscriptApi()
  transcript = api.fetch("VIDEO_ID")
  for snippet in transcript:
      print(f"[{snippet.start:.0f}s] {snippet.text}")
  ```
- **Failure modes:** YouTube aggressively rate-limits and blocks cloud IPs. Some videos have no transcripts. Age-restricted video support is broken as of early 2026.
- **Best fit:** Custom Python scripts, Claude Code skills, automated pipelines.
- **Source:** [PyPI page][2] `[T1]`, [GitHub repo][3] `[T1]`

#### YouTube "Show Transcript" (browser, manual)

- **What:** YouTube's built-in transcript viewer. Click `...` > `Show transcript` under any video.
- **Cost:** Free.
- **Granularity:** Full timestamped transcript, segmented roughly by sentence. Copy-pasteable.
- **Failure modes:** Only works if video has captions (auto or manual). Cannot export programmatically. Tedious for long videos.
- **Best fit:** Quick one-off when you don't want to install anything.
- **Source:** Direct observation `[T1 — first-party platform feature]`

### Layer 2: AI Summarization Tools

#### Fabric (CLI, open-source)

- **What:** Open-source framework by Daniel Miessler. 140+ "patterns" (structured prompts) for specific tasks. Built-in YouTube transcript extraction via yt-dlp. Pipes to any LLM (Claude, GPT, Gemini, Ollama).
- **Cost:** Free (you pay for the LLM API calls, or free with local Ollama).
- **Granularity:** EXCELLENT. The `extract_wisdom` pattern produces Ideas, Insights, Quotes, Habits, Facts, References, Recommendations — all structured. The `--transcript-with-timestamps` flag preserves time references. You can create custom patterns for even more granular output.
- **Installation:** `go install github.com/danielmiessler/fabric@latest`
- **Failure modes:** Requires Go installed. The `yt` helper command has had bugs in some versions (see GitHub issues #947, #529). Depends on yt-dlp for YouTube access, so inherits its rate-limiting issues.
- **Best fit:** THE recommended tool for Kartavya's use case. CLI-native, scriptable, customizable, works with Claude.
- **Source:** [Fabric GitHub][4] `[T1]`, [Fabric YouTube Processing docs][5] `[T1]`, [Major Hayden blog][6] `[T3 — practitioner blog]`

#### Glasp YouTube Summary Extension (browser)

- **What:** Chrome/Safari/Edge extension. Shows transcript sidebar on YouTube with timestamps. One-click copy transcript. Summarize via ChatGPT, Claude, Gemini, or Mistral.
- **Cost:** Free for desktop (unlimited YouTube summaries). Pro $8.99/mo adds mobile + PDF summaries.
- **Granularity:** GOOD. Shows full transcript with timestamps. Summary granularity depends on which LLM you route to and how you prompt it. The extension itself is more of a transcript-access + LLM-routing layer.
- **Failure modes:** Depends on video having captions. Extension needs updating when YouTube UI changes. Data goes to external AI providers.
- **Best fit:** Quick browser-based workflow when you don't want CLI. Good complement to Fabric.
- **Source:** [Glasp website][7] `[T4 — vendor]`, [Chrome Web Store][8] `[T3]`, [Ekamoira comparison][9] `[T2]`

#### NotebookLM (Google, web app)

- **What:** Google's AI research tool. Paste YouTube URLs as sources, ask questions across multiple videos. Generates structured summaries, podcast-style audio overviews.
- **Cost:** Free.
- **Granularity:** MODERATE-to-GOOD. Not minute-by-minute, but synthesizes across sources well. Best for deep research across multiple videos, not for granular single-video extraction.
- **Failure modes:** Setup overhead (5-10 min to configure a notebook). Not quick for "I just want to skim this one video." Video must be public and >1 day old. No CLI/API.
- **Best fit:** When you have 5-10 videos on a topic and want to cross-reference them. Not for the quick-skim use case.
- **Source:** [Futurepedia course][10] `[T3]`, [Ekamoira comparison][9] `[T2]`

#### Eightify (Chrome extension)

- **What:** Chrome extension that adds a "Key Takeaways" button to YouTube. Produces 8 key points with timestamps.
- **Cost:** 7-day free trial, then paid (pricing varies, reported ~$4.99-9.99/mo). [T4 — pricing hard to verify; vendor doesn't list it clearly]
- **Granularity:** LOW-MODERATE. Designed for "8 key takeaways" — a TL;DR summarizer, NOT a granular breakdown. Timestamps help but the output is deliberately compressed.
- **Failure modes:** Free trial only. The "8 key points" format forces compression that loses nuance. Vendor-controlled — you can't customize the prompt.
- **Best fit:** Quick "is this video worth watching?" filter. NOT for "I need to know everything."
- **Source:** [Chrome Web Store][11] `[T3]`, [Ekamoira comparison][9] `[T2]`

#### NoteGPT (web + Chrome extension)

- **What:** AI summarizer with mind maps, flashcards, slides. Claims to handle videos up to 150 minutes even without subtitles.
- **Cost:** 15 free quotas/month. Pro $9/mo for 1,000 quotas.
- **Granularity:** MODERATE. Produces transcript view with timestamps + summary + mind map. Stronger on study-tool integration than raw extraction depth.
- **Failure modes:** Only 15 free uses/month (not enough for heavy use). Trustpilot rating is 2.3/5 with complaints about quota consumption and billing. Vendor-controlled output format.
- **Best fit:** Students who want flashcards/mind maps. NOT for Kartavya's use case (too few free uses, not CLI-able).
- **Source:** [NoteGPT website][12] `[T4 — vendor]`, [Ekamoira review][13] `[T2]`

#### Summarize.tech (web)

- **What:** Paste YouTube URL, get instant summary. No registration.
- **Cost:** Free (limited daily). Premium $10/mo for unlimited.
- **Granularity:** LOW-MODERATE. Provides section-by-section breakdown but not minute-by-minute. Designed for quick gisting.
- **Failure modes:** Accuracy varies with content complexity. Struggles with heavily visual content. Free tier has daily limits.
- **Best fit:** Zero-effort quick check. Not for deep extraction.
- **Source:** [Summarize.tech review (Skywork)][14] `[T3]`, [Nextool review][15] `[T3]`

### Layer 3: Local Transcription (Whisper variants)

#### whisper.cpp / MLX-Whisper (local, Mac-native)

- **What:** C/C++ port of OpenAI's Whisper model, optimized for Apple Silicon. MLX-Whisper is the Apple MLX framework variant (~30-40% faster than whisper.cpp on Apple Silicon).
- **Cost:** Free, fully local, no API calls.
- **Models and performance on Apple Silicon:**

  | Model          | Params | RAM    | Speed (Apple Silicon) | Accuracy                        |
  | -------------- | ------ | ------ | --------------------- | ------------------------------- |
  | tiny           | 39M    | ~1 GB  | ~32x realtime         | Draft quality                   |
  | base           | 74M    | ~1 GB  | ~16x realtime         | Basic, ok for clear speech      |
  | small          | 244M   | ~2 GB  | ~6x realtime          | Good for most content           |
  | medium         | 769M   | ~5 GB  | ~2x realtime          | Professional grade              |
  | large-v3       | 1.5B   | ~10 GB | ~1x realtime          | Maximum precision               |
  | large-v3-turbo | 809M   | ~6 GB  | ~10x realtime         | Near-large quality, much faster |

- **For a 60-min video with medium model on M-series Mac:** ~30 minutes transcription time. With large-v3-turbo: ~6 minutes.
- **Installation:**
  ```bash
  # whisper.cpp
  brew install whisper-cpp
  # Or build from source with Metal:
  git clone https://github.com/ggerganov/whisper.cpp
  cd whisper.cpp && WHISPER_METAL=1 make -j
  bash ./models/download-ggml-model.sh medium
  ```
- **When to use:** When YouTube has no captions (rare), when you need higher accuracy than auto-captions, for Twitter/X videos (no native captions), for any non-YouTube video source.
- **Failure modes:** Slow on large-v3 for long videos. Requires model download (medium = ~1.5 GB). Can hallucinate on silent segments (a known Whisper issue — generates phantom text during silence).
- **Source:** [whisper.cpp GitHub][16] `[T1]`, [Simon Willison TIL][17] `[T3 — expert practitioner]`, [Vocoding guide][18] `[T3]`, [Mac whisper speedtest][19] `[T3]`

#### MacWhisper (macOS GUI app)

- **What:** Native macOS app wrapping Whisper models. Drag-and-drop video/audio files, or paste YouTube URLs directly.
- **Cost:** Free (tiny/base/small models). Pro $69 lifetime (medium/large models + speaker identification).
- **Granularity:** Full timestamped transcript. Export as plain text, SRT, VTT. Speaker identification in Pro.
- **When to use:** If you want a GUI instead of CLI. The YouTube URL paste feature is convenient.
- **Failure modes:** Pro needed for the good models. No LLM summarization built in — you'd still need to pipe the output somewhere.
- **Source:** [MacWhisper website][20] `[T4 — vendor]`, [Australian Apple News review][21] `[T2]`, [Getvoibe pricing comparison][22] `[T3]`

### Layer 4: Multimodal Extraction (Transcript + Visual)

#### claude-video-vision (Claude Code plugin)

- **What:** Claude Code plugin that extracts video frames via ffmpeg + audio via Whisper/Gemini/OpenAI, then sends both to Claude for multimodal analysis. Claude sees the actual frames AND reads the transcript.
- **Cost:** Free (plugin). You pay for the LLM calls. Gemini backend has 1,500 free requests/day.
- **Installation:**
  ```
  /plugin marketplace add https://github.com/jordanrendric/claude-video-vision
  /setup-video-vision
  ```
- **Granularity:** HIGHEST. This is the only tool that combines transcript + visual frame analysis. Claude can see code on screen, read slides, identify UI elements.
- **Usage:** `/watch-video URL "extract all code snippets and commands shown on screen"` or conversationally ask Claude about a video.
- **Failure modes:** Token-expensive (frames are large). Processing time scales with video length. Relatively new (v1.0.0). Requires ffmpeg + yt-dlp.
- **Best fit:** When the video is a coding demo or slide-heavy talk where on-screen content matters as much as narration. The nuclear option for "I need everything."
- **Source:** [GitHub repo][23] `[T1]`, [Claude Vision docs][24] `[T1 — vendor, but authoritative for capability claims]`

#### Gemini Video Understanding (API)

- **What:** Google's Gemini models can process video directly — paste a YouTube URL and ask questions. Understands visual content, not just transcript.
- **Cost:** Gemini 2.5 Flash free tier: 1,500 requests/day, 250K tokens/min. Paid: $0.15/$0.60 per million tokens.
- **Granularity:** GOOD for summarization, MODERATE for verbatim extraction. Gemini summarizes meaning rather than transcribing word-for-word.
- **Failure modes:** Cannot produce verbatim transcript. Only public YouTube videos. One video per request. May miss rapid visual transitions.
- **Best fit:** When you want "what is shown on screen at 14:32?" type queries, or visual content analysis. Not for complete extraction.
- **Source:** [Google Cloud docs][25] `[T1]`, [Vomo.ai test][26] `[T3]`

#### ffmpeg + OCR pipeline (DIY)

- **What:** Extract keyframes from video with ffmpeg, then OCR them with Tesseract or Apple Vision framework.
- **Cost:** Free.
- **Commands:**

  ```bash
  # Extract 1 frame per second
  ffmpeg -i video.mp4 -vf "fps=1" frames/frame_%04d.png

  # Extract only keyframes (I-frames, scene changes)
  ffmpeg -i video.mp4 -vf "select=eq(pict_type\,I)" -vsync vfr keyframes/kf_%04d.png

  # OCR with macOS Vision framework (via ocrmac Python wrapper)
  pip install ocrmac
  python -c "from ocrmac import ocrmac; print(ocrmac.OCR('frame_0001.png').recognize())"
  ```

- **Granularity:** Gets on-screen text, slides, code. Combined with transcript, gives full picture.
- **Failure modes:** Noisy frames produce bad OCR. Small text on busy backgrounds fails. Manual pipeline — needs scripting to be useful. Many frames will be duplicates or transitions.
- **Best fit:** When you specifically need to extract code or slide text that the speaker doesn't read aloud.
- **Source:** [FFmpeg docs / GitHub gist][27] `[T1]`, [ocrmac GitHub][28] `[T1]`, [Herostrat.us blog on OCR from coding videos][29] `[T3 — expert practitioner]`

### Layer 5: Twitter/X Specific

#### yt-dlp on Twitter URLs

- **What:** yt-dlp handles Twitter/X video downloads natively.
- **Usage:** `yt-dlp -o "output.mp4" "https://x.com/user/status/12345"`
- **Cost:** Free.
- **Limitations:** May need cookies for some content. Twitter Spaces are a separate path.
- **Source:** [yt-dlp Twitter extractor source][30] `[T1]`, [Venkatarangan blog][31] `[T3]`

#### twspace-dl / TwSpaceTool / SpacesDown

- **What:** Tools specifically for Twitter Spaces (live audio events, often 1-3 hours).
- **twspace-dl:** Python CLI, requires cookies since July 2023 API changes. `[T1 — GitHub][32]`
- **TwSpaceTool:** Chrome extension, free download + 120 free minutes of transcription + summarization. `[T3 — Chrome Web Store]`
- **SpacesDown:** Web tool, 5 free downloads/day with MP3 conversion. `[T3 — vendor]`
- **Best fit:** twspace-dl for CLI scripting, TwSpaceTool for quick browser use.

---

## Comparison Table

| Tool                       | Granularity                              | Cost                     | Speed (60-min) | Handles 1hr+  | Twitter/X            | CLI-able        | Scriptable | Visual Extraction |
| -------------------------- | ---------------------------------------- | ------------------------ | -------------- | ------------- | -------------------- | --------------- | ---------- | ----------------- |
| **Fabric**                 | Excellent (structured patterns)          | Free + LLM cost (~$0.08) | ~30 sec        | Yes           | No (manual pipeline) | YES             | YES        | No                |
| **Glasp**                  | Good (full transcript + LLM summary)     | Free                     | ~10 sec        | Yes           | No                   | No              | No         | No                |
| **youtube-transcript-api** | Raw (segments + timestamps)              | Free                     | ~5 sec         | Yes           | No                   | YES (CLI mode)  | YES        | No                |
| **yt-dlp**                 | Raw (caption tracks)                     | Free                     | ~5 sec         | Yes           | YES                  | YES             | YES        | No                |
| **NotebookLM**             | Moderate (cross-source synthesis)        | Free                     | ~60 sec        | Yes           | No                   | No              | No         | No                |
| **Eightify**               | Low (8 key points)                       | Paid after trial         | ~10 sec        | Yes           | No                   | No              | No         | No                |
| **NoteGPT**                | Moderate (notes + mind map)              | 15 free/month            | ~15 sec        | Yes (150 min) | No                   | No              | No         | No                |
| **Summarize.tech**         | Low-Moderate (sections)                  | Free (limited)           | ~10 sec        | Yes           | No                   | No              | No         | No                |
| **whisper.cpp (local)**    | Raw (full transcript)                    | Free                     | ~6-30 min      | Yes (chunk)   | YES (any file)       | YES             | YES        | No                |
| **MacWhisper**             | Raw (full transcript)                    | Free / $69 Pro           | ~5 min (M4)    | Yes           | YES (any file)       | No              | No         | No                |
| **claude-video-vision**    | Highest (frames + transcript + analysis) | Free + LLM cost          | ~2-5 min       | Partial       | Yes (local files)    | YES (CC plugin) | YES        | YES               |
| **Gemini API**             | Good (multimodal summary)                | Free tier generous       | ~30 sec        | Yes (2hr max) | No                   | YES (API)       | YES        | YES               |
| **ffmpeg + OCR**           | Visual only (on-screen text)             | Free                     | ~5-10 min      | Yes           | YES (any file)       | YES             | YES        | YES (only)        |

---

## Workflows for Different Use Cases

### Workflow A: "Fast Skim" (~2 min, free)

**Scenario:** "Is this 45-min video worth my time?"

```bash
fabric -y "URL" --pattern summarize --stream
```

Produces a 200-word summary. Read in 60 seconds. Decide whether to go deeper.

**Alternative (no CLI):** Install Glasp extension. Go to the YouTube page. Click "View AI Summary." Done.

### Workflow B: "Must Understand Every Claim" (~5 min, ~$0.08)

**Scenario:** "This is a 90-min talk on agentic frameworks. I need to know every tool mentioned, every architecture claim, every opinion stated."

```bash
# Step 1: Full extraction
fabric -y "URL" --transcript-with-timestamps --pattern extract_wisdom -o raw_wisdom.md

# Step 2: Follow up with claim analysis
fabric -y "URL" --transcript-with-timestamps --pattern analyze_claims -o claims.md

# Step 3 (optional): Custom deep-dive
fabric -y "URL" --transcript-with-timestamps | claude --print "
For this transcript, produce:
1. TIMELINE: For every 5-minute block, one sentence on what was covered
2. TOOLS MENTIONED: Every tool, library, framework, with timestamp and what was said about it
3. CLAIMS: Every factual claim made, with timestamp and whether it's verifiable
4. OPINIONS: Every opinion or prediction, with timestamp
5. DEMOS: Every demo step or command shown, in order
"
```

### Workflow C: "Extract Code from Demo" (~10 min, ~$0.15)

**Scenario:** "This is a Claude Code tutorial. I need every command, every config file, every terminal output."

```bash
# Step 1: Get transcript
fabric -y "URL" --transcript-with-timestamps > transcript.txt

# Step 2: Extract keyframes (code is usually on screen)
yt-dlp -o /tmp/demo.mp4 "URL"
ffmpeg -i /tmp/demo.mp4 -vf "fps=0.5" /tmp/frames/frame_%04d.png

# Step 3: OCR the frames (macOS native)
pip install ocrmac
python3 -c "
import os, glob
from ocrmac import ocrmac
for f in sorted(glob.glob('/tmp/frames/*.png')):
    result = ocrmac.OCR(f).recognize()
    if result:
        print(f'--- {os.path.basename(f)} ---')
        for text, confidence, bbox in result:
            if confidence > 0.5:
                print(text)
"

# Step 4: Or use claude-video-vision for the nuclear option
# (inside Claude Code)
/watch-video "URL" "Extract every terminal command, code snippet, config file, and file path shown on screen. Present them in execution order with timestamps."
```

### Workflow D: "Twitter Thread + Video" (~5 min, ~$0.02)

**Scenario:** Someone posted a 5-min video in a Twitter thread with important context in the tweets.

```bash
# Step 1: Download video
yt-dlp -o /tmp/xvid.mp4 "https://x.com/user/status/ID"

# Step 2: Transcribe locally
ffmpeg -i /tmp/xvid.mp4 -vn -ar 16000 /tmp/xaudio.wav -y
whisper /tmp/xaudio.wav --model medium --output_format txt --output_dir /tmp/

# Step 3: Get the thread text (manual or via API)
# Copy thread text into thread.txt

# Step 4: Combine and analyze
cat /tmp/xaudio.txt thread.txt | fabric --pattern extract_wisdom --stream
```

### Workflow E: "Twitter Spaces" (~10 min, free)

```bash
# If live or recently archived:
twspace-dl -i SPACE_URL -o space.m4a

# Convert and transcribe
ffmpeg -i space.m4a -ar 16000 space.wav
whisper space.wav --model medium --output_format txt

# Summarize
cat space.txt | fabric --pattern meeting_summary --stream
```

**Alternative:** Use TwSpaceTool Chrome extension (120 free minutes, includes transcription + summary).

---

## Source Bibliography

```
[1]  yt-dlp — yt-dlp contributors, ongoing — [T1]
     https://github.com/yt-dlp/yt-dlp
     Why: Primary open-source project. All capability claims verified against repo.

[2]  youtube-transcript-api — PyPI, Jan 2026 (v1.2.4) — [T1]
     https://pypi.org/project/youtube-transcript-api/
     Why: Authoritative package registry listing.

[3]  youtube-transcript-api — jdepoix, GitHub — [T1]
     https://github.com/jdepoix/youtube-transcript-api
     Why: Primary source code and documentation.

[4]  Fabric — Daniel Miessler, GitHub, ongoing — [T1]
     https://github.com/danielmiessler/fabric
     Why: Primary project repo. 30k+ stars.

[5]  Fabric YouTube Processing docs — Daniel Miessler — [T1]
     https://github.com/danielmiessler/Fabric/blob/main/docs/YouTube-Processing.md
     Why: Official documentation for YouTube-specific features.

[6]  "Summarize YouTube videos with Fabric" — Major Hayden, 2024 — [T3]
     https://major.io/p/summarize-youtube-videos-fabric/
     Why: Independent practitioner walkthrough confirming Fabric capabilities.

[7]  Glasp YouTube Summary — Glasp, ongoing — [T4 — vendor]
     https://glasp.co/youtube-summary
     Why: Vendor page. Claims cross-checked against Chrome Web Store listing.

[8]  YouTube Summary & ChatGPT by Glasp — Chrome Web Store — [T3]
     https://chromewebstore.google.com/detail/cdjifpfganmhoojfclednjdnnpooaojb
     Why: Independent distribution platform with user counts and reviews.

[9]  "Can ChatGPT Summarize YouTube Videos? 4 Methods Compared" — Ekamoira, 2026 — [T2]
     https://www.ekamoira.com/blog/chatgpt-summarize-youtube-videos
     Why: Independent comparison with tested methodology and specific data.

[10] NotebookLM course — Futurepedia, 2025 — [T3]
     https://www.futurepedia.io/courses/google-notebooklm-complete-course/lessons/analyzing-and-summarize-youtube-videos
     Why: Independent educational content on NotebookLM capabilities.

[11] Eightify — Chrome Web Store — [T3]
     https://chromewebstore.google.com/detail/cdcpabkolgalpgeingbdcebojebfelgb
     Why: Distribution platform listing with independent ratings.

[12] NoteGPT — notegpt.io — [T4 — vendor]
     https://notegpt.io/youtube-video-summarizer
     Why: Vendor page. Pricing verified. Trustpilot rating cross-checked.

[13] "NoteGPT YouTube Summarizer: Complete Guide" — Ekamoira, 2026 — [T2]
     https://www.ekamoira.com/blog/notegpt-youtube-summarizer-complete-guide-to-features-limits-better-alternatives-2026
     Why: Independent review covering limitations and alternatives.

[14] "Summarize.tech Review" — Skywork AI, 2025 — [T3]
     https://skywork.ai/skypage/en/Summarize.tech-Review:-The-AI-Video-Companion-I-Actually-Use/1976478652303470592
     Why: Independent user review.

[15] Summarize.tech — Nextool review — [T3]
     https://www.nextool.ai/tools/summarize-tech/
     Why: Independent tool review platform.

[16] whisper.cpp — ggml-org, GitHub, ongoing — [T1]
     https://github.com/ggml-org/whisper.cpp
     Why: Primary project repo. Benchmark data from source.

[17] "Transcribing MP3s with whisper-cpp on macOS" — Simon Willison, 2024 — [T3 — expert practitioner]
     https://til.simonwillison.net/macos/whisper-cpp
     Why: Simon Willison is a respected developer. Practical walkthrough.

[18] "Whisper Local Transcription Guide" — Vocoding, Apr 2026 — [T3]
     https://vocoding.com/blog/whisper-local-transcription-guide
     Why: Detailed model comparison with benchmarks.

[19] mac-whisper-speedtest — GitHub — [T3]
     https://github.com/anvanvan/mac-whisper-speedtest
     Why: Comparative benchmarks across Whisper implementations on Apple Silicon.

[20] MacWhisper — macwhisper.net — [T4 — vendor]
     https://macwhisper.net/
     Why: Vendor page. Pricing verified against Gumroad listing.

[21] "MacWhisper delivers on-device transcription" — Australian Apple News, Jun 2025 — [T2]
     https://australianapplenews.com/2025/06/16/review-macwhisper-delivers-on-device-transcription-without-subscription-fees/
     Why: Independent editorial review.

[22] MacWhisper pricing comparison — Getvoibe, 2026 — [T3]
     https://www.getvoibe.com/resources/macwhisper-pricing/
     Why: Independent pricing comparison.

[23] claude-video-vision — jordanrendric, GitHub — [T1]
     https://github.com/jordanrendric/claude-video-vision
     Why: Primary project repo. Capability claims verified against source.

[24] Claude Vision docs — Anthropic — [T1]
     https://platform.claude.com/docs/en/build-with-claude/vision
     Why: Official documentation for Claude's vision capabilities.

[25] "Video understanding" — Google Cloud docs — [T1]
     https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/video-understanding
     Why: Official Google documentation.

[26] "Can Gemini Transcribe YouTube Videos?" — Vomo.ai, 2026 — [T3]
     https://vomo.ai/blog/can-gemini-transcribe-youtube-videos
     Why: Independent testing of Gemini's actual capabilities vs claims.

[27] ffmpeg keyframe extraction — GitHub gist (savvot) — [T1]
     https://gist.github.com/savvot/9e4316dc68f6111f7b1f
     Why: Verified ffmpeg commands.

[28] ocrmac — straussmaximilian, GitHub — [T1]
     https://github.com/straussmaximilian/ocrmac
     Why: Open-source wrapper for Apple Vision framework OCR.

[29] "Labelling Coding Videos Using Tesseract OCR" — Kay Lack, Herostrat.us — [T3 — expert practitioner]
     https://www.herostrat.us/posts/labelling-coding-videos-using-tesseract/
     Why: Specific practical experience with OCR on coding video frames.

[30] yt-dlp Twitter extractor — GitHub source — [T1]
     https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/extractor/twitter.py
     Why: Primary source code.

[31] "How to download videos from Twitter using yt-dlp" — Venkatarangan, Oct 2023 — [T3]
     https://venkatarangan.com/blog/2023/10/download-videos-from-twitter-x/
     Why: Practitioner walkthrough.

[32] twspace-dl — HoloArchivists, GitHub — [T1]
     https://github.com/HoloArchivists/twspace-dl
     Why: Primary project repo.

[33] "YouTube auto-generated captions accuracy" — NoteLM.ai, 2026 — [T3]
     https://www.notelm.ai/blog/youtube-auto-captions-transcript
     Why: Testing data on caption accuracy ranges.

[34] "Hallucination Rates in 2025" — Medium (Markus Brinsa), 2025 — [T3]
     https://medium.com/@markus_brinsa/hallucination-rates-in-2025-accuracy-refusal-and-liability-aa0032019ca1
     Why: Aggregated hallucination rate data.

[35] "A hallucination detection framework for faithful text summarization" — Scientific Reports (Nature), 2025 — [T1]
     https://www.nature.com/articles/s41598-025-31075-1
     Why: Peer-reviewed research on summarization hallucination.

[36] Claude API Pricing — Anthropic, 2026 — [T1]
     https://platform.claude.com/docs/en/about-claude/pricing
     Why: Official pricing page.

[37] Gemini API Pricing — Google, 2026 — [T1]
     https://ai.google.dev/gemini-api/docs/pricing
     Why: Official pricing page.
```

---

## Confidence Assessment

**Strong evidence (multiple independent sources converge):**

- yt-dlp reliably extracts YouTube captions and Twitter videos
- youtube-transcript-api works for most public videos with captions
- Whisper medium/large-v3-turbo on Apple Silicon is fast enough for practical use
- YouTube auto-captions are 85-95% accurate for clear English
- Fabric's extract_wisdom pattern produces structured, granular output
- AI summarizers hallucinate — this is an inherent limitation, not a fixable bug

**Convergent reporting (2-3 independent sources):**

- Glasp is the best free browser extension for transcript access
- NotebookLM is better for multi-source research than single-video extraction
- Whisper outperforms YouTube auto-captions on accuracy, especially with accents
- claude-video-vision is the most capable multimodal extraction tool for Claude Code users

**Single source / contested:**

- MLX-Whisper being 30-40% faster than whisper.cpp — reported by one benchmark set `[T3]`, not independently replicated at scale
- Eightify handling "up to 10 hours" — vendor claim `[T4]`, untested by independent source
- NoteGPT handling "150 minutes without subtitles" — vendor claim `[T4]`

**Speculative:**

- Token cost estimates are based on average speaking rates (~150 WPM = ~9,000 words/hr = ~12,000 tokens). Actual costs vary with content density and output length.

---

## Honest Limitations Section

### What the workflow CANNOT do well

1. **Heavily visual demos with little narration.** If a coding tutorial shows code on screen but the speaker says "and then I do this... and this... okay, that works," the transcript is useless. You MUST use the multimodal path (claude-video-vision or ffmpeg+OCR). This adds 5-10 minutes and significant cost.

2. **Heavy accents, multiple speakers, crosstalk.** YouTube auto-captions and Whisper both degrade. For multi-speaker content, accuracy drops to 60-80%. Speaker identification is an add-on (MacWhisper Pro, or Whisper + pyannote).

3. **Music, sound effects, ambient noise.** Whisper may hallucinate text during non-speech segments — a documented and unresolved issue. It generates phantom words or repeated phrases when processing silence or music.

4. **Videos with no captions AND no audio.** Pure screencasts with no narration. Only the ffmpeg+OCR path works, and it's slow.

5. **Paywalled or private videos.** yt-dlp can sometimes work with browser cookies (`--cookies-from-browser chrome`), but this is fragile and may violate ToS.

6. **AI summarizer hallucination.** All LLM-based summarizers can fabricate details that sound plausible but aren't in the source. A 2025 Nature-published study found summarization hallucination persists even when models have the source text `[35, T1]`. Reasoning models (GPT-5, Claude Sonnet) have HIGHER hallucination rates on grounded summarization tasks (>10%) than simpler models `[34, T3]`. **Mitigation:** Always keep the raw transcript alongside the summary. Use the summary for navigation, the transcript for verification.

7. **Nuance loss.** Every summarizer compresses. The speaker's tone, hesitation, emphasis, humor, sarcasm — all lost in text. The speaker's "I'm not sure about this, but..." becomes "The speaker stated X." This is structurally unfixable in text extraction.

8. **Token costs for very long videos.** A 90-min video generates ~13,500 words = ~18,000 tokens. Sending this to Claude Opus 4.7 ($5/M input) costs ~$0.09 for input alone. If you ask for detailed output (~5,000 tokens), add ~$0.13 output. Total ~$0.22. Not expensive for one video, but at 10 videos/day = ~$2.20/day = ~$66/month. Using Gemini 2.5 Flash ($0.15/$0.60 per M tokens) instead: ~$0.006/video. Use the cheaper model for extraction, the expensive model for questions you care about.

9. **YouTube rate limiting.** Both yt-dlp and youtube-transcript-api hit YouTube rate limits at scale. If you're processing >20 videos/day, expect HTTP 429 errors. Mitigations: add `--sleep-requests 2` to yt-dlp, use residential proxies, or use browser cookies.

10. **Twitter/X is harder than YouTube.** No native captions. Must download + Whisper. The workflow is 3-5 steps instead of 1. For Twitter Spaces, twspace-dl requires auth cookies since July 2023.

### Quality comparison: YouTube auto-captions vs Whisper re-transcription

| Factor                  | YouTube Auto-Captions       | Whisper (medium)          |
| ----------------------- | --------------------------- | ------------------------- |
| Accuracy (clear speech) | 85-95% `[33, T3]`           | 92-97% `[T3, aggregated]` |
| Punctuation             | No                          | Yes                       |
| Capitalization          | No                          | Yes                       |
| Speaker labels          | No                          | No (add-on needed)        |
| Handles accents         | Moderate                    | Better                    |
| Speed                   | Instant (already generated) | 2-30 min for 1hr          |
| Cost                    | Free                        | Free (local)              |
| Availability            | Only if video has captions  | Any audio/video file      |

**Verdict:** Use YouTube auto-captions when available (instant, free, good enough). Fall back to Whisper when captions are missing, when accuracy matters, or for non-YouTube sources.

---

## Gaps & Open Questions

1. **No single tool does everything.** Transcript + visual + summary in one step doesn't exist outside of claude-video-vision (which is new and hasn't been battle-tested at scale).

2. **Eightify's actual paid pricing is opaque.** The Chrome Web Store and vendor pages don't clearly state pricing after the trial. Multiple sources give different numbers. Treat with caution.

3. **claude-video-vision is v1.0.0.** It works on macOS Apple Silicon (tested per the repo), but long-term stability, Windows/Linux support, and behavior on very long videos are uncharted.

4. **No good end-to-end Twitter video summarizer exists.** Every approach requires stitching together download + transcription + summarization manually. The best path is yt-dlp + Whisper + Fabric, but it's 3-4 commands.

5. **Whisper hallucination on silence** is a known issue with no clean fix. The common workaround is silence detection + segment filtering, which adds complexity.

6. **Token cost estimates are approximate.** The actual token count depends on the specific tokenizer (Claude's new Opus 4.7 tokenizer generates ~35% more tokens for the same text than older models). Real costs could be 20-40% higher than estimated.

---

## Suggested Next Steps

1. **Build a Claude Code slash command / skill** that wraps the Fabric pipeline: `/skim URL` = `fabric -y URL --transcript-with-timestamps --pattern extract_wisdom --stream`. Wire it into the Claude Code session so it's one command away. Consider adding a custom pattern that matches Kartavya's exact output needs (minute-by-minute timeline + claims + tools mentioned).

2. **Test on 3 specific videos** — pick one clean podcast-style talk, one coding demo, and one multi-speaker panel. Compare Fabric's extract_wisdom output quality across them. This will reveal where the workflow breaks and where visual extraction is needed.

3. **Set up local Whisper for Twitter.** `brew install whisper-cpp` + download the medium model. This makes the Twitter/X workflow self-contained and free.

4. **Evaluate Gemini 2.5 Flash as the LLM backend** instead of Claude for routine extraction. At $0.15/M input tokens vs Claude Sonnet's $3/M, it's 20x cheaper for a task where you're mostly reformatting rather than reasoning. Reserve Claude for the "analyze claims" and "deep reasoning" passes.
