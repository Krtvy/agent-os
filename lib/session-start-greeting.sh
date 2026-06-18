#!/usr/bin/env bash
# session-start-greeting.sh — fires on Claude Code SessionStart.
#
# Picks one Mahabharat character at random, applies a Mahabharat-flavoured
# theme that evokes a state of action from the epic, and shows three quick
# "where are we" lines so the next session never starts cold.
#
# Discipline: fast (<150ms), never errors out, output goes to stdout. If
# anything fails, exit 0 silently — a broken greeting must NEVER block a
# session from starting. Compatible with macOS Bash 3.2 (no associative
# arrays).
#
# Themes (set via $CLAUDE_THEME; default rotates with the character pick):
#   arambh    — beginning, the start of a campaign · dawn-blue
#   manthan   — the churning of options · deep violet
#   sangram   — battle, the hour of action · ember red-orange
#   vijay     — victory, when work succeeds · golden bronze
#   shanti    — peace, when nothing burns · soft river-green
#   dhyana    — meditation, the long stillness · silver-grey
#
# Use:   export CLAUDE_THEME=shanti      (pin a single theme)
# Use:   export CLAUDE_THEME=auto        (default — rotates with character)
# Use:   export CLAUDE_THEME=random      (different theme every session)

set +e   # never fail; this is cosmetic

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# --------------------------------------------------------------------------
# Theme palette as parallel arrays (Bash 3.2 has no associative arrays).
# Index 0 = arambh, 1 = manthan, 2 = sangram, 3 = vijay, 4 = shanti, 5 = dhyana
# --------------------------------------------------------------------------
THEME_NAMES=(arambh manthan sangram vijay shanti dhyana)
THEME_PRIMARY=(75 99 208 220 84 250)
THEME_ACCENT=(80 141 215 222 120 255)
THEME_TAG_0="the start of a campaign"
THEME_TAG_1="the churning of options"
THEME_TAG_2="the hour of action"
THEME_TAG_3="the gold of success"
THEME_TAG_4="when nothing burns"
THEME_TAG_5="the long stillness"

theme_index() {
  # Return the index of a theme name, or -1 if unknown.
  local needle="$1" i
  for i in 0 1 2 3 4 5; do
    if [[ "${THEME_NAMES[$i]}" == "$needle" ]]; then
      echo "$i"; return
    fi
  done
  echo "-1"
}

# --------------------------------------------------------------------------
# Character roster — icon, name, motto, "natural theme" (which palette suits
# each character's voice). Used when $CLAUDE_THEME=auto (the default).
# --------------------------------------------------------------------------
CHARACTERS=(
  "🏹|Arjuna|Aim true. The eye of the bird, nothing else.|sangram"
  "🐒|Hanuman|Report first. Speed, precision, total recall.|arambh"
  "🐎|Nakula|Loud failures, quiet successes. The lights stay on.|shanti"
  "🪶|Narada|Specifics over generics. Always.|manthan"
  "⚖️|Yudhishthira|Dharmaraja doesn't guess. Every number defensible.|dhyana"
  "🔬|Vidura|Tier every source. Surface dissent.|manthan"
  "👁️|Sanjaya|Watching faithfully. Append-only, never invent.|dhyana"
  "📜|Vyasa|Slow, structural, patient. Frame-level only.|vijay"
  "🔮|Sahadeva|Stateless. Honest. Numbers, not narrative.|shanti"
  "⚔️|Bhishma|The vow holds. R1–R23 bind everyone equally.|sangram"
)

