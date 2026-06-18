---
sample_id: 007
date: 2026-04-23
time: 22:05
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
Updates on what I've been working on recently:
Business: Updated sheets and uploaded raw data for the dashboard. Coordinating with Arshdeep on creator outreach, pushing follow-up messages across the acquisition pipeline.
AI: Kicked off my first AI project today. Shipped:
• Full Python setup, venv, deps, secrets handling
• hello.py, first working OpenAI API call (auth → request → parsed response, end-to-end)
• README + reference docs so every line is defensible
The project: an LLM-powered Job Description Classifier. Input: raw JD text. Output: structured JSON across seniority, work-mode, and industry, plus an eval harness measuring accuracy against a hand-labeled test set.
For a while I was figuring out how to actually approach learning AI, decided the only way that makes sense for me is learning by building. Every concept gets a project attached to it.
Trajectory: classifier → classical ML → RAG → agents → fine-tuning → production deploy, each stage a working shipped project.
Will share GitHub link once past scaffolding. From here on, daily updates without fail.
