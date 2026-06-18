# VISION.md — Where this project is heading

> Read this first when picking up the project after a break. This is the _destination_. Every task done, every pattern written, every glossary entry is a step toward it.

## The end-state

Kartavya is a data intern at Rootlabs. The work comes from 8 POCs (Trupti, Shivangi, Khushi, Vansh, Manini, Chanchal, Rachit, Sanya). Each POC owns a slice of creators / campaigns / sample-deliveries and gives Kartavya data tasks: reconciliations, breakdowns, trackers, new-video-GMV analyses, etc.

The end-state is a **self-serve HTML portal** that any POC can use directly to get a data task done — without going through Kartavya as the bottleneck. The portal:

- Asks "what task do you want to do?" with a guided flow (yes/no/select)
- Tells the POC which file/sheet to upload and what shape it should be in
- Runs the analysis (calls Yudhishthira or a derived script behind the scenes)
- Returns a deliverable (CSV + MD audit) to download
- Persists the task to that POC's folder for history

Kartavya's role evolves: from "do the task" → "operate the system that does the task."

## The three phases

### Phase 1 — Teaching by doing (now → ~6 months)

Every task done becomes a brick in the pattern library:

- **New terminology** → `training/glossary/<term>.md`
- **Reusable task shape** → `training/patterns/<slug>.md` (trigger phrases · data needed · deliverable shape · pitfalls · worked example)
- **POC-specific quirk** → that POC's `pocs/<name>/register.md`
- **Past good deliverable** → `training/examples/<YYYY-MM-DD>_<slug>.md` (anonymised if needed)

**The leverage habit:** after every task, ask "will I see this shape again?" If yes, document it. Each documented task is a step closer to the portal being useful.

### Phase 2 — Self-serve portal (when pattern library covers ~80% of incoming tasks)

Build an HTML portal that wraps the pattern library:

- Decision-tree frontend (yes/no/select narrows to the right pattern)
- File upload + Sheet URL input
- Backend that maps the answers → pattern → execution → deliverable
- POC authentication (each POC sees only their own past tasks)
- Probably Flask/FastAPI + plain HTML form, or Streamlit/Gradio for faster prototyping

The portal **is not the work** — it's the wrapper around the patterns. The patterns are the actual asset. Building the portal early without enough patterns is just an empty form.

### Phase 3 — AI-assisted long tail (continuous)

For tasks that don't cleanly match a pre-built pattern, the portal hands off to Yudhishthira (or whatever data-analyst agent exists then). The system covers the routine 80%; AI handles the novel 20%. Each handled novel case becomes the next pattern.

## What this means for every task we do today

1. **Document the task.** Even small tasks worth a pattern entry once the shape is established. The "New Video GMV calculation" work from 2026-05-13 should become `training/patterns/new-video-gmv-attribution.md` — trigger phrases, data needs, deliverable shape, the hgr-only filter pitfall, the worked example with $5,693.47 reconciliation.
2. **Be explicit about which POC.** Strengthens the per-POC scoping that the portal will need to enforce.
3. **Save good deliverables.** They become the "this is what a good answer looks like" reference.
4. **Glossary discipline.** Every term used should have a canonical definition. The portal will surface these to POCs who don't share Kartavya's mental model.
5. **Don't take shortcuts on the audit chain.** Each deliverable's `.md` is what future Kartavya (and the portal) will rely on to understand what was done.
6. **Document workbooks top-down.** Per Kartavya 2026-05-13: each tracker workbook that POCs use should have a top-down explainer answering "what does the whole sheet do?", "what does each tab do?", "what does each column track and why?" This is the same content layer the portal will eventually surface as inline help — a new POC who opens the portal should be able to learn the tracker by reading the same explainer Yudhishthira authored. The May workbook's v2 top-down report (`.claude/agents/yudhishthira/deliverables/may-workbook-report-v2-top-down_2026-05-13.html`) is the prototype for this; future trackers should follow the same shape.
7. **Inspiration intake is a discipline.** When you read an article, Twitter thread, or paper that suggests changes to the ecosystem, the response shape is: per-idea fit-check → document the analysis → defer to a trigger condition, not adopt-on-enthusiasm. The template is `_audit/2026-05-13_zodchii-inspiration-intake.md` — for each idea, decide adopt/skip with explicit reasoning, record what trigger would make adoption worthwhile, set a reminder to revisit. **Adopting nothing tonight ≠ adopting nothing ever.** The discipline is patient. Article ideas survive in `_audit/` until trigger fires. The `_audit/REMINDERS.md` file plus the SessionStart greeting surface overdue reminders automatically, so deferred decisions don't get lost.

## Non-goals

- **Don't build the portal tonight.** It's premature without enough patterns. We're in Phase 1.
- **Don't over-engineer the patterns.** A 1-page pattern is better than a 10-page one. Quick to write, quick to read, quick to update.
- **Don't try to make the system fully autonomous before Phase 3.** Phase 1 + 2 explicitly keep Kartavya in the loop — that's where the learning happens.

## Open architectural questions (Phase 2 design)

To revisit when Phase 1 has produced enough patterns:

1. **Hosting.** Localhost only? Internal Rootlabs server? Cloud (Render, Fly.io, etc.)?
2. **Auth.** Google login (POCs already have Workspace accounts)? Simple shared secret? Per-POC API key?
3. **Backend stack.** Flask + jinja templates is simplest. FastAPI + a small SPA is more flexible. Streamlit/Gradio is fastest to prototype but harder to extend later.
4. **How does the portal actually run Yudhishthira?** Subprocess call to Claude Code? Direct Anthropic API call? A queue (Celery/RQ) for long-running tasks?
5. **Data persistence.** SQLite for task history? Plain markdown files in `pocs/<poc>/tasks/` (matches current discipline)?
6. **Yudhishthira's Hyperagent deployment.** When the portal exists, does the agent still run locally via Claude Code, or does it move to Hyperagent for production? Affects how the portal talks to it.

None of these need answering now. They need answering when the pattern library is rich enough to justify the build.

## The story this VISION.md is telling

This project isn't an isolated experiment. It's the **scaffolding for the system that replaces the bottleneck Kartavya currently is**. Every disciplined piece — Bhishma constitution, audit chain, per-POC scoping, training library, glossary, agent procedures — exists because someday a POC will hit a button on a portal and expect a correct answer back, and the foundation we're laying today is what makes that possible.

The path isn't sexy. It's pattern-by-pattern accumulation. But it compounds, and it ends with a tool the whole team can use.

---

_Vision authored 2026-05-13 03:05 IST by Claude Code session at Kartavya's direction. Living document — update as the architecture decisions in Phase 2 actually get made._
