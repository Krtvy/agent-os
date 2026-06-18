#!/usr/bin/env bash
# session-end-checkpoint.sh — fires on Claude Code SessionEnd.
#
# Writes a tiny `_audit/.last-session.md` file capturing what just happened
# so the NEXT session can read "where I left off" in one glance. Overwritten
# every session — this is the rolling snapshot, NOT the historical record.
# (The historical record stays in the dated _audit/<topic>.md files.)
#
# Discipline:
#   - Fast (<200ms). Read-only on the repo except for `.last-session.md`.
#   - Never fail loud — a broken session-end hook must NEVER block session
#     closure. Exit 0 on any error.
#   - No interactive prompts.

set +e   # never fail; this is a safety net, not a critical path

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$REPO_ROOT/_audit/.last-session.md"

NOW_UTC="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
NOW_IST="$(date +"%Y-%m-%d %H:%M %Z")"

# Last 3 _audit/ files (excluding this hidden one and any backup files).
LAST_AUDIT_FILES=$(ls -t "$REPO_ROOT/_audit"/*.md 2>/dev/null | grep -v "\.last-session\.md" | head -3 | xargs -n1 basename 2>/dev/null)

# Files modified since last commit.
cd "$REPO_ROOT" 2>/dev/null
MODIFIED_FILES=$(git status --short 2>/dev/null | head -30)
[ -z "$MODIFIED_FILES" ] && MODIFIED_FILES="(none — working tree clean)"

# Last commit summary.
LAST_COMMIT=$(git log --oneline -1 2>/dev/null)
[ -z "$LAST_COMMIT" ] && LAST_COMMIT="(no commits)"

# Any agent ran during this session? Approximate by looking at run.log mtime
# relative to the last 24h.
SANJAYA_RAN="no"
if [ -f "$REPO_ROOT/.claude/agents/_meta/observer/run.log" ]; then
  if [ "$REPO_ROOT/.claude/agents/_meta/observer/run.log" -nt /tmp/session-start-marker 2>/dev/null ] || \
     find "$REPO_ROOT/.claude/agents/_meta/observer/run.log" -mtime -1 -print 2>/dev/null | grep -q .; then
    SANJAYA_RAN="possibly (run.log mtime within last 24h)"
  fi
fi

SAHADEVA_RAN="no"
if [ -f "$REPO_ROOT/.claude/agents/_meta/audit/run.log" ]; then
  if find "$REPO_ROOT/.claude/agents/_meta/audit/run.log" -mtime -1 -print 2>/dev/null | grep -q .; then
    SAHADEVA_RAN="possibly (run.log mtime within last 24h)"
  fi
fi

# Sahadeva inbox state.
INBOX_STATE="(no inbox)"
INBOX="$REPO_ROOT/.claude/agents/_meta/audit/inbox.md"
if [ -f "$INBOX" ]; then
  CRIT_COUNT=$(awk '/critical/{c++} END{print c+0}' "$INBOX" 2>/dev/null)
  CRIT_COUNT="${CRIT_COUNT:-0}"
  if [ "$CRIT_COUNT" -gt 0 ]; then
    INBOX_STATE="$CRIT_COUNT critical finding(s) waiting"
  else
    INBOX_STATE="clear"
  fi
fi

# Compose. Use a heredoc so the markdown is verbatim.
cat > "$TARGET" <<EOF
# Last Session Snapshot

> Rolling "where I left off" file. Overwritten each session. **Not** part of the historical record — that's in the dated \`_audit/<topic>.md\` files. Use this for the 30-second "what was I doing yesterday" glance.

**Session ended:** $NOW_IST (\`$NOW_UTC\`)

## Last 3 audit decisions

$(echo "$LAST_AUDIT_FILES" | sed 's/^/- /')

## Working tree at session close

\`\`\`
$MODIFIED_FILES
\`\`\`

**Last commit:** $LAST_COMMIT

## Agent activity during this session

- **Sanjaya** (daily 02:00 IST cron): $SANJAYA_RAN
- **Sahadeva** (Sunday 10:00 IST cron): $SAHADEVA_RAN

## Sahadeva inbox

$INBOX_STATE

## Resume procedure

1. \`/status\` — full one-screen scan of project state
2. Read the most recent \`_audit/\` file from the list above for the decision context
3. \`/resume\` inside Claude Code — pick up the prior conversation if you want the full reasoning chain

---

*Auto-written by \`lib/session-end-checkpoint.sh\` on session close. This file is overwritten — for a permanent save-point, use the \`/checkpoint\` skill which writes to a dated file in \`_audit/\`.*
EOF

exit 0
