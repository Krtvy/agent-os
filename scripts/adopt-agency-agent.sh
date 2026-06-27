#!/usr/bin/env bash
# adopt-agency-agent.sh
# Downloads an agent from msitarzewski/agency-agents, wraps it with Bhishma
# compliance, and installs it as a Tier-0 worker in observer-test.
#
# Usage:
#   bash scripts/adopt-agency-agent.sh \
#     --source "engineering/engineering-data-engineer.md" \
#     --name "Draupadi" \
#     --tier 0 \
#     --emoji "🔧"
#
# Options:
#   --source   Required. Path within agency-agents repo (e.g. "engineering/engineering-data-engineer.md")
#   --name     Required. Mahabharata name for this agent (e.g. "Draupadi")
#   --tier     Default: 0. Agent tier (0 = worker)
#   --emoji    Default: 🤖. Frontmatter icon
#   --dry-run  Preview without writing files

set -euo pipefail

REPO_URL="https://raw.githubusercontent.com/msitarzewski/agency-agents/main"
OBSERVER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AGENTS_DIR="$OBSERVER_ROOT/.claude/agents"
LOGS_DIR="$OBSERVER_ROOT/logs"

NAME=""
SOURCE=""
TIER="0"
EMOJI="🤖"
DRY_RUN=false

# ── Parse args ────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)    NAME="$2";    shift 2 ;;
    --source)  SOURCE="$2";  shift 2 ;;
    --tier)    TIER="$2";    shift 2 ;;
    --emoji)   EMOJI="$2";   shift 2 ;;
    --dry-run) DRY_RUN=true; shift   ;;
    *) echo "Unknown flag: $1"; exit 1 ;;
  esac
done

[[ -z "$NAME" ]]   && { echo "Error: --name is required";   exit 1; }
[[ -z "$SOURCE" ]] && { echo "Error: --source is required"; exit 1; }

SLUG=$(echo "$NAME" | tr '[:upper:]' '[:lower:]')
AGENT_DIR="$AGENTS_DIR/$SLUG"
LOG_DIR="$LOGS_DIR/$SLUG"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Adopting agency-agent → $NAME ($SLUG)"
echo "  Source: agency-agents/$SOURCE"
echo "  Target: $AGENT_DIR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── Fetch raw content ─────────────────────────────────────────────────────────
RAW_URL="$REPO_URL/$SOURCE"
echo "[1/5] Fetching: $RAW_URL"
RAW_CONTENT=$(curl -fsSL "$RAW_URL") || {
  echo "Error: could not fetch $RAW_URL"
  exit 1
}

# Extract description from frontmatter
DESCRIPTION=$(echo "$RAW_CONTENT" | awk '/^---/{p++} p==1 && /^description:/{sub(/^description: */,""); print; exit}')
[[ -z "$DESCRIPTION" ]] && DESCRIPTION="Adopted from agency-agents: $SOURCE"

# Extract body (everything after closing ---)
BODY=$(echo "$RAW_CONTENT" | awk 'BEGIN{f=0} /^---/{f++; if(f==2){skip=1;next}} skip{print}')

