# `lib/` — Runtime enforcement scripts

Scripts shared across the agent ecosystem. They are tools the runners and (when wired in) the harness invoke; they are not themselves agents.

## `bhishma-check.sh`

Runtime `write_scope` enforcement. Given an agent name and a target path, returns 0 (allow) or non-zero (block). Reads the agent's `write_scope:` from its `agent.md` frontmatter.

**Usage from a runner:**

```bash
lib/bhishma-check.sh sanjaya "$target_path" || {
  echo "Write blocked by Bhishma" >&2
  exit 1
}
```

**Exit codes:**

| Code | Meaning                                                                           |
| ---- | --------------------------------------------------------------------------------- |
| 0    | allow — path is within the agent's declared `write_scope`                         |
| 1    | block — path is outside `write_scope` (or R1 `bhishma.md` immutability triggered) |
| 2    | block — agent.md not found or unparsable                                          |
| 3    | block — agent's `write_scope` is empty / missing (explicit declaration required)  |
| 64   | usage error — missing required arguments                                          |

**Logs.** Every block is logged to `logs/bhishma-blocks.log` with `run_id`-style format:

```
2026-05-11T17:56:50Z agent=sanjaya path=/.../arjuna/agent.md verdict=block rule=not-in-write-scope
```

Sahadeva ingests this log during weekly audit.

## `bhishma-pretool-hook.sh`

Claude Code `PreToolUse` hook wrapper. Reads the tool-call JSON from stdin, extracts the target path, and dispatches to `bhishma-check.sh`.

**Activation discipline.** The hook is opt-in via the `$BHISHMA_AGENT` environment variable:

- **`$BHISHMA_AGENT` unset** → hook exits 0 immediately. Safe default for Kartavya's interactive sessions (the human is not a member of the Tier chain and has full repo access by design).
- **`$BHISHMA_AGENT=<name>`** → hook enforces that agent's `write_scope` for all write-shaped tool calls (`Edit`, `Write`, `MultiEdit`, `NotebookEdit`).

This design lets the same `.claude/settings.json` work for both Kartavya sessions and agent-runner sessions — only the env var differs.

### Wiring into `.claude/settings.json` — status: **WIRED**

As of 2026-05-12 00:05 IST, both hooks are wired into `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit|NotebookEdit",
        "hooks": [
          { "type": "command", "command": "lib/bhishma-pretool-hook.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [{ "type": "command", "command": "lib/post-tool-hook.sh" }]
      }
    ]
  }
}
```

Agent runners (`run_observer.sh`, `run_sahadeva.sh`) export the activation env vars:

```bash
export BHISHMA_AGENT=sanjaya
export BHISHMA_RUN_ID="${DATE_UTC}-sanjaya-${HHMMSS_UTC}"
claude -p --agent observer "..."
```

Kartavya's interactive sessions do NOT set `BHISHMA_AGENT`; the hooks no-op for those sessions and the harness behaves as before.

### Constitutional override note

R23 classifies any change touching the approval-gate logic as `constitutional` — requiring Kartavya approval + Sahadeva endorsement + 24-hour cooling-off. **Sahadeva endorsement is not available** because Sahadeva has not yet run (first audit fires 2026-05-17 10:00 IST). Kartavya explicitly directed this wiring via auto-mode 2026-05-12 00:04 IST, accepting that the strict R23 path was overridden.

This is the **second** Claude-Code-mediated constitutional override in this ecosystem (R23 itself was the first). The pattern — Kartavya directs constitutional change → Claude Code applies → discipline documented after the fact — should be flagged by Sahadeva on first run as a calibration question: does the override pattern become a habit, or stay rare?

Full attribution chain: `_audit/2026-05-12_hooks-wired.md`.

When ready: read the test-set first run results (after Phase 2 G3 ships), confirm Sahadeva is functional, then wire the hook in and observe for a week.

## `trace-writer.sh`

**Phase 3 G5.** Append-only writer for structured trace events that sit alongside Sanjaya's narrative journals. Consumed by Sahadeva's P5 (quantitative trends) and P10 (test-set evaluation).

Schema lives in `lib/trace-schema.md` (v1). Storage: `.claude/agents/_meta/observer/traces/<agent>/<run_id>.json`, one JSON document per run.

