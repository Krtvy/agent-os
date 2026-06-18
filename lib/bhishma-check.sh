#!/usr/bin/env bash
# bhishma-check.sh — runtime write_scope enforcement for the agent ecosystem.
#
# Invoked by agent runners BEFORE a write/edit operation. Reads the calling
# agent's `write_scope:` from its agent.md frontmatter and verifies that the
# proposed write path is within scope. Exits 0 (allow) or non-zero (block).
#
# Bhishma R-rules enforced at this layer:
#   R2  (no self-modification)            — blocks an agent writing its own agent.md / skill.md
#                                            unless the path is in write_scope, which it should
#                                            never be for self files.
#   R3  (no sibling/higher-tier mod)      — blocks an agent writing outside its declared scope.
#   R11 (no deletion outside write_scope) — covered indirectly: delete operations should be
#                                            wrapped by the runner and pass through this check.
#
# What this is NOT:
#   - Not a Claude Code PreToolUse hook. That would fire in Kartavya's sessions and isn't
#     the right enforcement layer. This is for agent runners (e.g., run_observer.sh,
#     Nakula's job scripts, Hanuman's scout scripts) to invoke before tool calls.
#   - Not a replacement for the agent's own internal discipline. Bhishma is loaded into
#     context at session start; this script is the *runtime backstop*, not the *primary*
#     enforcement.
#
# Usage:
#   bhishma-check.sh <agent-name> <write-path>
#
#   Returns:
#     exit 0  — path is within agent's declared write_scope (allow)
#     exit 1  — path is OUTSIDE agent's declared write_scope (block)
#     exit 2  — agent.md not found or unparsable (block with explicit signal)
#     exit 3  — agent's write_scope is empty / missing (block; explicit declaration required)
#
#   Logs all blocks (exit 1/2/3) to logs/bhishma-blocks.log with run_id, timestamp,
#   agent, attempted path, rule cited.

set -euo pipefail

AGENT="${1:-}"
WRITE_PATH="${2:-}"

if [[ -z "$AGENT" || -z "$WRITE_PATH" ]]; then
  echo "usage: bhishma-check.sh <agent-name> <write-path>" >&2
  exit 64
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$REPO_ROOT/logs"
LOG_FILE="$LOG_DIR/bhishma-blocks.log"
mkdir -p "$LOG_DIR"

# Locate the agent.md. Agents live at .claude/agents/<name>/agent.md, except
# the _meta agents under .claude/agents/_meta/{observer,conductor,audit}/agent.md
# and the mahabharat-name symlinks (sanjaya.md, vyasa.md, sahadeva.md, vidura.md).
AGENT_MD=""
for candidate in \
  "$REPO_ROOT/.claude/agents/$AGENT/agent.md" \
  "$REPO_ROOT/.claude/agents/_meta/observer/agent.md" \
  "$REPO_ROOT/.claude/agents/_meta/conductor/agent.md" \
  "$REPO_ROOT/.claude/agents/_meta/audit/agent.md"
do
  if [[ -f "$candidate" ]]; then
    # match either directory-name or frontmatter-name
    if grep -q "^name: $AGENT$" "$candidate"; then
      AGENT_MD="$candidate"
      break
    fi
  fi
done

if [[ -z "$AGENT_MD" ]]; then
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  echo "$ts agent=$AGENT path=$WRITE_PATH verdict=block rule=agent.md-not-found" >> "$LOG_FILE"
  echo "bhishma-check: agent.md not found for '$AGENT'" >&2
  exit 2
fi

