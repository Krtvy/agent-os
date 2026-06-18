---
sample_id: 016
date: 2026-05-02
time: 03:17
mode: mayank-update
recipient: mayank
medium: slack
captured_by: kartavya
captured_on: 2026-05-11
quality: real-historical
self_rating: 6/10
notes: From historical Slack DM dump. Real production voice. Use as training signal but flag identified weaknesses (see RATING-NOTES.md) rather than replicate them.
---

Hey Mayank,
AI Update 2 May

Noted on yesterday. Was not getting dedicated time to sit on AI because of the move. Moved into the new flat today, so more focused time for AI from here.

Three things from these days:

Classifier project: closed the first stage. Built the base function that handles every AI call. Learned how to wire up auth, error handling, retries, cost tracking, and streaming, and how to wrap them all behind one clean interface. Prompt engineering next.

Creator profile system: shipped v1.1.0. Built outreach contact extraction, posting cadence, earnings per video, and a brand fit score. Learned how to backfill cached profiles cheaply without re-running the full pipeline.

AI agent (Cruva + Kalodata): cracked Kalodata's internal API. Now pulling real Health category numbers directly from their endpoint instead of scraping the UI. Learned how to capture internal endpoints from network traffic and how to design a fallback when one platform's free tier does not cover the universe.

Repos:
- Classifier: https://github.com/Krtvy/LabeLLM
- Creator profile system: https://github.com/Krtvy/creator-profile-api

Good night.
