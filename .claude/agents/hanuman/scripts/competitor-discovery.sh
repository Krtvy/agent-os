#!/usr/bin/env bash
# competitor-discovery.sh — daily TikTok creator content discovery for watched competitors.
#
# Schema v2 (2026-05-11): hashtag-first design. These brands don't post
# much from their own accounts; the actual competitive signal lives in
# creator content tagged with brand hashtags. We optionally also pull
# from a known_creators list per brand for high-signal partners.
#
# Two-pass discovery:
#   Pass A — hashtag pass: for each brand's hashtag(s), pull recent videos
#            via clockworks/tiktok-hashtag-scraper. Tag each video with
#            source: "hashtag", source_value: "<hashtag>".
#   Pass B — creator pass: for each brand's known_creators[], pull recent
#            videos via clockworks/free-tiktok-scraper. Tag each video
#            with source: "creator", source_value: "<handle>".
#
# Per video, we record which brand it surfaced under. Same video can appear
# under multiple brands (e.g., a creator posts with both #bloom and #goli).
# We DON'T dedup across brands — each brand's daily JSON includes all
# videos that surfaced under its hashtags/creators.
#
# Recency filter: only keep videos posted within the configured window
# (defaults.recency_window_hours, default 168 = 7 days).
#
# Idempotent: re-running same day overwrites that day's per-brand JSON.

set -euo pipefail

# --- Paths ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HANUMAN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$HANUMAN_DIR/../../.." && pwd)"
COMPETITORS_FILE="$HANUMAN_DIR/competitors.yml"
CREDENTIALS_FILE="$REPO_ROOT/.credentials.yml"
OUTPUT_DIR="$REPO_ROOT/competitor_content/raw"
LOG_DIR="$REPO_ROOT/logs/hanuman"
LAST_DISCOVERY_FILE="$REPO_ROOT/competitor_content/raw/.last-discovery"

# --- Apify actor names (v2 — free-tier friendly variants) ---
HASHTAG_ACTOR="${HASHTAG_ACTOR:-clockworks/tiktok-hashtag-scraper}"
PROFILE_ACTOR="${PROFILE_ACTOR:-clockworks/free-tiktok-scraper}"

# --- Run ID per Bhishma R20 ---
RUN_ID="hanuman-$(date -u +%Y%m%d-%H%M%SZ)-$(openssl rand -hex 3)"

# --- Logging setup ---
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/${RUN_ID}-discovery.log"
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "[$RUN_ID] competitor-discovery starting (schema v2: hashtag-first)"
echo "  competitors_file: $COMPETITORS_FILE"
echo "  hashtag_actor: $HASHTAG_ACTOR"
echo "  profile_actor: $PROFILE_ACTOR"
echo "  output_dir: $OUTPUT_DIR"

# --- Sanity ---
if [[ ! -f "$COMPETITORS_FILE" ]]; then
  echo "ERROR: competitors.yml not found at $COMPETITORS_FILE"
  exit 1
fi

# --- Load Apify token pool ---
STUB_MODE=false
declare -a APIFY_TOKENS=()