**Subcommands:**

```bash
lib/trace-writer.sh init <agent> <run_id>
lib/trace-writer.sh tool-call <agent> <run_id> <event-json>
lib/trace-writer.sh bhishma-block <agent> <run_id> <rule> <attempt>
lib/trace-writer.sh decision <agent> <run_id> <desc> <choice>
lib/trace-writer.sh finalise <agent> <run_id> <completed|errored|blocked>
```

**Concurrency.** In-process Python `fcntl.LOCK_EX` on the trace file. Cross-platform (Linux + macOS); does not depend on the `flock` binary.

**Failure mode.** Trace recording must NOT abort the agent's primary work. The narrative journal is the trust layer; the trace is the audit layer. If the writer fails, the caller logs and continues.

## `post-tool-hook.sh`

**Phase 3 G1C.** Claude Code `PostToolUse` hook that records every tool call into the trace via `trace-writer.sh`. Same opt-in discipline as `bhishma-pretool-hook.sh` — requires both `$BHISHMA_AGENT` and `$BHISHMA_RUN_ID` to be set; no-op otherwise.

**Wire-up (when ready):**

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [{ "type": "command", "command": "lib/post-tool-hook.sh" }]
      }
    ]
  }
}
```

The hook **sanitises** before writing — full payloads, credentials, and PII are dropped. Only tool name, target path (for write-shaped tools), short summary, tokens, duration, and verdict are recorded. The discipline matches `lib/trace-schema.md` § "Field sanitisation rules."

**Failure mode.** `set -uo pipefail` is used deliberately — **not** `set -e`. We never want trace-recording errors to bubble back to Claude Code and interrupt the agent. Errors log to stderr; the hook always exits 0.

## `yudhi-py.sh`

**For Yudhishthira's pandas path (P5b) when running locally via Claude Code.**

System `python3` does not have pandas. The project's `.venv/bin/python3` (Python 3.12 + pandas 3.0.x, installed via `uv`) does. `yudhi-py.sh` is a one-line wrapper that ensures Yudhishthira's pandas invocations use the venv Python rather than bare `python3` (which would fail with `ModuleNotFoundError: No module named 'pandas'`).

**Usage:**

```bash
lib/yudhi-py.sh -c "import pandas, sys; print(pandas.__version__)"
lib/yudhi-py.sh path/to/script.py arg1 arg2
```

**Exit codes:** 0 (Python ran, its own exit preserved) · 1 (`.venv/bin/python3` missing — emits rebuild instructions) · 64 (usage error).

**Rebuild the venv if needed:**

```bash
cd /Users/mosaic/projects/observer-test
uv venv
uv pip install pandas
```

The wrapper is referenced explicitly in `.claude/agents/yudhishthira/skill.md` § P5b so the dependency is auditable.

## `yudhi-fetch.sh`

**For Yudhishthira's P0 Sheets-URL access procedure when running locally.**

Resolves a Google Sheets URL or local file path to a local CSV that pandas can read. Three behaviours:

| Input shape                                                             | Behaviour                                                                                                                                                      |
| ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Local file path                                                         | Returns the path unchanged.                                                                                                                                    |
| Google Sheets URL where the sheet is shared "anyone with link can view" | Fetches the public CSV export, writes to `/tmp/yudhi-sheet-<id>-gid<n>-<epoch>.csv`, echoes the local path.                                                    |
| Google Sheets URL where the sheet is private                            | Emits an auth-wall error with three clear options: (1) make the sheet public-view, (2) download as CSV manually, (3) provision Phase 2 Google account. Exit 2. |

**Usage:**

```bash
lib/yudhi-fetch.sh 'https://docs.google.com/spreadsheets/d/<id>/edit?gid=0'
lib/yudhi-fetch.sh /path/to/already-local.csv
lib/yudhi-fetch.sh '<url>' /custom/output/path.csv
```

**Exit codes:** 0 (success; stdout has the local CSV path) · 1 (network / HTTP error) · 2 (auth wall / private sheet) · 64 (usage error / unrecognised input).

**Bash 3.2 compatibility note.** The regex patterns are assigned to variables before use in `[[ =~ ]]` conditionals. This is the documented workaround for macOS's default Bash 3.2, which chokes on inline patterns containing `&`. Don't inline the regexes back — the script will break.

The wrapper is referenced explicitly in `.claude/agents/yudhishthira/skill.md` § P0 (Phase 1 local path).

## Phase 3 deliberate skips

Two Phase 3 / Phase 4 items were _not_ built this session, with documented reasoning:

### G7 — Sanjaya journal compaction (not yet needed)

The largest existing journal is `_meta/observer/journal/research-agent.md` at ~49 KB after 13 runs. The playbook ([14, T1] Anthropic Effective Context Engineering) recommends rolling compaction around the 200 KB mark. Extrapolating at the current growth rate, that's ~3 months away. Building the compaction script before then is premature optimisation; the trigger ("any agent journal >200 KB") is documented in `_audit/2026-05-11_post-phase-2-audit.md` as a next-session signal.

### G1B — Haiku semantic pre-tool validator (not yet justified)

The playbook framed this as **conditional** on Phase 2-3 signal warranting it. Concretely: G1A (declarative `write_scope` gate) is paper-only until wired in, G1C (post-action trace recording) is paper-only until wired in, and Sahadeva has never produced a report. The cost of the semantic validator (one Haiku call before every tool call across the ecosystem) is non-trivial. Until G1A + G1C surface a real class of violations that declarative rules can't catch, G1B is over-engineering against a hypothetical.

Trigger to revisit: 3 weeks of Sahadeva reports showing recurring violations that pre-tool-call `write_scope` checking _cannot_ see (e.g., semantic intent issues — "this write technically passes scope but is being used to bypass Bhishma R7 indirectly").

## Testing

The scripts have been unit-tested with synthetic inputs:

```bash
# In-scope write succeeds
lib/bhishma-check.sh sanjaya ~/projects/observer-test/.claude/agents/_meta/observer/journal/arjuna.md
# exit 0

