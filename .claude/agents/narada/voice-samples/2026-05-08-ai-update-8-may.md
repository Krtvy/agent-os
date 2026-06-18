---
sample_id: 021
date: 2026-05-08
time: 03:16
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
8 May
AI Update
Customer email pipeline (MagAshwa + HGR): built out the customer email flow using yesterday's research, settled on 8 emails per customer.
Agent work: kept improving the observer agent from yesterday and the research agent. Mapped how they work together and looked into how each is built. The observer agent in particular got a big update with more files and more capability, working towards a version that can improve itself on its own. Also planned for an Orchestrator agent that will manage all the agents together. Keeping it for the future, once I have enough data from the Observer and Research agents to design it well.
Cruva-Kalodata agent: working on it. Will update when there is real progress.
Token Saviour: ran the 4-day numbers. 192 prompts seen, 10 compressed, ~6,000 tokens saved. Most prompts were already short, so the hook did not need to touch them.
Classifier: read the documentation today so I can code from tomorrow onwards. Phase 2.B will show the model 2-3 example answer pairs so it picks up the right output pattern. A small demo script, plus an update to my wrapper so it can handle example pairs.
Data Update
HGR + MagAshwa LIVE tracker: extended yesterday's Anisha tracker. Built an automated sheet for Trupti that counts HGR LIVE and MagAshwa LIVE GMV and creators, using the same logic Anisha's tracker runs on, so both pipelines pull and append data the same way.
May sheet: fixed a few glitches that had crept in.
Data workflow: discussed the data-request process in the data request channel with Rachit. Shared some inputs from my experience as a data intern on how it can be streamlined.
Tomorrow:

Phase 2.B of the classifier.
Continue improving the agents.
Roll out the new Data Request channel so every data request goes through the form.
Repos:

Classifier: https://github.com/Krtvy/LabeLLM
Good night.
