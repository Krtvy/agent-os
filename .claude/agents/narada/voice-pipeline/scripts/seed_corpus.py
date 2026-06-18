"""Seed Narada's voice corpus from the historical Slack DM dump.

Inputs: hardcoded list of Kartavya-authored messages from his DM history with
Mayank, late April through early May 2026. Source: pasted by Kartavya
2026-05-11.

Outputs:
  voice-samples/kartavya-corpus.csv       — pipeline-ready CSV
  voice-samples/<date>-<slug>.md          — one human-readable file per sample

Recipient signals (Mayank's own messages prompting/correcting) are saved
separately at voice-samples/recipient-signals.md so the pipeline can read
them as context without polluting Kartavya's voice training data.

Self-rating: Kartavya rates this corpus 6/10. Narada should learn the
structural patterns and signature phrases, but flag identified weaknesses
(see RATING-NOTES.md after this script runs) rather than replicate them.
"""

import csv
import os
import re
from pathlib import Path

VOICE_SAMPLES = Path("/Users/mosaic/projects/observer-test/.claude/agents/narada/voice-samples")
VOICE_SAMPLES.mkdir(parents=True, exist_ok=True)

# Message format: (id, date_iso, time, slug, body)
# Dates are best-inference based on content cues. The pipeline degrades
# gracefully on imprecise timestamps.

