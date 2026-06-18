# Phase 0 — Decisions Locked (Autonomous Run)

**Date:** 2026-05-14 (05:40 IST)
**Context:** Kartavya said "run all" with full permission. Decisions made by Claude to unblock Phase 2 scaffolding. **All are reversible — override any with a single command tomorrow.**

---

## Decision 1: 5-part app framework — LOCKED as drafted

The framework from the strategy doc + blueprint is adopted verbatim:

| #   | Element                | Value                                                                                                                    |
| --- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| 1   | **Core function**      | Help a user discover the right Rootlabs product for their wellness goal, and learn what's in it.                         |
| 2   | **Core loop**          | Pick goal → see matched products → tap one → read science + reviews → save to wishlist → return for weekly science drop. |
| 3   | **Accessory features** | PDP ingredient deep-dive · Our Science articles · doctor + customer trust · cert PDFs inline · wishlist                  |
| 4   | **Surface area**       | 6 screens (Splash/GoalPicker · For You · Shop · PDP · Saved · Science + Account/HonestReports subroutes)                 |
| 5   | **Retention hook**     | Weekly science drop card on Home — fresh content every Sunday                                                            |

**Override:** edit `_audit/2026-05-14_rootlabs-app-strategy-lock.md` section 5 and re-run.

## Decision 2: Repo location — `apps/rootlabs-learning/` inside observer-test

**Why:** Keeps everything in your single lab notebook repo. VISION.md already references `apps/` as a future path. Easy to extract to a standalone repo later (`git subtree split`).

**Override:** if you want it standalone, run `git subtree split --prefix=apps/rootlabs-learning -b rootlabs-app` then move that branch into a new repo.

## Decision 3: iOS-first

**Why:** Your reference screenshots are iPhone. Expo Go runs both iOS + Android from the same codebase, but the demo preview targets your iPhone. Android works automatically — no separate code path.

**Override:** none needed — Expo is cross-platform by default.

## Decision 4: Brand naming — "Rootlabs" in code, "Root Labs" in display

**Why:** Both forms appear on the live site (`<title>` says "Root Labs", domain says "rootlabs"). Splitting them this way matches modern conventions: identifiers single-word, display copy whatever reads better.

- Code: `RootlabsApp`, `rootlabs-learning`, `services.products`
- Display: "Root Labs · Handpicked in nature."

**Override:** find-replace in `src/design-system/brand.ts` (one file).

## Decision 5: Cart screen — Include as non-functional "Coming Soon"

**Why:** Walks the talk on the "PLUG IN HERE" pattern. When the company sees the Saved → "Buy" CTA → Cart screen saying "Checkout integration pending API access", the pitch is right there in the UI itself. Stronger than just having a doc say it.

**Override:** delete `src/app/cart.tsx` and remove the route — 10 seconds.

---

## Open trade-offs noted but not blocking

- **Bottom tab nav: 3 or 4 tabs?** Going with **4 tabs**: For You · Shop · Science · Saved. Rationale: Science is more important for Rootlabs than for BB/MM (where it's basically absent). The 4th tab gives the science articles real prominence — matches the Rootlabs.co nav ("Our products · Science · About · What else · Blog"). If 4 feels cramped on small phones we drop to 3 and merge Science into a Home card.
- **Account access** — accessible via top-bar profile icon (no bottom tab). Keeps bottom nav focused on shopping discovery.
- **Goal-picker re-entry** — accessible from Account → "Update your goal".

---

Phase 2 scaffolding starts now.
