#!/usr/bin/env bash
# deploy.sh — install the observer-ecosystem into a target path.
#
# Usage:
#   bash deploy.sh [TARGET]
#
# TARGET defaults to ~/projects/observer-test
#
# What this does:
#   1. Renames dot-claude/ → .claude/ in the bundle
#   2. Copies the entire bundle to TARGET (preserving directory structure)
#   3. Makes scripts/*.sh executable
#   4. Creates the top-level symlinks under TARGET/.claude/agents/
#      so `claude --agent <name>` resolves
#   5. Prints next-step instructions
#
# This script is idempotent — running it twice leaves a clean install.
# It does NOT overwrite existing files in TARGET except for the bundle's
# own files; if you have local edits to skill.md or agent.md, back them up first.

set -euo pipefail

TARGET="${1:-$HOME/projects/observer-test}"
BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> deploy.sh: installing observer-ecosystem to $TARGET"
echo "    bundle source: $BUNDLE_DIR"

# Sanity check
if [[ ! -d "$BUNDLE_DIR/dot-claude" ]]; then
  echo "ERROR: bundle does not contain dot-claude/ — are you running from inside the extracted tarball?"
  exit 1
fi

# Step 1 — rename dot-claude → .claude inside the bundle (only first time)
if [[ -d "$BUNDLE_DIR/dot-claude" && ! -d "$BUNDLE_DIR/.claude" ]]; then
  echo "==> renaming dot-claude → .claude in bundle"
  mv "$BUNDLE_DIR/dot-claude" "$BUNDLE_DIR/.claude"
fi

# Step 2 — create target and copy
mkdir -p "$TARGET"
echo "==> copying bundle to $TARGET"
# Copy with -a (preserve), but skip self
rsync -a --exclude='deploy.sh' --exclude='README.md' "$BUNDLE_DIR/" "$TARGET/"
# Copy README and deploy.sh too (so the install is self-contained at TARGET)
cp "$BUNDLE_DIR/README.md" "$TARGET/README.md"
cp "$BUNDLE_DIR/deploy.sh" "$TARGET/deploy.sh"

# Step 3 — make scripts executable
echo "==> chmod +x scripts/*.sh"
chmod +x "$TARGET/scripts/"*.sh

# Step 4 — top-level symlinks under .claude/agents/
echo "==> creating top-level agent symlinks"
cd "$TARGET/.claude/agents"

# Helper: create symlink only if not already correct
mklink() {
  local link="$1"
  local target="$2"
  if [[ -L "$link" && "$(readlink "$link")" == "$target" ]]; then
    echo "    ok    $link → $target"
  else
    rm -f "$link"
    ln -s "$target" "$link"
    echo "    new   $link → $target"
  fi
}

mklink "vyasa.md"    "_meta/conductor/agent.md"
mklink "sanjaya.md"  "_meta/observer/agent.md"
mklink "sahadeva.md" "_meta/audit/agent.md"
mklink "vidura.md"   "vidura/agent.md"
mklink "hanuman.md"  "hanuman/agent.md"
mklink "narada.md"   "narada/agent.md"
mklink "arjuna.md"   "arjuna/agent.md"
mklink "nakula.md"   "nakula/agent.md"

cd "$TARGET"

echo
echo "==> done."
echo
echo "Next steps:"
echo "  1. cd $TARGET"
echo "  2. git init && git add . && git commit -m 'bhishma: initial constitution + 8 agents'"
echo "  3. Read docs/BOOTSTRAP.md for the phased bring-up order."
echo "  4. Drop voice samples into .claude/agents/narada/voice-samples/"
echo "  5. Edit .claude/agents/nakula/jobs.yml (start from scripts/jobs.yml.example)"
echo "  6. crontab -e and paste from scripts/crontab.example"
echo
echo "Agent symlinks:"
ls -l "$TARGET/.claude/agents/"*.md 2>/dev/null | sed 's|^|  |'