MESSAGES = [
    ("sample-002", "2026-04-21", "19:39", "first-response",
     """hey yesterday was working on the acquisition task only now also I am with pranav working on the same task would start sending whatever i have learned on AI without fail from today itself"""),

    ("sample-003", "2026-04-22", "06:55", "ai-update-day-1",
     """AI Update Day 1

Went through Andrej Karpathy's talk on how LLMs work. Key takeaway is that LLMs are not just chatbots, the real power is in tool use where they can browse the web, write and run code, do calculations. It's closer to a new operating system than a chat interface. Will be sharing one of these every day."""),

    ("sample-004", "2026-04-22", "21:15", "ai-update-day-2",
     """AI Update Day 2

Set up a fully local AI environment using Google's Gemma 4 (Apache 2.0, released 2 weeks ago) with LM Studio and Apple MLX as the inference backend. Built a Streamlit chat UI in Python that connects to the local model server. Tested across reasoning, coding, writing, and math — model ran at 25 tokens/sec with no API, no cloud, zero cost per query."""),

    ("sample-005", "2026-04-23", "12:41", "business-and-ai-context",
     """Hey Mayank

Business side: Coordinated with Ashdeep to push 60 creator outreach messages yesterday across the acquisition pipeline, covering both first follow-ups for new creators and second follow-ups for those who hadn't responded. This is part of the ongoing effort creator's acquisition pipeline

AI side: What I built yesterday runs entirely on-device with zero API costs. This week I'm connecting it to our Google Sheets and TikTok creator data so it can answer pipeline questions in plain English like who needs follow-up, who's underperforming, draft outreach messages instantly. Redis caching and a DB layer come after for speed and scale.

Let me know if you need any other update cause the context I understood this is the update for yesterday"""),

    ("sample-006", "2026-04-23", "22:29", "short-bullets",
     """Update for yesterday and today :

Daily reporting: Updated the sheets and uploaded raw data for the Dashboard

Acquisition: Pushed Follow ups 1 2 and First messages to the creators part of the acquisition pipe line
AI: learned about building AI agents the introduction do's and dont's
Understanding that build my first AI agent for about research and learning"""),

    ("sample-007", "2026-04-23", "22:05", "first-ai-project-kickoff",
     """Hey Mayank,
Updates on what I've been working on recently:
Business: Updated sheets and uploaded raw data for the dashboard. Coordinating with Arshdeep on creator outreach, pushing follow-up messages across the acquisition pipeline.
AI: Kicked off my first AI project today. Shipped:
• Full Python setup, venv, deps, secrets handling
• hello.py, first working OpenAI API call (auth → request → parsed response, end-to-end)
• README + reference docs so every line is defensible
The project: an LLM-powered Job Description Classifier. Input: raw JD text. Output: structured JSON across seniority, work-mode, and industry, plus an eval harness measuring accuracy against a hand-labeled test set.
For a while I was figuring out how to actually approach learning AI, decided the only way that makes sense for me is learning by building. Every concept gets a project attached to it.
Trajectory: classifier → classical ML → RAG → agents → fine-tuning → production deploy, each stage a working shipped project.
Will share GitHub link once past scaffolding. From here on, daily updates without fail."""),

    ("sample-008", "2026-04-24", "22:27", "ai-update-24-april",
     """Hey Mayank,
AI Update 24 April

Project live on GitHub
https://github.com/Krtvy/LabeLLM

Shipped today:
• Working Python that hits OpenAI's API end to end. Prompt in, full structured response parsed out (id, model, usage, finish reason).
• Built both of OpenAI's text endpoints side by side (responses.create and chat.completions.create). Same task, two implementations, real comparison of where they differ.
• Clean scaffolding: isolated environment, secrets out of git, pinned dependencies, four clean commits on GitHub.

Next: token accounting and cost per call, then consolidating both endpoints into one reusable function with retries and error handling."""),

    ("sample-009", "2026-04-25", "01:52", "ai-update-25-april",
     """Hey Mayank,
AI Update 25 April

Saturday was less coding, more going over what I have built.

What I did:

• Started looking at HyperAgent. Pranav told me to check it out. Trying to understand how AI agent tools work.
• Went back through the code and notes I wrote last week. Wanted to really understand every line before moving to the next part.
• Read up on the basics again. Things like how tokens work and the settings you can pass.

Sunday onwards I have two things going in parallel:

1. My classifier project: figure out how the AI charges per call, then build one clean function I can reuse with proper error handling.

2. The system Shambu asked me to build. Pulls a creator's latest 10 videos from Apify, gets the transcripts, does visual analysis, and builds a creator profile (style, tone, pacing, video format). End to end. Pushed to GitHub. Deployed as an API where you give a username and get back a profile card.

Repo (classifier): https://github.com/Krtvy/LabeLLM"""),

    ("sample-010", "2026-04-26", "02:17", "ai-update-26-april",
     """Hey Mayank,
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
- Creator profile system: local for now, pushing to GitHub once I have the keys and a successful real run."""),

    ("sample-011", "2026-04-27", "00:18", "ai-update-27-april",
     """Hey Mayank,
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
- Creator profile system: still local, pushing to GitHub once the batch produces cards I am happy with."""),

    ("sample-012", "2026-04-28", "04:52", "ai-update-28-april",
     """Hey Mayank,
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
- Creator profile system: https://github.com/Krtvy/creator-profile-api"""),

    ("sample-013", "2026-04-29", "01:24", "ai-update-29-april",
     """Hey Mayank,
AI Update 29 April

Classifier project: the API call now auto-retries when something temporary fails (slow network, rate limits) and waits longer between tries. Bad-key errors fail right away. Also added streaming so the reply appears live, word by word.

Creator profile system: started a 15-creator batch tonight that runs while I sleep. By morning there should be 25 full cards ready in one place.

AI agent (Cruva + Kalodata): pulled real Health GMV numbers for 591 of 1,384 creators on the list. Total: $14.27M across that group. Top 15 identified. Five CSV files delivered. The other 793 are not in Cruva's free data, so I will try a few more Cruva methods first, and build a Kalodata fallback if those do not work.

Tomorrow:

1. Wrapper for the classifier that combines everything so far into one reusable piece.
2. Check the overnight batch results.
3. Try the other Cruva methods, then build the Kalodata fallback if needed.

Repos:

- Classifier: https://github.com/Krtvy/LabeLLM
- Creator profile system: https://github.com/Krtvy/creator-profile-api

Good night."""),

    ("sample-014", "2026-04-30", "01:20", "ai-update-30-april",
     """Hey Mayank,
AI Update 30 April

Today went into the move. Packing, paperwork, payments, talking to the PG owner and the new flat owner. Did not get to the AI projects today. Tomorrow is the actual move.

Yesterday on the AI side went well. The creator profile system's overnight run finished well: 25 creator cards are now ready, 22 of them are good. 4 of them have real GMV numbers, adding up to $364K. The AI agent (Cruva + Kalodata) gave a much better number after I fixed the math: real Health GMV for 708 of 1,384 creators (that is 51%), $5.24M in the last 30 days, top one is legendarylootfinds with $247K. Did not get to the classifier yesterday because of the move work.

Moving so I have a proper space to work. The new place has a proper room and desk setup, which will make it much easier to focus on the AI work properly.

Also, if there is any project or task you have been thinking of giving me, please send it my way. Happy to work on it.

Good night."""),

    ("sample-015", "2026-05-01", "01:50", "ai-update-1-may",
     """Hey Mayank,
AI Update 1 May

Today was on internal data work, no AI side today. Mapped out the GMV and video count for Anisha, fixed the Tarmita sheet, and had a meeting with Shivangi and Rachit for the May tracker. Rachit also walked me through how things will progress in the next month.

Tomorrow is the actual flat move. The AI side has been quiet through these move days. From the new place onwards, the AI updates will be richer and have more progress than these past few days.

Good night."""),

    ("sample-016", "2026-05-02", "03:17", "ai-update-2-may",
     """Hey Mayank,
AI Update 2 May

Noted on yesterday. Was not getting dedicated time to sit on AI because of the move. Moved into the new flat today, so more focused time for AI from here.

Three things from these days:

Classifier project: closed the first stage. Built the base function that handles every AI call. Learned how to wire up auth, error handling, retries, cost tracking, and streaming, and how to wrap them all behind one clean interface. Prompt engineering next.

Creator profile system: shipped v1.1.0. Built outreach contact extraction, posting cadence, earnings per video, and a brand fit score. Learned how to backfill cached profiles cheaply without re-running the full pipeline.

AI agent (Cruva + Kalodata): cracked Kalodata's internal API. Now pulling real Health category numbers directly from their endpoint instead of scraping the UI. Learned how to capture internal endpoints from network traffic and how to design a fallback when one platform's free tier does not cover the universe.

Repos:
- Classifier: https://github.com/Krtvy/LabeLLM
- Creator profile system: https://github.com/Krtvy/creator-profile-api

Good night."""),

    ("sample-017", "2026-05-04", "02:40", "ai-update-4-may",
     """Hey Mayank,
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
Good night."""),

    ("sample-018", "2026-05-05", "05:08", "ai-update-5-may",
     """Hey Mayank,
AI Update 5 May
Started the day on Phase 2 of the classifier, then got engaged on the data part: automated the May sheet so it updates on its own, and got Khushi the data she needed. Also discussed a few build ideas with Pranav.
Tomorrow:

Get more context from Pranav on what we are building.
Back on Phase 2 of the classifier (showing the model example answers).
Watch Token Saviour through a full day of work to make sure the savings hold.
Repos:

Classifier: https://github.com/Krtvy/LabeLLM
Creator profile system: https://github.com/Krtvy/creator-profile-api
Good night."""),

    ("sample-019", "2026-05-06", "04:18", "ai-update-6-may",
     """Hey Mayank,
AI Update 6 May
Classifier project: closed Phase 2.A today and pushed everything to GitHub. The cost finding from the demo is now properly written up. Same question can swing about 10x in cost depending on how chatty the personality is. First sub-phase of Phase 2 is locked in.
D2C / consumer brand research: spent today researching D2C brand strategy across the funnel. Covers acquisition, conversion, retention, user habits, creator commissions, competitor profiles, and brand case studies. Each topic in its own doc so you can jump to whichever part you care about.
Data side: more work on the main sheet automation. Gave Khushi creator earnings data, including each creator's commission and what they brought in for Rootlabs. Also pulled new video GMV numbers for bearthevoice3.
Token Saviour: ran it through a full day. The savings on each individual chat are small, but the total tokens saved over a whole day adds up to something meaningful when you stack up long sessions.
Tomorrow:

Phase 2.B of the classifier (showing the model example answers).
Go back through the D2C research with Pranav, pull out the key points, and tighten it into a concise version of what actually matters.
Repos:

Classifier: https://github.com/Krtvy/LabeLLM
Good night."""),

    ("sample-020", "2026-05-07", "04:04", "ai-update-7-may",
     """Hey Mayank,
7 May
AI Update
Observer agent: built a new agent today that watches other AI agents while they work. After either 10 days of watching or 20 runs, it suggests changes for that agent based on what it has seen. I can apply, reject, or modify those suggestions. The idea is to let agents improve themselves over time.
Manini cross-reference: ran Manini's list of 1,875 creators through the Cruva-Kalodata agent I built. 554 covered so far. 1,321 have no data at all in either source. Of the 554, 207 are actually selling health products in the last 30 days, and 37 of those crossed $10,000. The other 347 are in our system but have zero health sales. The agent still has some limits and is not running at full capacity yet.
Research summary: yesterday's D2C research was done by the research agent. Today I used it to pull the key points for customer acquisition and retention, and turned that into a step-by-step plan for following up with customers, with ready-to-use message templates and a simple playbook.
Data Update
Khushi GMV: spent time on creator GMV numbers for Khushi. Worked out the New Video GMV for bearthevoice3 and blondevixen59 on alpha gummies. Combined was about $7,992 out of $102,449 total. Also recorded the process for future use.
Anisha's tracker: set up an automation that adds the daily MagAshwa LIVE creators and their GMV into her sheet on its own.
Chanchal: gave sample data on the basis of the PoC.
No progress on the Classifier today. Spent the whole day on agent and research work. Picking it back up tomorrow.
Tomorrow:

Phase 2.B of the classifier (showing the model example answers).
Improve the Cruva-Kalodata agent so it runs at full capacity.
Will be working from home tomorrow as my mother is visiting me.
Repos:

Classifier: https://github.com/Krtvy/LabeLLM
Good night."""),

    ("sample-021", "2026-05-08", "03:16", "ai-update-8-may",
     """Hey Mayank,
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
Good night."""),
]

