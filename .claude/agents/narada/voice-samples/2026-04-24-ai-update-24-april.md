---
sample_id: 008
date: 2026-04-24
time: 22:27
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
AI Update 24 April

Project live on GitHub
https://github.com/Krtvy/LabeLLM

Shipped today:
• Working Python that hits OpenAI's API end to end. Prompt in, full structured response parsed out (id, model, usage, finish reason).
• Built both of OpenAI's text endpoints side by side (responses.create and chat.completions.create). Same task, two implementations, real comparison of where they differ.
• Clean scaffolding: isolated environment, secrets out of git, pinned dependencies, four clean commits on GitHub.

Next: token accounting and cost per call, then consolidating both endpoints into one reusable function with retries and error handling.
