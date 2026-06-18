# `hanuman/platforms/` — Platform Knowledge for Hanuman

Per-platform knowledge files that Hanuman reads when handling reconnaissance tasks. Each file documents one platform Hanuman uses (or guides Kartavya through using) for creator-data lookups.

## Current platforms

| Platform     | Purpose                                                                                                                       | File                         | Status                                                                                                                                                                         |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Apify**    | Web scraping / Actor marketplace · creator data from TikTok, Instagram, etc.                                                  | [`apify.md`](apify.md)       | ✓ Populated from public marketing pages (2026-05-13)                                                                                                                           |
| **Cruva**    | Creator CRM + affiliate operations · API at `api.cruva.com`, MCP at `mcp.cruva.com` · Rootlabs is on the Scale plan ($599/mo) | [`cruva.md`](cruva.md)       | ✓ **Canonical API spec** imported from `/Users/mosaic/creator-intel/platforms/cruva.com-api.md` (mapped live 2026-04-29). 21 endpoints documented, 14 Standard + 7 Enterprise. |
| **Kalodata** | TikTok Shop analytics · GMV / creator / product / store data · Rootlabs is on Professional plan ($83.2/mo)                    | [`kalodata.md`](kalodata.md) | ✓ **Canonical UI map** imported from `/Users/mosaic/creator-intel/platforms/kalodata.com-map.md` (walked top-to-bottom 2026-04-29 in a logged-in session).                     |

**Provenance + Vidura integrated.** The Cruva and Kalodata files are imports of canonical maps Kartavya's earlier Creator Intel Agent built. Vidura's complementary third-party research (dispatched 2026-05-13 04:11 IST) **landed 2026-05-13 04:33 IST** and is now appended to each file: `cruva.md` carries 13 tier-tagged sources B1–B13 (founder info, market positioning, competitive comparisons vs Grin/Aspire/Brevo), `kalodata.md` carries 14 tier-tagged sources A1–A14 (pricing reviews, FastMoss/EchoTik comparison, Trustpilot billing complaints, Reddit-reported data gaps). The originals remain safe at `/Users/mosaic/creator-intel/platforms/`. The canonical maps remain operational ground truth — Vidura's appendices add context, not authority.

**⚠ Kalodata anti-abuse caveat.** Kalodata has aggressively locked Rootlabs's account twice (2026-04-30 and 2026-05-01) when automated calls exceeded concurrency=1 or daily quota caps. The current Hanuman default for any bulk Kalodata work is the **manual playbook** (Hanuman tells Kartavya the steps, Kartavya executes in his own browser). See `kalodata.md` § "Critical operational caveat" and `/Users/mosaic/creator-intel/PROJECT-STORY.md` Phase 5/6.

## Wiring this into Hanuman's procedures (pending)

These files exist but Hanuman's `agent.md` and `skill.md` don't yet route him to them. A proposal at `.claude/agents/_meta/observer/proposals/2026-05-13_hanuman-platforms-awareness.md` covers the spec changes (P1 reads `platforms/`, new P3 platform-routing decision table, new hard rule for Kalodata anti-abuse, `read_scope` and `mcps` updates).

**Status of the proposal:** awaits Sahadeva endorsement on first weekly audit (Sunday 2026-05-17 10:00 IST), then 24-hour cooling-off, then Kartavya commit. Per Bhishma R23.

**Until the proposal lands**, Hanuman can be dispatched with explicit instructions:

> _"Hanuman, this is a creator-intel task. Read `platforms/cruva.md` and `platforms/kalodata.md` first. Then look up @<handle>."_

That works today as a manual workaround.

## What every platform file contains

Standard template — same shape across all three for predictable lookup:

```
# <Platform> — Platform Knowledge for Hanuman

## What this platform is
## What KIND of creator data lives here
## Coverage / scope
## Inputs accepted
## Outputs available
## Comparative: when to prefer this over the others
## Direct extraction (API / Apify / auth)
## Manual playbook (the "tell Kartavya the steps" mode)
## Failure modes
## Pricing / quota
## Login URL
## Sources (tier-tagged)
## What's still unknown
```

The **Manual playbook** section is the most operationally valuable — even when Hanuman can't extract data directly (auth-walled / API-less / unwired), he can give Kartavya the exact navigation sequence ("open URL → click button → paste handle → read field X → save to `pocs/<poc>/raw/...`").

## How Hanuman uses these files

The intended flow:

1. **Kartavya gives Hanuman creator info** — handle, name, partial info.
2. **Hanuman reads this README** to know which platforms exist.
3. **Hanuman picks the right platform** based on what data is needed:
   - Need TikTok Shop GMV? → Kalodata
   - Need general TikTok creator metrics? → Apify (TikTok Scraper Actor)
   - Need contact info / past collaborations? → Cruva
   - Need data across multiple platforms in bulk? → Apify
4. **Hanuman reads that platform's file** for inputs accepted / outputs available / manual playbook.
5. **Hanuman either extracts directly** (if API / MCP / Actor available) **or returns the manual playbook** for Kartavya to execute.
6. **The deliverable lands at** `pocs/<active-poc>/raw/<source>_<handle>_<YYYY-MM-DD>.csv` per the Yudhishthira/Hanuman conventions.

## When to add a new platform

Trigger: a Kartavya task names a platform not in this directory.

Procedure:

1. Run Vidura with a research brief mirroring `_audit/2026-05-13_proposed-poc-workspace.md` style for the new platform.
2. Drop the resulting file at `platforms/<name>.md` matching the template.
3. Add a row to the table above.
4. If the platform needs an MCP integration or API token, that's a constitutional change to `hanuman/agent.md` frontmatter (`mcps:` field) — go through proposal flow per Bhishma R23.

## Refreshing existing files

Platforms change. Refresh triggers:

- **Pricing changes** — when a quoted tier no longer matches reality, re-run Vidura on pricing only.
- **Major UI redesign** — when manual-playbook steps no longer work because the UI moved.
- **New feature launched** — when reviewers / Reddit start mentioning a capability that's not in the file.
- **Default cadence:** annually for any platform that hasn't been refreshed in 12+ months.

When you refresh, **don't edit in place destructively** — write the new file, archive the old as `platforms/<name>_<YYYY-MM-DD>.md`, and put a "Previous versions" pointer in the live file's footer. The audit chain mirrors Bhishma R5 here.

## Pending action

Vidura research is in flight (dispatched 2026-05-13 ~04:11 IST). When complete:

- `cruva.md` and `kalodata.md` land at `platforms/`
- This README's "Status" column flips from ⏳ to ✓
- Update Hanuman's `skill.md` to reference `platforms/` directory at P1 (Session bootstrap) — **note: that's a behavioural change to Hanuman's skill manual, R23 proposal flow applies.** For now, the platforms files exist and Hanuman reads them informally when dispatched on a task.