# Mayank's directing/correcting messages — saved separately as recipient signals
RECIPIENT_SIGNALS = [
    ("2026-04-21", "18:41", "what did you learn on AI yesterday?"),
    ("2026-04-21", "18:45", "what are you working on right now"),
    ("2026-04-21", "18:46", "i want a daily update DMd without fail"),
    ("2026-04-22", "14:17", "Don't want you to just listen to podcasts"),
    ("2026-04-22", "14:17", "Actually execute something daily"),
    ("2026-04-22", "14:17", "Move faster"),
    ("2026-04-23", "03:59", "What did you contribute to the business"),
    ("2026-04-23", "03:59", "Can I get an update on that"),
    ("2026-05-01", "02:56", "Thanks"),
    ("2026-05-01", "02:57", "Even if there is no AI work, you should still learn"),
    ("2026-04-25", "01:53", "Okay thanks"),
    ("2026-04-26", "02:22", "thanks"),
    ("2026-04-29", "01:34", "thanks"),
    ("2026-05-07", "04:05", "thanks"),
    ("2026-05-08", "03:32", "Thanks"),
]


def main():
    csv_path = VOICE_SAMPLES / "kartavya-corpus.csv"

    # Read existing rows so we don't lose sample-001 (the May 10 reference)
    existing_rows = []
    if csv_path.exists():
        with open(csv_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            existing_rows = list(reader)
            existing_ids = {r["id"] for r in existing_rows}

    new_rows = []
    for sid, date, time, slug, body in MESSAGES:
        if sid in {r.get("id") for r in existing_rows}:
            continue
        ts = f"{date}T{time}:00+05:30"
        new_rows.append({
            "id": sid,
            "timestamp": ts,
            "recipient": "mayank",
            "medium": "slack",
            "thread_id": "—",
            "parent_ts": "—",
            "body": body,
            "reactions": "",
            "is_reply": "false" if sid != "sample-002" else "true",
        })

    all_rows = existing_rows + new_rows

    fieldnames = ["id", "timestamp", "recipient", "medium", "thread_id", "parent_ts", "body", "reactions", "is_reply"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    # One markdown file per new sample
    for sid, date, time, slug, body in MESSAGES:
        md_path = VOICE_SAMPLES / f"{date}-{slug}.md"
        if md_path.exists():
            continue
        md_path.write_text(f"""---
sample_id: {sid.split('-')[1]}
date: {date}
time: {time}
mode: mayank-update
recipient: mayank
medium: slack
captured_by: kartavya
captured_on: 2026-05-11
quality: real-historical
self_rating: 6/10
notes: From historical Slack DM dump. Real production voice. Use as training signal but flag identified weaknesses (see RATING-NOTES.md) rather than replicate them.
---

{body}
""")

    # Recipient signals (Mayank's own messages — context, not training body)
    rs_path = VOICE_SAMPLES / "recipient-signals.md"
    rs_path.write_text("""---
purpose: Mayank's own messages to Kartavya during the same period.
usage: Context for Narada to understand what Mayank values and how he prompts. NOT training data for Kartavya's voice — Mayank's voice should not bleed into Kartavya's drafts.
captured_on: 2026-05-11
---

# Mayank's directing/correcting messages

These are signals about audience preference, not voice training data.

## Original prompt that started the daily update habit

""" + "\n".join(f"- **{d} {t}** — {b}" for d, t, b in RECIPIENT_SIGNALS[:3]) + """

## Course corrections (early)

""" + "\n".join(f"- **{d} {t}** — {b}" for d, t, b in RECIPIENT_SIGNALS[3:6]) + """

## Specific demand for business contribution

""" + "\n".join(f"- **{d} {t}** — {b}" for d, t, b in RECIPIENT_SIGNALS[6:8]) + """

## Demand for learning even on no-AI days

""" + "\n".join(f"- **{d} {t}** — {b}" for d, t, b in RECIPIENT_SIGNALS[8:10]) + """

## Acknowledgments (positive signal that the update landed)

""" + "\n".join(f"- **{d} {t}** — {b}" for d, t, b in RECIPIENT_SIGNALS[10:]) + """

## What Narada should learn from these

1. Mayank values **business contribution** equally with AI learning. Updates that omit business → trigger correction.
2. Mayank values **execution** over consumption. Watching/listening alone → trigger correction.
3. Mayank values **brevity but with substance** — "thanks" is the most common response, suggesting the format works when it works.
4. Mayank does NOT respond at length to long updates; the bar is "did this earn 30 seconds of his time."
5. Mayank notices missing days and uses prompting to enforce cadence.
""")

    print(f"Wrote {csv_path}")
    print(f"  Total rows: {len(all_rows)}")
    print(f"  New rows added: {len(new_rows)}")
    print(f"")
    print(f"Wrote {len(MESSAGES)} markdown samples to {VOICE_SAMPLES}/")
    print(f"Wrote {rs_path}")


if __name__ == "__main__":
    main()
