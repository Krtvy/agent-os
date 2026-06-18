#!/usr/bin/env bash
# video-analyze-batch.sh — daily competitor video analysis.
#
# Called by Nakula at 01:00 IST. Reads new videos from competitor_content/raw/,
# computes per-brand baseline-multiplier, runs Gemini analysis on deep-tier
# videos (≥2× baseline), writes lightweight metadata for the rest.
#
# Authentication: reads Gemini API keys from .credentials.yml at the repo
# root (gitignored). Rotates through the key list on 429/5xx errors.
# Falls back to stub mode if no keys are configured.
#
# Idempotent: re-running won't re-analyze videos whose idempotency keys
# already exist. To force re-analysis of a video, delete its key file:
#   .claude/agents/arjuna/idempotency-keys/video-analysis/<video-id>.json

set -euo pipefail

# --- Paths ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARJUNA_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$ARJUNA_DIR/../../.." && pwd)"
CREDENTIALS_FILE="$REPO_ROOT/.credentials.yml"
RAW_DIR="$REPO_ROOT/competitor_content/raw"
ANALYZED_DIR="$REPO_ROOT/competitor_content/analyzed"
IDEMPOTENCY_DIR="$ARJUNA_DIR/idempotency-keys/video-analysis"
LOG_DIR="$REPO_ROOT/logs/arjuna"

# --- Config ---
GEMINI_MODEL="${GEMINI_MODEL:-gemini-2.5-flash}"
BASELINE_DEEP_THRESHOLD="${BASELINE_DEEP_THRESHOLD:-2.0}"
BOOTSTRAP_MIN_PRIOR_VIDEOS="${BOOTSTRAP_MIN_PRIOR_VIDEOS:-10}"
RATE_LIMIT_DELAY_SEC="${RATE_LIMIT_DELAY_SEC:-1}"

# --- Run ID per Bhishma R20 ---
RUN_ID="arjuna-$(date -u +%Y%m%d-%H%M%SZ)-$(openssl rand -hex 3)"

# --- Logging ---
mkdir -p "$LOG_DIR" "$IDEMPOTENCY_DIR"
LOG_FILE="$LOG_DIR/${RUN_ID}-video-analysis.log"
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "[$RUN_ID] video-analyze-batch starting"
echo "  raw_dir: $RAW_DIR"
echo "  analyzed_dir: $ANALYZED_DIR"
echo "  gemini_model: $GEMINI_MODEL"
echo "  deep_threshold: ${BASELINE_DEEP_THRESHOLD}x baseline"

# --- Load Gemini keys ---
STUB_MODE=false
declare -a GEMINI_KEYS=()

