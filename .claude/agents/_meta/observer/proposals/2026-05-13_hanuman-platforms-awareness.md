---
id: 20260513-hanuman-platforms-awareness
target: hanuman
mode: adaptation
status: pending
risk_tier: constitutional
mast_codes: [FM-1.3, FM-2.4]
confidence: 85
band: high
proposer: kartavya-via-claude-code
proposed_at: 2026-05-13 04:22 IST
sahadeva_endorsement_required: true
cooling_off_hours: 24
example_run_ids:
  - manual:creator-intel-2026-04-29 (PROJECT-STORY.md walkthrough of using Cruva + Kalodata on 1,384 health creators)
  - manual:2026-05-13-platforms-folder-creation (this session)
  - manual:user-explicit-request "Man, we have to train Hanuman for this, right or not?" 2026-05-13 04:21 IST
---

# Proposal — Wire Hanuman's platform-knowledge files into his procedures

## Rationale

Kartavya imported three platform-knowledge files into `.claude/agents/hanuman/platforms/` on 2026-05-13:

- `apify.md` — built from public WebFetch
- `cruva.md` — imported from `/Users/mosaic/creator-intel/platforms/cruva.com-api.md` (canonical API spec, 28 KB)
- `kalodata.md` — imported from `/Users/mosaic/creator-intel/platforms/kalodata.com-map.md` (canonical UI map, 22 KB)
- `README.md` — index + template

These files contain authoritative platform knowledge — API endpoints, UI navigation, pricing, gotchas, anti-abuse caveats. **But they're inert.** Nothing in Hanuman's spec tells him to read them, when to consult them, or how to use them. Until his procedures are updated, the files do nothing.

This proposal wires the knowledge in.

## Changes proposed (constitutional per R23)

### Change 1 — `agent.md` frontmatter `read_scope`

**Add:**

```yaml
read_scope:
  - ~/projects/observer-test/.claude/agents/hanuman/platforms/ # NEW
```

### Change 2 — `agent.md` frontmatter `mcps`

Currently: `mcps: [kalodata, cruva]`

**Change to:**

```yaml
mcps: [kalodata, cruva, apify]
```

Apify wasn't a wired MCP before — apify.md documents the upcoming integration. If/when the Apify MCP is connected, this matches reality. Until then it's aspirational and that's flagged in apify.md itself.

### Change 3 — `skill.md` P1 (Session bootstrap) — read the platforms directory

**Add to P1:**

```markdown
- Read every file in `.claude/agents/hanuman/platforms/`. These are the canonical knowledge files for the platforms Hanuman uses to look up creator data. At minimum, scan `README.md` (the index) and any file matching a platform named in the task. Default: scan all three (`apify.md`, `cruva.md`, `kalodata.md`) so cross-platform routing decisions are informed.
```

### Change 4 — `skill.md` new procedure P3 (Platform routing)

**New procedure between current P2 and P3:**

```markdown
### P3. Platform routing

Given task input (creator handle / username / URL / partial info), decide which platform(s) to use:

| Need                                                                         | Default platform                                                                                | Fallback                                                                                                 |
| ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| TikTok Shop GMV / sales / category revenue                                   | Kalodata (use `cateIds` to filter category)                                                     | Cruva (formula: `med_gmv_revenue × category_splits[cat]/100`) when Kalodata is locked or creator missing |
| Creator already in Rootlabs affiliate program                                | Cruva (`/v1/affiliate/crm/list` — direct, fast, no rate-limit risk)                             | —                                                                                                        |
| Cross-platform / non-shop creator data (general TikTok, Instagram, etc.)     | Apify (TikTok Scraper, Instagram Scraper Actors)                                                | —                                                                                                        |
| Demographics / audience / creator-profile depth (NOT in your affiliate list) | Cruva Enterprise endpoints (`/v1/affiliate/marketplace/search`) — **gated, needs plan upgrade** | Kalodata creator profile (UI, manual playbook)                                                           |
| Bulk creator enrichment (>100 handles)                                       | Cruva CRM (zero per-call cost) for affiliates; Apify Actor for non-affiliates                   | NEVER bulk-Kalodata. Account lock has happened twice — see kalodata.md § "Critical operational caveat"   |

State the routing decision in the audit `.md`: _"Routing to Cruva (creator is in affiliate list) + Kalodata for verification (last 30d Health revenue)."_

If unsure which platform, **default to manual playbook mode** — return the steps for Kartavya to execute rather than guessing.
```

### Change 5 — `skill.md` P5 (Compute) — extract OR generate manual playbook

**Add a sub-decision:**

