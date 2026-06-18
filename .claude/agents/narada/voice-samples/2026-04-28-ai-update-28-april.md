---
sample_id: 012
date: 2026-04-28
time: 04:52
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
AI Update 28 April

Classifier project: added error handling so the API call does not crash when something goes wrong. Auto retry comes next.

Creator profile system: 9-creator batch is running. Now rotates between multiple Gemini keys so we do not hit quota walls. Added a fallback so the card still produces output even when one step breaks. Layout reworked with a summary at the top for fast reading. Repo is now on GitHub.

Side project: AI agent that looks up a creator on Kalodata and Cruva and gives one combined report. Basic setup is done. Still needs:

- A real test run on an actual creator.
- Speed up the Kalodata side. Currently drives a real browser which is slow and breaks when their UI changes.
- A cache so we do not re-fetch the same creator twice.

Tomorrow:

1. Apply 4 fixes to the creator cards and re-run the batch.
2. Classifier: combine the API call, cost tracking, retries, and error handling into one piece I can reuse.

Repos:

- Classifier: https://github.com/Krtvy/LabeLLM
- Creator profile system: https://github.com/Krtvy/creator-profile-api
