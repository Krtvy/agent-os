---
name: Deep Research
description: Multi-source deep research on any topic. Runs parallel searches, reads primary sources, triangulates claims, surfaces dissent, and synthesizes into a structured deliverable with tier-tagged citations.
---

# Deep Research Skill

You are executing a deep research workflow. This is your most thorough research mode — used for topics that require 10+ sources, cross-referencing, and structured synthesis.

## Workflow

### Phase 1: Scoping (before any search)

1. Write a one-sentence research question
2. Identify 3-5 sub-questions that break the topic down
3. List what source types would be most authoritative for this topic
4. Decide output format (webpage for comprehensive, document for evolving, table for comparisons)

### Phase 2: Wide Search (cast the net)

Run parallel searches across multiple angles:
- **Semantic search** for the core topic (ExaSearch with `type: auto`)
- **News search** for recent developments (ExaSearch with `category: news`, date-filtered)
- **Academic/research** if applicable (ExaSearch with `category: research_paper`)
- **Industry sources** for practitioner perspectives

For deep multi-source synthesis, use ExaResearch (async, 1-3 min) — it synthesizes across many sources automatically.

Target: 15-30 sources minimum for a comprehensive deliverable.

### Phase 3: Primary Source Reading

For every key claim:
1. Open the actual source with ExaContents or WebFetch (not just the search snippet)
2. If JS-rendered or paywalled, escalate to Browser tools
3. Extract specific data points, quotes, and methodology
4. Note the author, publication, date, and any conflicts of interest

### Phase 4: Triangulation & Dissent

- Every non-trivial claim needs 2+ independent sources
- Single-source claims get flagged: `[T3, single source]`
- Actively search for counter-arguments: "criticism of X", "problems with X", "X controversy"
- Note where expert consensus exists vs. where there's genuine disagreement

### Phase 5: Synthesis

Structure the output as:

```
## TL;DR
2-4 sentences. Direct answer.

## Key Findings
4-7 bullets with inline citations: [1, T1] [3, T2]

## Detailed Analysis
Depth per finding. Comparisons, counterpoints, contested areas.

## Source Bibliography
[1] Title — Publisher, Date — [Tier]
    URL
    Why cited: one-line note

## Confidence Assessment
Strong evidence / convergent reporting / single source / contested / speculative

## Gaps & Open Questions
What you couldn't find or verify.

## Suggested Next Steps
Concrete follow-up angles.
```

## Quality Checklist

Before delivering, verify:
- [ ] Every claim has a source with tier badge
- [ ] No fabricated citations
- [ ] Counter-evidence surfaced where it exists
- [ ] Publication dates included on all sources
- [ ] Confidence assessment is honest
- [ ] Gaps section is non-empty (there are always gaps)
- [ ] Follow-up suggestions are specific, not generic

## Parallel Research Pattern

For topics with 3+ distinct sub-questions, use subagents:

```
Launch in parallel:
- Agent 1: Sub-question A (search + read + extract)
- Agent 2: Sub-question B (search + read + extract)
- Agent 3: Sub-question C (search + read + extract)

Then: synthesize all findings into unified report
```

This is faster and produces broader coverage than sequential research.

## When NOT to Use This Skill

- Quick factual lookups (just search + answer in chat)
- Single-source questions ("what does X company's website say?")
- Opinion requests (no sources needed)

Use this skill for: market research, competitive analysis, technology evaluations, policy research, industry reports, due diligence.
