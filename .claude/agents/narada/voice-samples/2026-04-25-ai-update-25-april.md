---
sample_id: 009
date: 2026-04-25
time: 01:52
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
AI Update 25 April

Saturday was less coding, more going over what I have built.

What I did:

• Started looking at HyperAgent. Pranav told me to check it out. Trying to understand how AI agent tools work.
• Went back through the code and notes I wrote last week. Wanted to really understand every line before moving to the next part.
• Read up on the basics again. Things like how tokens work and the settings you can pass.

Sunday onwards I have two things going in parallel:

1. My classifier project: figure out how the AI charges per call, then build one clean function I can reuse with proper error handling.

2. The system Shambu asked me to build. Pulls a creator's latest 10 videos from Apify, gets the transcripts, does visual analysis, and builds a creator profile (style, tone, pacing, video format). End to end. Pushed to GitHub. Deployed as an API where you give a username and get back a profile card.

Repo (classifier): https://github.com/Krtvy/LabeLLM