if [[ -f "$CREDENTIALS_FILE" ]]; then
  while IFS= read -r tok; do
    [[ -z "$tok" ]] && continue
    [[ "$tok" == *"REPLACE_ME"* ]] && continue
    APIFY_TOKENS+=("$tok")
  done < <(python3 -c "
import yaml
try:
    cfg = yaml.safe_load(open('$CREDENTIALS_FILE'))
    for t in (cfg or {}).get('apify', {}).get('tokens', []) or []:
        print(t)
except Exception:
    pass
")
fi

if [[ -n "${APIFY_TOKEN:-}" ]]; then
  APIFY_TOKENS+=("$APIFY_TOKEN")
fi

if [[ ${#APIFY_TOKENS[@]} -eq 0 ]]; then
  echo "WARN: No Apify tokens configured. Running in stub mode."
  STUB_MODE=true
else
  echo "  apify_tokens_available: ${#APIFY_TOKENS[@]}"
fi

# --- Parse competitors.yml into work units ---
WORK_UNITS_JSON=$(python3 <<EOF
import yaml, json
cfg = yaml.safe_load(open('$COMPETITORS_FILE'))
defaults = cfg.get('defaults', {})
default_vph = defaults.get('videos_per_hashtag', 30)
default_vpc = defaults.get('videos_per_creator', 10)

units = []
for b in cfg.get('competitors', []):
    if not b.get('enabled', True): continue
    slug = b['slug']
    vph = b.get('videos_per_hashtag', default_vph)
    vpc = b.get('videos_per_creator', default_vpc)
    for tag in b.get('hashtags', []) or []:
        units.append({'brand_slug': slug, 'source': 'hashtag', 'source_value': tag, 'limit': vph})
    for handle in b.get('known_creators', []) or []:
        # Accept either string handles or {tiktok_handle: ...} objects
        h = handle if isinstance(handle, str) else handle.get('tiktok_handle')
        if h:
            units.append({'brand_slug': slug, 'source': 'creator', 'source_value': h, 'limit': vpc})
print(json.dumps(units))
EOF
)

UNIT_COUNT=$(echo "$WORK_UNITS_JSON" | python3 -c "import sys, json; print(len(json.loads(sys.stdin.read())))")
HASHTAG_UNITS=$(echo "$WORK_UNITS_JSON" | python3 -c "import sys, json; print(sum(1 for u in json.loads(sys.stdin.read()) if u['source']=='hashtag'))")
CREATOR_UNITS=$(echo "$WORK_UNITS_JSON" | python3 -c "import sys, json; print(sum(1 for u in json.loads(sys.stdin.read()) if u['source']=='creator'))")
echo "  work_units: $UNIT_COUNT total ($HASHTAG_UNITS hashtags, $CREATOR_UNITS creators)"

# --- Date setup ---
TODAY_UTC=$(date -u +%Y-%m-%d)
RECENCY_HOURS=$(python3 -c "
import yaml
cfg = yaml.safe_load(open('$COMPETITORS_FILE'))
print(cfg.get('defaults', {}).get('recency_window_hours', 168))
")
echo "  recency_window_hours: $RECENCY_HOURS"
echo ""

# --- Per-brand accumulator: temp files per brand slug (bash 3.2 compat) ---
ACCUM_DIR="$(mktemp -d)"
trap 'rm -rf "$ACCUM_DIR"' EXIT
# Initialize an empty array file per brand we'll touch
echo "  accum_dir: $ACCUM_DIR"

TOTAL_FETCHED=0
TOTAL_KEPT=0
TOTAL_ERRORS=0

# --- Process each work unit ---
for i in $(seq 0 $((UNIT_COUNT - 1))); do
  UNIT=$(echo "$WORK_UNITS_JSON" | python3 -c "import sys, json; print(json.dumps(json.loads(sys.stdin.read())[$i]))")
  BRAND_SLUG=$(echo "$UNIT" | python3 -c "import sys, json; print(json.loads(sys.stdin.read())['brand_slug'])")
  SOURCE=$(echo "$UNIT" | python3 -c "import sys, json; print(json.loads(sys.stdin.read())['source'])")
  SOURCE_VALUE=$(echo "$UNIT" | python3 -c "import sys, json; print(json.loads(sys.stdin.read())['source_value'])")
  LIMIT=$(echo "$UNIT" | python3 -c "import sys, json; print(json.loads(sys.stdin.read())['limit'])")

  if [[ "$SOURCE" == "hashtag" ]]; then
    LABEL="#$SOURCE_VALUE → $BRAND_SLUG"
    ACTOR="$HASHTAG_ACTOR"
    APIFY_INPUT="{\"hashtags\":[\"$SOURCE_VALUE\"],\"resultsPerPage\":$LIMIT,\"shouldDownloadVideos\":false,\"shouldDownloadCovers\":false,\"proxyConfiguration\":{\"useApifyProxy\":true}}"
  else
    LABEL="@$SOURCE_VALUE → $BRAND_SLUG"
    ACTOR="$PROFILE_ACTOR"
    APIFY_INPUT="{\"profiles\":[\"$SOURCE_VALUE\"],\"resultsPerPage\":$LIMIT,\"shouldDownloadVideos\":false,\"shouldDownloadCovers\":false,\"proxyConfiguration\":{\"useApifyProxy\":true}}"
  fi

  echo "[$LABEL] limit=$LIMIT actor=$ACTOR"

  if $STUB_MODE; then
    echo "  -> stub (no Apify call)"
    TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
    continue
  fi

  # --- Token rotation ---
  APIFY_RESPONSE=""
  HTTP_CODE=""
  TOKEN_USED=-1
  for tok_idx in "${!APIFY_TOKENS[@]}"; do
    TOK="${APIFY_TOKENS[$tok_idx]}"
    TAIL="${TOK: -4}"

    RESP=$(curl -sS -w "\n___HTTP_CODE___%{http_code}" -X POST \
      "https://api.apify.com/v2/acts/${ACTOR//\//~}/run-sync-get-dataset-items?token=$TOK" \
      -H "Content-Type: application/json" \
      -d "$APIFY_INPUT" 2>&1) || true

    HTTP_CODE=$(echo "$RESP" | grep "___HTTP_CODE___" | sed 's/.*___HTTP_CODE___//')
    APIFY_RESPONSE=$(echo "$RESP" | sed 's/___HTTP_CODE___.*//')

    if [[ "$HTTP_CODE" =~ ^2[0-9]{2}$ ]]; then
      TOKEN_USED=$tok_idx
      break
    fi
    echo "  HTTP $HTTP_CODE on token (...${TAIL}); rotating"
  done

  if [[ $TOKEN_USED -lt 0 ]]; then
    echo "  -> ALL tokens exhausted (last HTTP: $HTTP_CODE)"
    TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
    continue
  fi

  # --- Parse, filter by recency, map to our shape ---
  # Write response to temp file to avoid heredoc string-interpolation issues
  # (captions contain control characters that break shell quoting)
  RESP_TMP=$(mktemp)
  PARSED_TMP=$(mktemp)
  echo "$APIFY_RESPONSE" > "$RESP_TMP"
  python3 <<EOF
import json
from datetime import datetime, timedelta, timezone

raw = open("$RESP_TMP").read()
recency_hours = int("$RECENCY_HOURS")
cutoff = datetime.now(timezone.utc) - timedelta(hours=recency_hours)
source = "$SOURCE"
source_value = "$SOURCE_VALUE"

try:
    items = json.loads(raw, strict=False)
except Exception as e:
    json.dump({"fetched": 0, "kept": 0, "videos": [], "error": f"parse_failed: {e}"}, open("$PARSED_TMP", "w"))
    raise SystemExit(0)

if not isinstance(items, list):
    json.dump({"fetched": 0, "kept": 0, "videos": [], "error": "not_a_list"}, open("$PARSED_TMP", "w"))
    raise SystemExit(0)

# Filter out actor error markers
items = [it for it in items if isinstance(it, dict) and 'error' not in it and 'note' not in it]
fetched = len(items)

def parse_dt(iso):
    if not iso: return None
    try:
        return datetime.fromisoformat(iso.replace('Z', '+00:00'))
    except Exception:
        return None

def map_video(item):
    posted = item.get('createTimeISO') or item.get('createTime') or ''
    author = item.get('authorMeta') or {}
    return {
        'video_id': str(item.get('id') or ''),
        'url': item.get('webVideoUrl') or '',
        'posted_at_utc': posted,
        'views': int(item.get('playCount') or 0),
        'likes': int(item.get('diggCount') or 0),
        'comments': int(item.get('commentCount') or 0),
        'shares': int(item.get('shareCount') or 0),
        'caption': (item.get('text') or '')[:1000],
        'hashtags': [h.get('name') if isinstance(h, dict) else h for h in (item.get('hashtags') or [])][:30],
        'duration_seconds': int((item.get('videoMeta') or {}).get('duration') or 0),
        'thumbnail_url': (item.get('videoMeta') or {}).get('coverUrl') or '',
        'author_handle': author.get('name', ''),
        'author_followers': int(author.get('fans', 0) or 0),
        'source': source,
        'source_value': source_value,
    }

kept_videos = []
for it in items:
    v = map_video(it)
    if not v['video_id']: continue
    dt = parse_dt(v['posted_at_utc'])
    if dt is None or dt < cutoff: continue
    kept_videos.append(v)

json.dump({"fetched": fetched, "kept": len(kept_videos), "videos": kept_videos}, open("$PARSED_TMP", "w"))
EOF

  FETCHED=$(python3 -c "import json; print(json.load(open('$PARSED_TMP'))['fetched'])")
  KEPT=$(python3 -c "import json; print(json.load(open('$PARSED_TMP'))['kept'])")
  echo "  -> fetched: $FETCHED, kept after recency filter: $KEPT"
  TOTAL_FETCHED=$((TOTAL_FETCHED + FETCHED))
  TOTAL_KEPT=$((TOTAL_KEPT + KEPT))

  # Accumulate videos into per-brand temp file (read from file, not heredoc)
  ACCUM_FILE="$ACCUM_DIR/$BRAND_SLUG.json"
  if [[ ! -f "$ACCUM_FILE" ]]; then echo "[]" > "$ACCUM_FILE"; fi
  python3 -c "
import json
prev = json.load(open('$ACCUM_FILE'))
parsed = json.load(open('$PARSED_TMP'))
new = parsed.get('videos', [])
json.dump(prev + new, open('$ACCUM_FILE', 'w'))
"

  rm -f "$RESP_TMP" "$PARSED_TMP"
done

# --- Write per-brand JSON files (dedup within brand by video_id) ---
echo ""
echo "=== Writing per-brand JSON files ==="
for ACCUM_FILE in "$ACCUM_DIR"/*.json; do
  [[ -f "$ACCUM_FILE" ]] || continue
  slug=$(basename "$ACCUM_FILE" .json)
  BRAND_OUT_DIR="$OUTPUT_DIR/$slug"
  mkdir -p "$BRAND_OUT_DIR"
  OUTPUT_FILE="$BRAND_OUT_DIR/${TODAY_UTC}.json"

  python3 <<EOF
import json
from datetime import datetime
videos = json.load(open('$ACCUM_FILE'))
# Dedup by video_id, keep first occurrence
seen = set()
deduped = []
for v in videos:
    vid = v.get('video_id')
    if vid and vid not in seen:
        seen.add(vid)
        deduped.append(v)
out = {
    'brand_slug': '$slug',
    'pulled_at_utc': datetime.utcnow().isoformat() + 'Z',
    'run_id': '$RUN_ID',
    'total_collected': len(videos),
    'deduped_count': len(deduped),
    'videos': deduped,
}
with open('$OUTPUT_FILE', 'w') as f:
    json.dump(out, f, indent=2)
print(f"  $slug: collected={len(videos)} deduped={len(deduped)} → $OUTPUT_FILE")
EOF
done

# --- Last-discovery marker ---
date -u +%Y-%m-%dT%H:%M:%SZ > "$LAST_DISCOVERY_FILE"

# --- Run summary ---
echo ""
echo "=== Run summary ==="
echo "  run_id: $RUN_ID"
echo "  work_units_processed: $UNIT_COUNT"
echo "  videos_fetched_total: $TOTAL_FETCHED"
echo "  videos_kept_after_recency: $TOTAL_KEPT"
echo "  errors: $TOTAL_ERRORS"
echo "  log: $LOG_FILE"

if [[ $TOTAL_ERRORS -eq $UNIT_COUNT ]] && [[ $UNIT_COUNT -gt 0 ]]; then
  echo "  status: ALL work units failed"
  exit 1
elif [[ $TOTAL_ERRORS -gt 0 ]]; then
  echo "  status: PARTIAL"
  exit 0
else
  echo "  status: OK"
  exit 0
fi
