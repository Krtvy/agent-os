# Yudhishthira — Install Notes (Claude Code)

This bundle is the Claude Code adaptation of the Hyperagent Yudhishthira agent. Same voice, same disciplines, but the Playbook is a local `.md` file (not a Hyperagent document) and Memories live in a local `.md` file (not platform memories).

## Hyperagent vs. Claude Code — what changed

| Aspect | Hyperagent version | Claude Code version (this bundle) |
|---|---|---|
| Playbook | A document accessed via `ReadDocument` / `UpdateDocument`. Document ID is wired into the system prompt. | A local file at `yudhishthira/playbook.md`. Read via `Read`, updated via `Edit`. |
| Memories | Platform-managed via `CreateMemory` / `UpdateMemory`. Surface contextually. | A local file at `yudhishthira/memories.md`. One entry per fact, append-only on entries. |
| Google Sheets | `SearchIntegrations` / `ConnectIntegration` / `ExecuteIntegration` flow. | An MCP if you have one connected (e.g., a Google Sheets MCP server). Otherwise CSV-export workflow. |
| Backup guardrail | Same — first line of every file-touching task. | Same. |
| Loop (Inspect → Classify → Filter → Compute → Audit → Deliver) | Same. | Same. |
| Deliverable format (.csv + .md per task) | Same. | Same. The bundle includes a `deliverables/` directory. |
| Voice | Dharmaraja, direct, numerate, no filler. | Same. |

## Install

If you already have the observer-ecosystem installed at `~/projects/observer-test/`:

```bash
cd ~/Downloads     # or wherever you have this tarball
tar -xzf yudhishthira-bundle.tar.gz
cp -r yudhishthira-bundle/yudhishthira ~/projects/observer-test/.claude/agents/
mkdir -p ~/projects/observer-test/logs/yudhishthira
ln -sf yudhishthira/agent.md ~/projects/observer-test/.claude/agents/yudhishthira.md
```

If you don't have observer-test set up, you can install Yudhishthira anywhere:

```bash
mkdir -p ~/projects/my-data-project/.claude/agents
cp -r yudhishthira-bundle/yudhishthira ~/projects/my-data-project/.claude/agents/
cd ~/projects/my-data-project
ln -sf .claude/agents/yudhishthira/agent.md .claude/agents/yudhishthira.md
mkdir -p logs/yudhishthira
git init && git add . && git commit -m "yudhishthira: initial install"
```

Then update `agent.md` if your project root is not `~/projects/observer-test/` — the `write_scope` and `read_scope` frontmatter paths need to match your actual layout.

## After install — first session

1. Open a Claude Code session in the project root:
   ```bash
   cd ~/projects/observer-test
   claude --agent yudhishthira
   ```

2. Yudhishthira will (or should) read `playbook.md` and `memories.md` first thing. Both are empty at install.

3. Feed it a small task to verify the Loop works end-to-end:
   ```
   here's a tiny test file at /tmp/test.csv with 3 rows. count them
   and tell me the sum of column 'amount'.
   ```

   The agent should:
   - Ask the backup question.
   - Profile the file (shape, columns, dtypes).
   - State the task class (`single-number`).
   - Declare filters (likely "none — count all rows").
   - Compute via pandas in Bash.
   - Cross-check (sum two ways).
   - Save a `.md` to `deliverables/` (CSV optional for single-number tasks).

4. Once a real pattern emerges, teach it with: `remember this — <pattern>`. Watch `playbook.md` or `memories.md` get a new entry.

## Google Sheets

This bundle does not include a Google Sheets connector. Two ways to add one:

**Option A — MCP**: install a Google Sheets MCP server in Claude Code's MCP configuration. The agent will see it under the `mcps_optional` slot in frontmatter and use it for read-only access to your sheets.

**Option B — CSV export**: have your intern download sheets as CSV (`File → Download → CSV`) and place them in a known path. Yudhishthira reads them like any other file.

Write-back to Sheets is intentionally not enabled. The system prompt's "Phase 2" section is the placeholder for when you provision a dedicated service account.

## Optional integration with the observer-ecosystem

If you have the observer-ecosystem installed:

1. `bhishma.md` will be read at session start, and Yudhishthira will follow R2, R5, R11, R19, R20.
2. Once Sanjaya runs, it will read `logs/yudhishthira/*.log` and start journaling Yudhishthira's behavior. After ≥3 distinct example_run_ids that fit a pattern, Sanjaya may draft a proposal to update `yudhishthira/skill.md` — same approval-gate flow as the other Tier-0 workers.
3. Sahadeva's weekly audit will include Yudhishthira's heartbeat (last log entry, agent silence detection, run_id format conformance).

If you don't have the observer-ecosystem, none of that fires. Yudhishthira just runs standalone, which is the intended fallback.

## Files in this bundle

```
yudhishthira-bundle/
├── README.md                          quick install reference
├── install.sh                         minimal installer (copy + symlink)
├── docs/
│   └── INSTALL_NOTES.md               this file
├── yudhishthira/
│   ├── agent.md                       identity + posture + structure
│   ├── skill.md                       procedures
│   ├── playbook.md                    empty starter playbook (procedures)
│   ├── memories.md                    empty starter memories (atomic facts)
│   └── deliverables/.gitkeep          output directory
└── yudhishthira-hyperagent-prompt.md  the original Hyperagent prompt verbatim, for reference
```
