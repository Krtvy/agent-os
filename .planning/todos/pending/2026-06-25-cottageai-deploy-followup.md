---
created: 2026-06-25T21:45:00
title: CottageAI — complete deploy + wire waitlist
area: general
files:
  - agents/cottageai/app/page.tsx
  - agents/cottageai/components/Cursor.tsx
---

## Problem

CottageAI landing page deployed to Vercel but two things are incomplete:

1. **DNS not pointed** — A record `@ → 76.76.21.21` needs to be added at name.com. Until then, cottageai.app is not live (preview URL works: https://cottageai-three.vercel.app).

2. **Waitlist form unconnected** — The email form on the CTA section changes a button label on submit but sends nothing anywhere. No emails are being collected.

## Solution

**DNS (user action, ~2 min):**
- Go to name.com → cottageai.app → Manage DNS Records
- Add: A record, host `@`, value `76.76.21.21`, TTL 300
- Also add: A record, host `www`, value `76.76.21.21`

**Waitlist wiring (~15 min, Claude does):**
- Add a Next.js API route: `app/api/waitlist/route.ts`
- On POST, write email to Notion database using existing Notion token (`ntn_325551...` in `~/agents/ai-knowledge-feed/.env`)
- Create a "CottageAI Waitlist" Notion database (Name + Email + Timestamp)
- Update the form in page.tsx to POST to `/api/waitlist`

**Also pending:**
- Run `~/move-todays-work.ps1` to move Draupadi/Abhimanyu/Bhima agents from `~/projects/observer-test/` to `~/agents/observer-test/`
- Vercel project is named `cottageai` under scope `gitsy`