# --------------------------------------------------------------------------
# Pick character (XOR /dev/urandom for variance across rapid invocations).
# --------------------------------------------------------------------------
URAND=$(od -An -tu4 -N4 /dev/urandom 2>/dev/null | tr -d ' ')
RAND_SEED=$(( RANDOM ^ ${URAND:-0} ))
INDEX=$(( RAND_SEED % ${#CHARACTERS[@]} ))
IFS='|' read -r ICON NAME MOTTO NATURAL_THEME <<< "${CHARACTERS[$INDEX]}"

# --------------------------------------------------------------------------
# Resolve theme.
# --------------------------------------------------------------------------
CHOSEN_THEME="${CLAUDE_THEME:-auto}"
case "$CHOSEN_THEME" in
  auto)
    CHOSEN_THEME="$NATURAL_THEME"
    ;;
  random)
    THEME_INDEX=$(( (RAND_SEED >> 4) % ${#THEME_NAMES[@]} ))
    CHOSEN_THEME="${THEME_NAMES[$THEME_INDEX]}"
    ;;
esac

T_IDX=$(theme_index "$CHOSEN_THEME")
if [[ "$T_IDX" -lt 0 ]]; then
  # Unknown theme → fall back to arambh (beginning).
  CHOSEN_THEME=arambh
  T_IDX=0
fi

PRIMARY_CODE="${THEME_PRIMARY[$T_IDX]}"
ACCENT_CODE="${THEME_ACCENT[$T_IDX]}"
# Indirect-lookup the tagline (Bash 3.2 has no associative arrays).
TAGLINE_VAR="THEME_TAG_$T_IDX"
THEME_TAG="${!TAGLINE_VAR}"

# --------------------------------------------------------------------------
# ANSI colours (only if stdout is a tty).
# --------------------------------------------------------------------------
if [[ -t 1 ]]; then
  C_RESET=$'\033[0m'
  C_DIM=$'\033[2m'
  C_BOLD=$'\033[1m'
  C_PRIMARY=$'\033[38;5;'"$PRIMARY_CODE"'m'
  C_ACCENT=$'\033[38;5;'"$ACCENT_CODE"'m'
  C_GOLD=$'\033[38;5;220m'
  C_GREEN=$'\033[38;5;120m'
else
  C_RESET=""; C_DIM=""; C_BOLD=""; C_PRIMARY=""; C_ACCENT=""; C_GOLD=""; C_GREEN=""
fi

# --------------------------------------------------------------------------
# State lines.
# --------------------------------------------------------------------------
LATEST_AUDIT=""
if [[ -d "$REPO_ROOT/_audit" ]]; then
  LATEST_AUDIT=$(ls -t "$REPO_ROOT/_audit"/*.md 2>/dev/null | head -1 | xargs -n1 basename 2>/dev/null)
fi

NEXT_CRON=""
if command -v crontab >/dev/null 2>&1; then
  if crontab -l 2>/dev/null | grep -q "observer-test"; then
    NEXT_CRON="$(crontab -l 2>/dev/null | grep "observer-test" | head -1 | awk '{print $1, $2, $3, $4, $5}')"
  fi
fi

INBOX_STATUS=""
INBOX="$REPO_ROOT/.claude/agents/_meta/audit/inbox.md"
if [[ -f "$INBOX" ]]; then
  INBOX_LINES=$(awk '/critical/{c++} END{print c+0}' "$INBOX" 2>/dev/null)
  INBOX_LINES="${INBOX_LINES:-0}"
  if [[ "$INBOX_LINES" -gt 0 ]]; then
    INBOX_STATUS="${C_GOLD}${INBOX_LINES} critical finding(s) in inbox${C_RESET}"
  else
    INBOX_STATUS="${C_GREEN}inbox clear${C_RESET}"
  fi
fi

# --------------------------------------------------------------------------
# Reminders due — read _audit/REMINDERS.md, surface any entry whose
# `remind_after:` date is today or earlier. Lexicographic comparison works
# for YYYY-MM-DD format.
# --------------------------------------------------------------------------
REMINDERS_STATUS=""
REMINDERS_FILE="$REPO_ROOT/_audit/REMINDERS.md"
if [[ -f "$REMINDERS_FILE" ]]; then
  TODAY=$(date +%Y-%m-%d)
  DUE=$(awk -v today="$TODAY" '
    /^- id:/             { id = $3 }
    /^  remind_after:/ {
      remind = $2
      # Only accept real YYYY-MM-DD dates; skip placeholders in the format docs
      if (remind !~ /^[0-9]{4}-[0-9]{2}-[0-9]{2}$/) remind = ""
    }
    /^  topic:/ {
      sub(/^  topic: /, "")
      topic = $0
      if (remind != "" && remind <= today) {
        print "  • " topic " (id: " id ")"
      }
      id = ""; remind = ""; topic = ""
    }
  ' "$REMINDERS_FILE" 2>/dev/null)
  DUE_COUNT=$(echo -n "$DUE" | grep -c "^" 2>/dev/null || echo 0)
  if [[ -n "$DUE" ]] && [[ "$DUE_COUNT" -gt 0 ]]; then
    REMINDERS_STATUS="${C_GOLD}${DUE_COUNT} reminder(s) due${C_RESET}"
  fi
fi

# --------------------------------------------------------------------------
# Decorative vibe bar — 10 cells, fill count seeded by hour so it changes
# subtly through the day.
# --------------------------------------------------------------------------
HOUR=$(date +%-H)
FILL=$(( (HOUR % 8) + 2 ))   # always 2-9 filled cells; never empty, never full
VIBE_BAR=""
i=0
while [ $i -lt 10 ]; do
  if [ $i -lt $FILL ]; then
    VIBE_BAR+="${C_PRIMARY}▰${C_RESET}"
  else
    VIBE_BAR+="${C_DIM}▱${C_RESET}"
  fi
  i=$((i+1))
done

# --------------------------------------------------------------------------
# Render.
# --------------------------------------------------------------------------
echo ""
echo "  ${C_BOLD}${ICON}  ${C_PRIMARY}${NAME}${C_RESET}  ${C_DIM}—${C_RESET}  ${C_ACCENT}${MOTTO}${C_RESET}"
echo ""
if [[ -n "$LATEST_AUDIT" ]]; then
  echo "  ${C_DIM}last decision:${C_RESET}  ${LATEST_AUDIT}"
fi
if [[ -n "$NEXT_CRON" ]]; then
  echo "  ${C_DIM}next cron:${C_RESET}     ${NEXT_CRON}  (IST)"
fi
if [[ -n "$INBOX_STATUS" ]]; then
  echo "  ${C_DIM}sahadeva:${C_RESET}      ${INBOX_STATUS}"
fi
if [[ -n "$REMINDERS_STATUS" ]]; then
  echo "  ${C_DIM}reminders:${C_RESET}     ${REMINDERS_STATUS}  ${C_DIM}— see _audit/REMINDERS.md${C_RESET}"
  echo "$DUE" | while IFS= read -r line; do
    [[ -n "$line" ]] && echo "  ${C_GOLD}${line}${C_RESET}"
  done
fi
echo ""
echo "  ${C_DIM}theme:${C_RESET} ${C_PRIMARY}${CHOSEN_THEME}${C_RESET} ${C_DIM}— ${THEME_TAG}${C_RESET}   ${VIBE_BAR}"
echo ""

exit 0
