---
sample_id: 010
date: 2026-04-26
time: 02:17
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
AI Update 26 April

Shipped today:

Built tokens.py for the classifier project. It reads token usage from each API response and calculates the dollar cost per call. A single call is fractions of a cent, but tracking this matters once we are running at volume.

Started on the creator profile system Shambu asked me to build. Set up the project with FastAPI, Apify, and Google Gemini. Phase 1 is working end to end locally: given a TikTok creator username, the API fetches their latest 10 videos and returns the metadata (IDs, durations, average length). Includes retry logic for network failures.

Will request the API keys from Shambu tomorrow (Apify, Kalodata, Gemini). Once those are in, I can run it against a real creator and move into Phase 2 (transcripts) and Phase 3 (visual analysis).

Tomorrow plan:

1. Consolidate tokens.py with the existing classifier code into a single reusable function with proper retry and error handling.
2. Creator profile system: get the keys from Shambu, run a real end to end test, push to GitHub, then begin Phase 2 (transcripts).

Links:

- https://github.com/Krtvy/LabeLLM (classifier with tokens.py)
- Creator profile system: local for now, pushing to GitHub once I have the keys and a successful real run.
