---
sample_id: 017
date: 2026-05-04
time: 02:40
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
AI Update 4 May
Classifier project: started Phase 2 tonight. The AI now takes a "personality" along with the question, so the same model can answer the same question differently each time.
Token Saviour: built a small tool that plugs into Claude Code. It cuts the extra words sent to the AI every time, so each chat costs a little less. Running automatically now.
Creator profile system: closed. A last data refresh fixed most of the wrong labels. All 25 cards are live and the full project story is in the repo.
AI agent (Cruva + Kalodata): closed. Pulled data from both sources, merged it into one master file, and did a final gap check. Both platforms limit how much you can pull on the free plan, so the rest stays uncovered.
Tomorrow:

Next step of Phase 2 on the classifier (showing the model example answers).
Watch Token Saviour through a full day to make sure the savings actually hold.
Repos:

Classifier: https://github.com/Krtvy/LabeLLM
Creator profile system: https://github.com/Krtvy/creator-profile-api
Good night.