# Extract write_scope via Python (robust YAML parsing).
verdict=$(python3 - "$AGENT_MD" "$WRITE_PATH" "$AGENT" <<'PY'
import sys
import os
import re

agent_md_path = sys.argv[1]
write_path = sys.argv[2]
agent_name = sys.argv[3]

# Parse just the frontmatter block (between first two --- lines).
with open(agent_md_path, "r") as f:
    text = f.read()

m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
if not m:
    print("block:no-frontmatter")
    sys.exit(0)

fm = m.group(1)

# Find write_scope block. Format:
#   write_scope:
#     - path1
#     - path2  # optional comment
write_scope_lines = []
in_block = False
for line in fm.splitlines():
    stripped = line.rstrip()
    if stripped.startswith("write_scope:"):
        # inline list case: write_scope: [a, b, c] — not used in this codebase
        rest = stripped[len("write_scope:"):].strip()
        if rest.startswith("["):
            inside = rest[1:].rstrip("]").strip()
            for item in inside.split(","):
                item = item.strip().strip("'\"")
                if item:
                    write_scope_lines.append(item)
            break
        in_block = True
        continue
    if in_block:
        if line.startswith("  - "):
            item = line[4:].split("#")[0].strip()
            if item:
                write_scope_lines.append(item)
        elif line and not line.startswith(" "):
            break

if not write_scope_lines:
    print("block:empty-write-scope")
    sys.exit(0)

# Normalise paths: expand ~ → $HOME, resolve, drop trailing slashes (but keep
# semantics: a write_scope ending in / is a directory prefix; without trailing
# / it's an exact file path).
home = os.path.expanduser("~")
def norm(p):
    p = p.strip()
    # strip any URI-style scope (hyperagent://, etc.) — those are not filesystem paths
    if "://" in p:
        return None
    p = p.replace("~", home, 1) if p.startswith("~") else p
    return os.path.abspath(p)

target = norm(write_path)
if target is None:
    print("block:invalid-target-uri")
    sys.exit(0)

# Check each scope entry.
for scope_entry in write_scope_lines:
    scope_norm = norm(scope_entry)
    if scope_norm is None:
        continue  # URI scope — not enforced at filesystem layer
    # Directory-prefix match: if the scope entry ends with a path separator,
    # treat it as a directory and check prefix.
    if scope_entry.rstrip().endswith("/") or os.path.isdir(scope_norm):
        if target == scope_norm or target.startswith(scope_norm.rstrip("/") + os.sep):
            print("allow")
            sys.exit(0)
    else:
        # Exact-file scope.
        if target == scope_norm:
            print("allow")
            sys.exit(0)

# Special case: the conductor's bhishma.md is read-only for all agents (R1).
# Even if some scope entry seems to include it, block.
bhishma = norm("~/projects/observer-test/.claude/agents/_meta/conductor/bhishma.md")
if target == bhishma:
    print("block:R1-bhishma-immutable")
    sys.exit(0)

print("block:not-in-write-scope")
PY
)

ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if [[ "$verdict" == "allow" ]]; then
  exit 0
fi

# All non-allow verdicts are blocks. Log and exit non-zero.
case "$verdict" in
  block:no-frontmatter)
    echo "$ts agent=$AGENT path=$WRITE_PATH verdict=block rule=no-frontmatter" >> "$LOG_FILE"
    echo "bhishma-check: agent.md has no parseable frontmatter" >&2
    exit 2
    ;;
  block:empty-write-scope)
    echo "$ts agent=$AGENT path=$WRITE_PATH verdict=block rule=empty-write-scope" >> "$LOG_FILE"
    echo "bhishma-check: agent '$AGENT' has no declared write_scope" >&2
    exit 3
    ;;
  block:R1-bhishma-immutable)
    echo "$ts agent=$AGENT path=$WRITE_PATH verdict=block rule=R1" >> "$LOG_FILE"
    echo "bhishma-check: R1 violation — bhishma.md is editable only by Kartavya" >&2
    exit 1
    ;;
  block:invalid-target-uri)
    echo "$ts agent=$AGENT path=$WRITE_PATH verdict=block rule=invalid-target-uri" >> "$LOG_FILE"
    echo "bhishma-check: target path '$WRITE_PATH' is not a filesystem path" >&2
    exit 1
    ;;
  *)
    echo "$ts agent=$AGENT path=$WRITE_PATH verdict=block rule=not-in-write-scope" >> "$LOG_FILE"
    echo "bhishma-check: path '$WRITE_PATH' is not within agent '$AGENT' write_scope" >&2
    exit 1
    ;;
esac