```markdown
For each platform used, decide between direct extraction and manual playbook:

- **Direct extraction** when: (a) the relevant MCP/API is wired (Cruva today; Apify when integrated), (b) the call won't hit rate limits or abuse-detection thresholds (Kalodata: never automate at concurrency >1 or beyond ~100 daily calls).
- **Manual playbook** when: (a) the platform is browser-only and unsafe to automate (Kalodata for bulk), (b) the data is gated behind a plan tier we don't have, (c) the auth flow requires interactive login. The playbook is the exact step-by-step Kartavya executes in his own browser — same shape as the playbook sections in `cruva.md` and `kalodata.md`.

Either path produces the same deliverable shape: a `.csv` + `.md` audit in the right POC folder, per Yudhishthira's discipline.
```

### Change 6 — `skill.md` Hard Rules — Kalodata anti-abuse

**Add a hard rule:**

```markdown
- **Never automate Kalodata at concurrency >1 or volume >~100 daily calls.** The platform has aggressive abuse-detection — Rootlabs has been locked out twice (see `kalodata.md` § "Critical operational caveat" and `/Users/mosaic/creator-intel/PROJECT-STORY.md` Phase 5 + Phase 6). For any task requiring bulk Kalodata data, escalate to Kartavya before proceeding. Default action for bulk: generate the manual playbook, don't automate.
```

## What does NOT change

- Hanuman's identity, character, tier.
- His `write_scope` (still `research/creators/`, `logs/hanuman/`, `cache/`).
- Bhishma rules he's bound by.
- His `tools` declaration (still `[Read, Write, WebSearch, WebFetch, Bash]`).

This is **adding procedural and read-scope knowledge** without expanding write authority or weakening any guardrail.

## Risk assessment

**Why this is safe to apply once endorsed:**

- All changes are additive (new procedures, expanded read_scope, new hard rule). Nothing existing is removed or weakened.
- The platform-knowledge files themselves are already on disk (Hanuman can already read them informally if dispatched with explicit instructions).
- The hard rule on Kalodata reduces operational risk (preventing future account locks).
- The platform routing in P3 is _suggestive_ — if Hanuman doesn't recognize the task, the default is the manual playbook, which is the safest path.

**Why it's constitutional anyway:**

- Touches `read_scope` (per R23, this is constitutional regardless of how additive)
- Touches `mcps` (same)
- Adds new procedures (behavioural minimum; combined with frontmatter changes → constitutional)

## Approval path

1. ☑ Kartavya approval (implicit — user directly asked "we have to train Hanuman for this, right or not?")
2. ☐ Sahadeva endorsement — pending first audit Sunday 2026-05-17 10:00 IST
3. ☐ 24-hour cooling-off — starts now (2026-05-13 04:22 IST), elapses 2026-05-14 04:22 IST
4. ☐ One-line rationale field on application: "Wires three existing platform-knowledge files into Hanuman's session bootstrap + routing logic. All changes additive."

## What works today even without this proposal applied

Hanuman is **operationally usable now** for any creator-data task if Kartavya explicitly tells him which platform file to consult:

> _"Hanuman, this is a creator-intel task. Read `platforms/cruva.md` and `platforms/kalodata.md` first. Then look up @<handle>."_

That's a fine workaround for the 4 days until Sahadeva endorses. The proposal just makes platform-awareness automatic at session start instead of opt-in per dispatch.

## What Sahadeva should check on first audit

1. **Verify the three platform files exist** at the paths cited above.
2. **Verify Apify is NOT wired as an MCP yet** (the change to `mcps:` is aspirational; flag if Apify MCP isn't connected and the change is being applied anyway).
3. **Verify no Hanuman runs have happened between proposal-write and audit** that would have benefited from this knowledge but instead used the wrong approach. (Audit `_meta/observer/journal/hanuman.md` for the gap.)
4. **Confirm the Kalodata anti-abuse hard rule is correctly stated** — Sahadeva should not endorse a watered-down version.
5. **Confirm `read_scope` expansion is bounded** — only the `platforms/` directory added, not Hanuman's whole agent dir.

## Files affected when this proposal applies

```
.claude/agents/hanuman/agent.md       — frontmatter: read_scope, mcps
.claude/agents/hanuman/skill.md       — P1 (add platforms read), new P3 routing, P5 sub-decision, new hard rule
.claude/agents/hanuman/CHANGELOG.md   — entry recording the change
_audit/README.md                      — file index update (this proposal moves from proposals/ to approved/)
```

## Files NOT affected

```
.claude/agents/hanuman/platforms/*    — already on disk, no changes needed
Bhishma                                — no rule changes
Other agents' specs                    — no cross-agent changes
```

---

_Proposal authored 2026-05-13 04:22 IST by Claude Code session at Kartavya's explicit request ("we have to train Hanuman for this, right or not?"). Honours the override-count discipline — does not self-apply; awaits Sahadeva endorsement Sunday 2026-05-17 + Kartavya commit after cooling-off._
