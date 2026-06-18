#!/usr/bin/env python3
# Helper: build a Gemini API request body from a video item JSON file.
# Called by video-analyze-batch.sh per video.
#
# Usage:
#   python3 build-gemini-request.py <item_tmp_path>
#
# Output: JSON request body printed to stdout.
#
# Note: this analyzes text-only (caption + hashtags + metadata).
# Gemini's free tier blocks direct video URL input (limit: 0 on
# generate_content_free_tier with fileData), so we work from the
# textual signal TikTok exposes. Hook DESCRIPTION (visual) is replaced
# with hook_description_inferred (what the caption suggests is happening).

import json, sys

if len(sys.argv) != 2:
    print(json.dumps({"error": "usage: build-gemini-request.py <item_tmp>"}))
    sys.exit(1)

item = json.load(open(sys.argv[1]))
video = item["video"]

prompt = f"""You are analyzing a TikTok video for competitive intelligence on US supplement brands. You're working from the caption + hashtags + metadata only (no visual access). Be honest when a field can't be reliably inferred from text — say "unclear" rather than guessing.

Caption: {video.get('caption', '')[:800]}
Hashtags: {', '.join(['#' + str(h) for h in video.get('hashtags', [])])}
Duration: {video.get('duration_seconds', 0)}s
Views: {video.get('views', 0)}
Author handle: @{video.get('author_handle', '')}
Source: {video.get('source', '')}={video.get('source_value', '')}

Return STRICT JSON with these exact keys:
- "hook_type": one of [problem-led, claim-led, trend-audio, before-after, talking-head, demo, testimonial, cold-open, unclear]
- "hook_description_inferred": short description of what the hook likely is, based on caption ("unclear from caption" if not enough signal)
- "format_tags": list from [single-shot, voice-over, on-screen-text, demo, before-after, talking-head, interview, GRWM, trend-audio, review, unboxing] — pick all that apply or empty
- "claims": list of objects with "text" and "category" (one of [sleep, energy, stress, focus, digestion, immunity, hormonal, skin, general-wellness, other])
- "cta": call to action text or null
- "brand_partnership_signal": one of [explicit-partner, implicit-partner, organic, unclear]

Return ONLY the JSON object. No markdown fences. No preamble."""

req = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {"responseMimeType": "application/json", "temperature": 0.1},
}
print(json.dumps(req))