if [[ -f "$CREDENTIALS_FILE" ]]; then
  while IFS= read -r key; do
    [[ -z "$key" ]] && continue
    [[ "$key" == *"REPLACE_ME"* ]] && continue
    GEMINI_KEYS+=("$key")
  done < <(python3 -c "
import yaml
try:
    cfg = yaml.safe_load(open('$CREDENTIALS_FILE'))
    for k in (cfg or {}).get('gemini', {}).get('keys', []) or []:
        print(k)
except Exception:
    pass
")
fi

if [[ -n "${GEMINI_API_KEY:-}" ]]; then
  GEMINI_KEYS+=("$GEMINI_API_KEY")
fi

if [[ ${#GEMINI_KEYS[@]} -eq 0 ]]; then
  echo "WARN: No Gemini keys configured."
  echo "      Add real keys to .credentials.yml under 'gemini.keys:' or set GEMINI_API_KEY env var."
  echo "      Running in stub mode — deep-tier videos will be written with error: no_gemini_keys."
  STUB_MODE=true
else
  echo "  gemini_keys_available: ${#GEMINI_KEYS[@]}"
fi

# --- Date setup ---
TODAY_UTC=$(date -u +%Y-%m-%d)
YESTERDAY_UTC=$(date -u -v-1d +%Y-%m-%d 2>/dev/null || date -u -d "yesterday" +%Y-%m-%d)

# --- Discover videos to analyze ---
# Find all raw JSONs from yesterday and today; collect (slug, video) pairs
# that don't yet have an idempotency key.
echo ""
echo "=== Discovering unanalyzed videos ==="

TO_ANALYZE_TMP=$(mktemp)
trap 'rm -f "$TO_ANALYZE_TMP" "${TIERED_TMP:-}"' EXIT
python3 <<EOF
import json, os, glob
from pathlib import Path

raw_dir = "$RAW_DIR"
idem_dir = "$IDEMPOTENCY_DIR"
dates = ["$YESTERDAY_UTC", "$TODAY_UTC"]

to_analyze = []
for slug_dir in sorted(Path(raw_dir).iterdir()):
    if not slug_dir.is_dir(): continue
    slug = slug_dir.name
    for date in dates:
        f = slug_dir / f"{date}.json"
        if not f.exists(): continue
        try:
            data = json.load(open(f))
        except Exception:
            continue
        for video in data.get("videos", []):
            vid = video.get("video_id")
            if not vid: continue
            # Skip if idempotency key exists
            if (Path(idem_dir) / f"{vid}.json").exists():
                continue
            to_analyze.append({
                "slug": slug,
                "video": video,
            })

json.dump(to_analyze, open("$TO_ANALYZE_TMP", "w"))
EOF

UNANALYZED_COUNT=$(python3 -c "import json; print(len(json.load(open('$TO_ANALYZE_TMP'))))")
echo "  unanalyzed_videos: $UNANALYZED_COUNT"

if [[ "$UNANALYZED_COUNT" -eq 0 ]]; then
  echo ""
  echo "=== Run summary ==="
  echo "  run_id: $RUN_ID"
  echo "  Nothing to analyze."
  echo "  status: OK (no new videos)"
  exit 0
fi

# --- Compute per-brand baseline + tier each video ---
echo ""
echo "=== Computing baselines + tiering videos ==="

TIERED_TMP=$(mktemp)
python3 <<EOF
import json, os
from pathlib import Path
from statistics import mean

to_analyze = json.load(open("$TO_ANALYZE_TMP"))
analyzed_dir = Path("$ANALYZED_DIR")
deep_threshold = float("$BASELINE_DEEP_THRESHOLD")
bootstrap_min = int("$BOOTSTRAP_MIN_PRIOR_VIDEOS")

# Per-brand baseline cache
baselines = {}
for slug in {item["slug"] for item in to_analyze}:
    brand_dir = analyzed_dir / slug
    if not brand_dir.exists():
        baselines[slug] = None
        continue
    views = []
    for f in brand_dir.glob("*.json"):
        try:
            d = json.load(open(f))
            v = d.get("performance_signal", {}).get("views", 0)
            if v > 0: views.append(v)
        except Exception:
            pass
    if len(views) >= bootstrap_min:
        baselines[slug] = mean(views)
    else:
        baselines[slug] = None  # bootstrap phase

tiered = []
for item in to_analyze:
    slug = item["slug"]
    video = item["video"]
    views = video.get("views", 0)
    baseline = baselines[slug]
    if baseline is None or baseline == 0:
        multiplier = 1.0
    else:
        multiplier = views / baseline
    tier = "deep" if multiplier >= deep_threshold else "lightweight"
    tiered.append({
        "slug": slug,
        "video": video,
        "baseline": baseline,
        "multiplier": multiplier,
        "tier": tier,
    })

json.dump(tiered, open("$TIERED_TMP", "w"))
EOF

DEEP_COUNT=$(python3 -c "import json; print(sum(1 for x in json.load(open('$TIERED_TMP')) if x['tier']=='deep'))")
LIGHT_COUNT=$(python3 -c "import json; print(sum(1 for x in json.load(open('$TIERED_TMP')) if x['tier']=='lightweight'))")
echo "  deep_tier (≥${BASELINE_DEEP_THRESHOLD}x baseline): $DEEP_COUNT"
echo "  lightweight_tier: $LIGHT_COUNT"

# --- Process each video ---
echo ""
echo "=== Processing ==="

ANALYZED_OK=0
ANALYZED_ERR=0
TIERED_COUNT=$(python3 -c "import json; print(len(json.load(open('$TIERED_TMP'))))")

for i in $(seq 0 $((TIERED_COUNT - 1))); do
  ITEM_TMP=$(mktemp)
  python3 -c "import json; json.dump(json.load(open('$TIERED_TMP'))[$i], open('$ITEM_TMP', 'w'))"
  SLUG=$(python3 -c "import json; print(json.load(open('$ITEM_TMP'))['slug'])")
  VID=$(python3 -c "import json; print(json.load(open('$ITEM_TMP'))['video']['video_id'])")
  VURL=$(python3 -c "import json; print(json.load(open('$ITEM_TMP'))['video'].get('url',''))")
  TIER=$(python3 -c "import json; print(json.load(open('$ITEM_TMP'))['tier'])")
  MULT=$(python3 -c "import json; d=json.load(open('$ITEM_TMP')); print(f'{d[\"multiplier\"]:.2f}')")
  VIEWS=$(python3 -c "import json; print(json.load(open('$ITEM_TMP'))['video'].get('views',0))")

  BRAND_ANALYZED_DIR="$ANALYZED_DIR/$SLUG"
  mkdir -p "$BRAND_ANALYZED_DIR"
  OUTPUT_FILE="$BRAND_ANALYZED_DIR/${VID}.json"
  IDEM_FILE="$IDEMPOTENCY_DIR/${VID}.json"

  echo "[$SLUG $VID] tier=$TIER mult=${MULT}x views=$VIEWS"

  # --- Lightweight tier: just write metadata, no Gemini call ---
  if [[ "$TIER" == "lightweight" ]]; then
    python3 <<EOF
import json
from datetime import datetime
item = json.load(open("$ITEM_TMP"))
video = item["video"]
out = {
    "video_id": "$VID",
    "brand_slug": "$SLUG",
    "analyzed_at_utc": datetime.utcnow().isoformat() + "Z",
    "analyzer": "none",
    "analyzer_model": None,
    "tier": "lightweight",
    "transcript": None,
    "hook_description": None,
    "hook_type": None,
    "format_tags": [],
    "claims": [],
    "cta": None,
    "duration_seconds": video.get("duration_seconds", 0),
    "performance_signal": {
        "views": video.get("views", 0),
        "likes": video.get("likes", 0),
        "shares": video.get("shares", 0),
        "comments": video.get("comments", 0),
        "view_velocity_per_hour": None,
        "baseline_multiplier": item["multiplier"],
    },
    "caption": video.get("caption", ""),
    "hashtags": video.get("hashtags", []),
    "url": "$VURL",
    "run_id": "$RUN_ID",
}
with open("$OUTPUT_FILE", "w") as f:
    json.dump(out, f, indent=2)
with open("$IDEM_FILE", "w") as f:
    json.dump({"video_id": "$VID", "tier": "lightweight", "completed_at_utc": datetime.utcnow().isoformat() + "Z", "run_id": "$RUN_ID"}, f, indent=2)
EOF
    ANALYZED_OK=$((ANALYZED_OK + 1))
    continue
  fi

  # --- Deep tier ---
  if $STUB_MODE; then
    python3 <<EOF
import json
from datetime import datetime
out = {
    "video_id": "$VID",
    "brand_slug": "$SLUG",
    "analyzed_at_utc": datetime.utcnow().isoformat() + "Z",
    "analyzer": "gemini",
    "analyzer_model": None,
    "tier": "deep",
    "error": "no_gemini_keys — deep analysis skipped; stub",
    "performance_signal": {
        "views": $VIEWS,
        "baseline_multiplier": $MULT,
    },
    "url": "$VURL",
    "run_id": "$RUN_ID",
}
with open("$OUTPUT_FILE", "w") as f:
    json.dump(out, f, indent=2)
with open("$IDEM_FILE", "w") as f:
    json.dump({"video_id": "$VID", "tier": "deep", "stubbed": True, "completed_at_utc": datetime.utcnow().isoformat() + "Z", "run_id": "$RUN_ID"}, f, indent=2)
EOF
    echo "  -> stub written (no Gemini call)"
    ANALYZED_ERR=$((ANALYZED_ERR + 1))
    continue
  fi

  # --- Real Gemini call with key rotation ---
  # Note (2026-05-11): Gemini free tier doesn't support direct video URL input
  # via fileData.fileUri (returns 429 with "limit: 0"). We analyze text-only
  # from caption + hashtags + metadata. Request body construction lives in
  # the standalone build-gemini-request.py helper (heredoc + f-string +
  # braces inside $() was breaking bash's heredoc parser).
  GEMINI_REQ=$(python3 "$SCRIPT_DIR/build-gemini-request.py" "$ITEM_TMP")

  ANALYSIS_RESULT=""
  KEY_USED=-1
  HTTP_CODE=""
  for k_idx in "${!GEMINI_KEYS[@]}"; do
    CUR_KEY="${GEMINI_KEYS[$k_idx]}"
    KEY_TAIL="${CUR_KEY: -4}"
    echo "  attempt gemini key #$((k_idx + 1))/${#GEMINI_KEYS[@]} (...${KEY_TAIL})"

    RESP=$(curl -sS -w "\n___HTTP_CODE___%{http_code}" -X POST \
      "https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=$CUR_KEY" \
      -H "Content-Type: application/json" \
      -d "$GEMINI_REQ" 2>&1) || true

    HTTP_CODE=$(echo "$RESP" | grep "___HTTP_CODE___" | sed 's/.*___HTTP_CODE___//')
    BODY=$(echo "$RESP" | sed 's/___HTTP_CODE___.*//')

    if [[ "$HTTP_CODE" =~ ^2[0-9]{2}$ ]]; then
      echo "  -> HTTP $HTTP_CODE (success)"
      ANALYSIS_RESULT="$BODY"
      KEY_USED=$k_idx
      break
    elif [[ "$HTTP_CODE" == "429" || "$HTTP_CODE" =~ ^5[0-9]{2}$ ]]; then
      echo "  -> HTTP $HTTP_CODE (rate-limit or server error); rotating"
      continue
    elif [[ "$HTTP_CODE" =~ ^4[0-9]{2}$ ]]; then
      echo "  -> HTTP $HTTP_CODE (auth/quota issue); rotating"
      continue
    else
      echo "  -> unexpected HTTP $HTTP_CODE; rotating"
      continue
    fi
  done

  if [[ $KEY_USED -lt 0 ]]; then
    echo "  -> ALL Gemini keys exhausted for $VID (last HTTP: $HTTP_CODE)"
    python3 <<EOF
import json
from datetime import datetime
out = {
    "video_id": "$VID",
    "brand_slug": "$SLUG",
    "analyzed_at_utc": datetime.utcnow().isoformat() + "Z",
    "analyzer": "gemini",
    "analyzer_model": "$GEMINI_MODEL",
    "tier": "deep",
    "error": "gemini_exhausted (last HTTP: $HTTP_CODE)",
    "performance_signal": {
        "views": $VIEWS,
        "baseline_multiplier": $MULT,
    },
    "url": "$VURL",
    "run_id": "$RUN_ID",
}
with open("$OUTPUT_FILE", "w") as f:
    json.dump(out, f, indent=2)
EOF
    ANALYZED_ERR=$((ANALYZED_ERR + 1))
    # Do NOT write idempotency key — we want to retry next run
    continue
  fi

  # Parse Gemini response into our shape (text-only mode)
  # Write Gemini response to temp file to avoid heredoc control-char issues
  ANALYSIS_TMP=$(mktemp)
  echo "$ANALYSIS_RESULT" > "$ANALYSIS_TMP"
  python3 <<EOF
import json, re
from datetime import datetime

raw = open("$ANALYSIS_TMP").read()
try:
    gemini_response = json.loads(raw, strict=False)
except Exception:
    gemini_response = {}

# Extract the model's text output from Gemini's response envelope
analysis = {}
text = None
try:
    text = gemini_response["candidates"][0]["content"]["parts"][0]["text"]
    text = re.sub(r'^\`\`\`(?:json)?\s*', '', text.strip())
    text = re.sub(r'\s*\`\`\`$', '', text)
    analysis = json.loads(text, strict=False)
except Exception as e:
    analysis = {"_parse_error": f"could not parse gemini response: {e}", "_raw_text": (text or raw[:500])}

out = {
    "video_id": "$VID",
    "brand_slug": "$SLUG",
    "analyzed_at_utc": datetime.utcnow().isoformat() + "Z",
    "analyzer": "gemini",
    "analyzer_model": "$GEMINI_MODEL",
    "tier": "deep",
    "analysis_basis": "text-only (caption + hashtags + metadata, no visual access on free tier)",
    "transcript": None,
    "hook_description_inferred": analysis.get("hook_description_inferred"),
    "hook_type": analysis.get("hook_type"),
    "format_tags": analysis.get("format_tags", []),
    "claims": analysis.get("claims", []),
    "cta": analysis.get("cta"),
    "brand_partnership_signal": analysis.get("brand_partnership_signal"),
    "performance_signal": {
        "views": $VIEWS,
        "baseline_multiplier": $MULT,
    },
    "url": "$VURL",
    "run_id": "$RUN_ID",
}
if "_parse_error" in analysis:
    out["parse_error"] = analysis["_parse_error"]
    out["_raw_text"] = analysis.get("_raw_text")

with open("$OUTPUT_FILE", "w") as f:
    json.dump(out, f, indent=2)
with open("$IDEM_FILE", "w") as f:
    json.dump({"video_id": "$VID", "tier": "deep", "key_used_index": $KEY_USED, "completed_at_utc": datetime.utcnow().isoformat() + "Z", "run_id": "$RUN_ID"}, f, indent=2)
EOF
  ANALYZED_OK=$((ANALYZED_OK + 1))

  # Cleanup per-iteration temps + rate-limit defensive delay
  rm -f "$ITEM_TMP" "$ANALYSIS_TMP"
  sleep "$RATE_LIMIT_DELAY_SEC"
done

# --- Run summary ---
echo ""
echo "=== Run summary ==="
echo "  run_id: $RUN_ID"
echo "  unanalyzed_at_start: $UNANALYZED_COUNT"
echo "  deep_tier: $DEEP_COUNT"
echo "  lightweight_tier: $LIGHT_COUNT"
echo "  analyzed_ok: $ANALYZED_OK"
echo "  analyzed_err: $ANALYZED_ERR"
echo "  log: $LOG_FILE"

if [[ $ANALYZED_ERR -eq $UNANALYZED_COUNT ]] && [[ $UNANALYZED_COUNT -gt 0 ]]; then
  echo "  status: ALL FAILED (likely auth or quota)"
  exit 1
elif [[ $ANALYZED_ERR -gt 0 ]]; then
  echo "  status: PARTIAL"
  exit 0
else
  echo "  status: OK"
  exit 0
fi
