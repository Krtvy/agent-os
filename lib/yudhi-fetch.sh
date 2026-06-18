#!/usr/bin/env bash
# yudhi-fetch.sh — resolve a Google Sheets URL or local file path to a local CSV.
#
# Why: Yudhishthira's P0 (when input is a Sheet URL) needs a way to read the
# sheet. On Hyperagent that's the Google Sheets integration. Locally there is
# no integration. This wrapper tries the public-CSV-export path (works when
# the sheet is shared "anyone with link can view") and otherwise returns
# actionable instructions instead of failing silently.
#
# Usage:
#   lib/yudhi-fetch.sh 'https://docs.google.com/spreadsheets/d/<id>/edit?gid=0'
#       → fetches public CSV export to a /tmp file, echoes the path on success
#
#   lib/yudhi-fetch.sh 'https://docs.google.com/.../edit?gid=0' /path/out.csv
#       → same, but writes to the named output path
#
#   lib/yudhi-fetch.sh /local/path/to/file.csv
#       → returns the path unchanged (already local)
#
# Exit codes:
#   0  — success; stdout has the local CSV path
#   1  — fetch failed for non-auth reasons (network, etc.)
#   2  — sheet is private / not publicly accessible (auth-wall HTML returned)
#   64 — usage error

set -euo pipefail

INPUT="${1:-}"
OUTPUT="${2:-}"

if [[ -z "$INPUT" ]]; then
  echo "usage: yudhi-fetch.sh <sheet-url-or-csv-path> [output-csv-path]" >&2
  exit 64
fi

# Local file path → return unchanged.
if [[ -f "$INPUT" ]]; then
  echo "$INPUT"
  exit 0
fi

# Google Sheets URL → extract sheet ID + gid, attempt CSV export.
# Note: Bash 3.2 (macOS default) chokes on inline =~ patterns containing `&`.
# Assigning the pattern to a variable first is the documented workaround.
SHEET_ID_PATTERN='docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)'
GID_PATTERN='[#?&]gid=([0-9]+)'

if [[ "$INPUT" =~ $SHEET_ID_PATTERN ]]; then
  SHEET_ID="${BASH_REMATCH[1]}"
  GID="0"
  if [[ "$INPUT" =~ $GID_PATTERN ]]; then
    GID="${BASH_REMATCH[1]}"
  fi

  if [[ -z "$OUTPUT" ]]; then
    OUTPUT="/tmp/yudhi-sheet-${SHEET_ID:0:12}-gid${GID}-$(date +%s).csv"
  fi

  EXPORT_URL="https://docs.google.com/spreadsheets/d/${SHEET_ID}/export?format=csv&gid=${GID}"

  # -L follow redirects, -s silent, -w status code, -o output file
  HTTP_STATUS=$(curl -sL -o "$OUTPUT" -w "%{http_code}" "$EXPORT_URL" 2>/dev/null || echo "000")

  if [[ "$HTTP_STATUS" == "200" && -s "$OUTPUT" ]]; then
    # Detect HTML auth wall returned with 200 status (Google's pattern).
    if head -c 256 "$OUTPUT" | grep -qiE "<html|<!DOCTYPE|<head"; then
      rm -f "$OUTPUT"
      cat >&2 <<EOF
yudhi-fetch: sheet $SHEET_ID is not publicly accessible (received HTML auth wall).

Three options:
  1. Make the sheet public-view (fastest):
     - Open the sheet in Google Sheets
     - Share → "Anyone with the link can view"
     - Re-run yudhi-fetch.sh with the same URL

  2. Download the sheet manually:
     - In Google Sheets: File → Download → Comma-separated values (.csv)
     - Pass the local path:
         lib/yudhi-fetch.sh /path/to/downloaded.csv

  3. Provision a dedicated Google account for Yudhishthira (Phase 2):
     - See .claude/agents/yudhishthira/skill.md § Phase 2 readiness
EOF
      exit 2
    fi
    echo "$OUTPUT"
    exit 0
  fi

  rm -f "$OUTPUT" 2>/dev/null || true
  echo "yudhi-fetch: HTTP $HTTP_STATUS fetching sheet $SHEET_ID (gid=$GID)" >&2
  exit 1
fi

echo "yudhi-fetch: unrecognized input '$INPUT' — expected a Google Sheets URL or a local file path" >&2
exit 64