# Out-of-scope write blocks
lib/bhishma-check.sh sanjaya ~/projects/observer-test/.claude/agents/arjuna/agent.md
# exit 1, logged

# R1 bhishma.md immutability
lib/bhishma-check.sh vyasa ~/projects/observer-test/.claude/agents/_meta/conductor/bhishma.md
# exit 1, rule=R1

# Unknown agent
lib/bhishma-check.sh shakuni <anything>
# exit 2
```

No automated test harness yet — testing is manual at the script level. If/when this layer matures, a `lib/test-bhishma-check.sh` would be a sensible addition.

## Bhishma rule mapping

| Rule                                               | Enforced by `bhishma-check.sh`? | Notes                                                                                                                                                      |
| -------------------------------------------------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R1 (bhishma.md immutable)                          | ✅ explicit case                | Hardcoded in the Python checker                                                                                                                            |
| R2 (no self-modification)                          | ⚠️ indirectly                   | Agents shouldn't have their own `agent.md` in `write_scope`. If they do, this layer cannot detect the violation — Sahadeva must catch it via weekly audit. |
| R3 (no sibling/higher-tier mod)                    | ✅ via write_scope              | Each agent's `write_scope` excludes sibling agents by construction                                                                                         |
| R4 (every applied diff cites an approved proposal) | ❌ not here                     | Sanjaya's `approval_polling` skill enforces this in its own logic                                                                                          |
| R11 (no deletion outside write_scope)              | ⚠️ only if delete is wrapped    | The runner must invoke this check before any `rm`/`unlink`; otherwise this layer is blind to deletes                                                       |

## Scope of this layer

This is **runtime defense in depth**, not the primary enforcement. The primary enforcement is each agent's loading of `bhishma.md` at session start and validating its own actions against R1–R23 internally. `bhishma-check.sh` is the backstop — it catches what the agent's self-discipline misses.

The playbook (`_audit/2026-05-11_multi-agent-playbook.md` §3) names this pattern explicitly: trained-in policy (impossible without retraining) → prompt-loaded policy (current Bhishma) → runtime gate (this layer) → post-action audit (Sanjaya journal + Sahadeva weekly). No single layer is sufficient. Stack them.