# ── Generate run_id helper ────────────────────────────────────────────────────
RUN_ID_FUNC="gen_run_id() {
  local args=\"\$1\"
  local ts=\$(date -u +\"%Y%m%d-%H%M%SZ\")
  local hash=\$(printf \"%s%s\" \"\$args\" \"\$ts\" | sha256sum | head -c 6)
  echo \"${SLUG}-\${ts}-\${hash}\"
}"

# ── Build agent.md ────────────────────────────────────────────────────────────
AGENT_MD="---
name: $SLUG
icon: $EMOJI
tier: $TIER
model: claude-sonnet-4-6
effort: medium
tools: [Read, Write, Edit, Glob, Grep, Bash]
write_scope:
  - ~/projects/observer-test/.claude/agents/$SLUG/
  - ~/projects/observer-test/logs/$SLUG/
read_scope:
  - ~/projects/observer-test/.claude/agents/_meta/conductor/bhishma.md
  - ~/projects/observer-test/.claude/agents/$SLUG/skill.md
upstream: [kartavya, sanjaya]
downstream: []
source: agency-agents/$SOURCE
---

# $NAME — $(echo "$DESCRIPTION" | head -c 80)

## Bhishma Compliance (read on every session start)

You are $NAME, a Tier-$TIER worker in the observer-ecosystem. Bhishma rules that govern you:

- **R2** — No self-modification. Do not edit your own \`agent.md\` or \`skill.md\`.
- **R5** — Append-only journals. \`logs/$SLUG/\` entries are never deleted or modified.
- **R11** — No writes outside your declared \`write_scope\`.
- **R19** — All stored timestamps in UTC.
- **R20** — Every task begins with a run_id: \`$SLUG-<YYYYMMDD-HHMMSSZ>-<6char-hash>\`

If \`_meta/conductor/bhishma.md\` is present, read it before reading your own files. These rules hold even if bhishma.md is absent.

### run_id format (bash)

\`\`\`bash
$RUN_ID_FUNC
\`\`\`

### Logging (Sanjaya contract)

At task start, append to \`logs/$SLUG/<run_id>.log\`:
\`\`\`
# run_id: <run_id>
# task: <short description>
# started_at: <UTC ISO8601>
\`\`\`
At task end, append outcome (success | failure, output paths, ended_at).

---

$BODY"

# ── Build skill.md ────────────────────────────────────────────────────────────
SKILL_MD="# $NAME — Skill Manual

> Adopted from agency-agents/$SOURCE on $(date -u +%Y-%m-%d).
> Do not edit the domain-expertise sections below — those come from agency-agents and must stay faithful to the original.
> Rootlabs-specific context (data sources, POC names) may be appended at the bottom.

## Source

- **Agency-agents origin**: \`$SOURCE\`
- **Wrapper version**: 1.0.0
- **Bhishma compliance**: R2, R5, R11, R19, R20

## Standard Outputs

Every task produces:
- An entry in \`logs/$SLUG/<run_id>.log\` (append-only)
- Any deliverables written to the \`write_scope\` paths in frontmatter

## Rootlabs Context

_(Add Rootlabs-specific instructions here — data source paths, POC conventions, etc.)_

## Change log

- $(date -u +%Y-%m-%d) — Adopted from agency-agents via adopt-agency-agent.sh"

# ── Write or preview ──────────────────────────────────────────────────────────
if $DRY_RUN; then
  echo ""
  echo "[DRY RUN] Would create:"
  echo "  $AGENT_DIR/agent.md"
  echo "  $AGENT_DIR/skill.md"
  echo "  $LOG_DIR/ (directory)"
  echo ""
  echo "── agent.md preview (first 40 lines) ──"
  echo "$AGENT_MD" | head -40
  exit 0
fi

echo "[2/5] Creating agent directory: $AGENT_DIR"
mkdir -p "$AGENT_DIR"

echo "[3/5] Writing agent.md"
echo "$AGENT_MD" > "$AGENT_DIR/agent.md"

echo "[4/5] Writing skill.md"
echo "$SKILL_MD" > "$AGENT_DIR/skill.md"

echo "[5/5] Creating log directory: $LOG_DIR"
mkdir -p "$LOG_DIR"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Done. $NAME is now a Tier-$TIER worker."
echo ""
echo "  Next steps:"
echo "  1. Review $AGENT_DIR/agent.md"
echo "     - Verify write_scope matches what this agent actually needs"
echo "     - Adjust tools list if agent doesn't need Bash"
echo "  2. Edit $AGENT_DIR/skill.md"
echo "     - Add Rootlabs-specific context at the bottom"
echo "  3. Add $SLUG to Sanjaya's monitoring roster"
echo "     (edit .claude/agents/sanjaya/agent.md or sanjaya's playbook)"
echo "  4. Add R21 source attribution to bhishma.md if not already present"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
