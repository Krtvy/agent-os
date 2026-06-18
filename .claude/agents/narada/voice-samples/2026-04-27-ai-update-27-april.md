---
sample_id: 011
date: 2026-04-27
time: 00:18
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
AI Update 27 April

Full day on Shambu's creator profile system today. Classifier work paused, picking it back up tomorrow.

Shipped today: 8 commits. Pipeline runs end to end. Input a TikTok username, it pulls their videos, analyses them with Gemini, fetches their Kalodata GMV, and produces a creator profile card.

Live tests on real creators:

• shopflashsales: full card with briefing rec and voice DNA. $109k 30-day GMV. Best output so far.
• gymselavi, bridgettesbuys: cards produced cleanly.
• shopbyjake, fitnhealthyeve, bbellabianca: $736k, $373k, $384k 30-day GMV pulled.

Kept hitting the Gemini quota wall through the day. Free tier is capped at 20 calls per day on this project, and a single creator burns ~12 calls. Will spin up a fresh key on a different Google account tomorrow and continue the batch run from there.

Tomorrow plan:

1. Switch to fresh Gemini key, validate the new fields populate on a clean run.
2. Run remaining creators on the batch list.
3. Pick classifier back up: wrap tokens.py into one reusable function with retries and error handling.

Repos:

- Classifier: https://github.com/Krtvy/LabeLLM (no changes today)
- Creator profile system: still local, pushing to GitHub once the batch produces cards I am happy with.
