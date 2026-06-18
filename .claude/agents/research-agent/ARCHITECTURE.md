# Research Agent — Architecture Guide

## agent.md vs SKILL.md — Which to Use?

### The Problem with agent.md (Monolithic Approach)

A single `agent.md` file puts everything — identity, methodology, domain knowledge, workflows, reference data — into one massive prompt that's loaded every time. This:

- **Wastes tokens** — domain knowledge about supplements loads even when researching AI policy
- **Doesn't scale** — as you add more research workflows, the file becomes unwieldy
- **Can't evolve** — adding a new research capability means editing a fragile monolith
- **No progressive disclosure** — Claude reads everything upfront vs. loading what it needs

### The Skill-Based Architecture (Recommended)

Based on Anthropic's official Agent Skills framework (Oct 2025), the proper architecture uses **layers**:

```
CLAUDE.md          → WHO you are (identity, always loaded, ~50 lines)
  ├── Rules        → WHAT you know (domain knowledge, loaded when relevant)
  └── Skills       → HOW you work (workflows, loaded on demand)
      └── docs/    → Reference data (loaded by skills as needed)
```

This maps to Claude Code's four configuration layers:

| Layer | File | Trigger | Purpose |
|-------|------|---------|---------|
| **CLAUDE.md** | `CLAUDE.md` | Always loaded | Core identity, methodology, tool index |
| **Rules** | `.claude/rules/*.md` | Path-based or always | Domain knowledge (source tiers, industry data) |
| **Skills** | `.claude/skills/*/SKILL.md` | On-demand (when relevant) | Research workflows (deep research, brand audit, etc.) |
| **Docs** | `docs/*.md` | Referenced by skills | Pre-researched data, loaded as needed |

### Why This Is Better for a Research Agent

1. **Progressive disclosure** — Claude loads the skill name + description (~100 tokens) upfront. The full SKILL.md (~500-1000 tokens) only loads when that research type is triggered. Reference docs (~10K+ tokens) only load when the skill references them. This is how Anthropic designed it.

2. **Composable** — Add a new research workflow (e.g., "regulatory-research") by creating a new SKILL.md. No existing files change.

3. **Evolving** — As you do more research, your skills improve. Edit the SKILL.md for a specific workflow without touching your identity or other skills.

4. **Shareable** — Skills are portable. Your "brand-audit" skill can be shared with other agents or team members.

5. **Domain-flexible** — The DTC supplements rule loads when relevant but doesn't clutter context when you're researching something else.

---

## File Structure

```
research-agent/
├── CLAUDE.md                              # Core identity (always loaded)
├── ARCHITECTURE.md                        # This file — how the system works
│
├── .claude/                               # Claude Code config directory
│   ├── skills/
│   │   ├── deep-research/
│   │   │   └── SKILL.md                   # Multi-source deep research workflow
│   │   ├── brand-audit/
│   │   │   └── SKILL.md                   # Brand competitive analysis
│   │   ├── market-intel/
│   │   │   └── SKILL.md                   # Market sizing and trend analysis
│   │   └── growth-playbook/
│   │       └── SKILL.md                   # Tactical growth recommendations
│   │
│   └── rules/
│       ├── source-tiers.md                # Detailed source classification
│       └── dtc-supplements.md             # Industry context and benchmarks
│
└── docs/                                  # Reference data (loaded by skills)
    ├── doc_brand_case_studies.md           # 8 brand deep-dives (49KB)
    ├── doc_personalization_report.md       # Data & personalization (58KB)
    ├── research_acquisition.md            # Acquisition tactics (30KB)
    ├── research_retention.md              # Retention strategies (33KB)
    ├── research_conversion.md             # Conversion & AOV (29KB)
    └── research_habits.md                 # Habit formation (33KB)
```

**Note:** The `claude-config/` folder in this download mirrors what goes into `.claude/` in your actual project. Rename it to `.claude/` when setting up:

```bash
mv claude-config .claude
```

---

## How Progressive Disclosure Works

When you start a conversation:

```
1. CLAUDE.md loads → Claude knows: "I'm a research agent. I have 4 skills available."
   Token cost: ~800 tokens (just identity + skill index)

2. User asks: "Research what DTC supplement brands are doing for retention"
   → Claude sees "growth-playbook" and "brand-audit" skills are relevant
   → Claude reads growth-playbook/SKILL.md (~1200 tokens)
   → SKILL.md references docs/research_retention.md
   → Claude reads that file (~8000 tokens)
   → dtc-supplements.md rule also loads (relevant context)

3. Claude executes the research workflow defined in the skill
   → Searches for additional recent data
   → Synthesizes with pre-researched data from docs/
   → Delivers structured report with tier-tagged sources
```

Total context used: ~10K tokens of relevant knowledge
Without skills (monolithic): Would have loaded ~50K+ tokens of everything

---

## How to Evolve Your Skills Over Time

### Adding a New Research Capability

1. Create a new directory: `.claude/skills/your-new-skill/`
2. Write `SKILL.md` with frontmatter (name, description) + workflow
3. Add a line to CLAUDE.md's "Available Skills" section
4. Done — Claude will discover and use it automatically

### Improving an Existing Skill

After a research session reveals a better workflow:
1. Edit the relevant `SKILL.md` to incorporate what worked
2. If new reference data was generated, save it to `docs/`
3. Update the skill's file references

### Adding Domain Knowledge

When you research a new industry:
1. Save key findings to `docs/new-industry-data.md`
2. Create a new rule: `.claude/rules/new-industry.md`
3. Reference the docs from relevant skills

### Capturing Learnings

After each major research session, ask yourself:
- Did the workflow work well? → Update the SKILL.md
- Did I discover new benchmarks? → Update or create a rule
- Did I generate reference data worth keeping? → Save to docs/
- Did I need a research type that doesn't have a skill? → Create one

---

## Claude Code Setup

```bash
# Clone or create the project
cd research-agent

# Rename config directory
mv claude-config .claude

# Start Claude Code
claude

# Claude automatically reads CLAUDE.md + discovers skills and rules
# Try: "Do a deep research on X" → triggers deep-research skill
# Try: "Audit Bloom Nutrition's strategy" → triggers brand-audit skill
# Try: "Build a growth playbook for my supplement brand" → triggers growth-playbook skill
```

### MCP Servers (for web search capabilities)

Add to `~/.claude/claude_code_config.json`:

```json
{
  "mcpServers": {
    "exa": {
      "command": "npx",
      "args": ["-y", "exa-mcp-server"],
      "env": {
        "EXA_API_KEY": "your-exa-api-key"
      }
    }
  }
}
```

This gives Claude access to ExaSearch, ExaContents, ExaResearch, and ExaFindSimilar — the same tools available in Hyperagent.
