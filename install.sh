#!/usr/bin/env bash
# install.sh — install Yudhishthira into a Claude Code project.
#
# Usage:
#   bash install.sh [TARGET]
#
# TARGET defaults to ~/projects/observer-test
#
# Effect:
#   1. Copies yudhishthira/ into TARGET/.claude/agents/
#   2. Creates TARGET/.claude/agents/yudhishthira.md as a symlink
#   3. Creates TARGET/logs/yudhishthira/ (Yudhishthira's append-only log dir)
#   4. Prints next-step instructions.
#
# Idempotent. Re-running leaves a clean install. Does NOT overwrite
# existing playbook.md or memories.md if they already exist in TARGET.

set -euo pipefail

TARGET="${1:-$HOME/projects/observer-test}"
BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> installing yudhishthira to $TARGET"
echo "    bundle source: $BUNDLE_DIR"

if [[ ! -d "$BUNDLE_DIR/yudhishthira" ]]; then
  echo "ERROR: bundle does not contain yudhishthira/ — are you running from inside the extracted tarball?"
  exit 1
fi

# Ensure target tree exists
mkdir -p "$TARGET/.claude/agents"
mkdir -p "$TARGET/logs/yudhishthira"

AGENT_DIR="$TARGET/.claude/agents/yudhishthira"

if [[ -d "$AGENT_DIR" ]]; then
  echo "==> $AGENT_DIR already exists — preserving playbook.md and memories.md, refreshing agent.md + skill.md"
  cp "$BUNDLE_DIR/yudhishthira/agent.md"  "$AGENT_DIR/agent.md"
  cp "$BUNDLE_DIR/yudhishthira/skill.md"  "$AGENT_DIR/skill.md"
  # Only copy playbook / memories if they don't already exist
  [[ -f "$AGENT_DIR/playbook.md" ]]  || cp "$BUNDLE_DIR/yudhishthira/playbook.md"  "$AGENT_DIR/playbook.md"
  [[ -f "$AGENT_DIR/memories.md" ]]  || cp "$BUNDLE_DIR/yudhishthira/memories.md"  "$AGENT_DIR/memories.md"
  mkdir -p "$AGENT_DIR/deliverables"
else
  echo "==> copying yudhishthira/ → $AGENT_DIR"
  cp -r "$BUNDLE_DIR/yudhishthira" "$AGENT_DIR"
fi

# Top-level symlink so `claude --agent yudhishthira` resolves
cd "$TARGET/.claude/agents"
if [[ -L "yudhishthira.md" && "$(readlink yudhishthira.md)" == "yudhishthira/agent.md" ]]; then
  echo "    ok    yudhishthira.md → yudhishthira/agent.md"
else
  rm -f "yudhishthira.md"
  ln -s "yudhishthira/agent.md" "yudhishthira.md"
  echo "    new   yudhishthira.md → yudhishthira/agent.md"
fi

cd "$TARGET"

echo
echo "==> done."
echo
echo "Next steps:"
echo "  1. cd $TARGET"
echo "  2. (optional) git add . && git commit -m 'yudhishthira: initial install'"
echo "  3. claude --agent yudhishthira"
echo "  4. First task suggested: a tiny CSV smoke test so you see the full Loop."
echo
echo "Files:"
ls -l "$AGENT_DIR/" 2>/dev/null | sed 's|^|  |'
