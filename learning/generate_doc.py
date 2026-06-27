"""
Phase Documentation Generator

After completing each learning phase, run this script.
Answer 5 questions → system generates a beautiful HTML document.

Usage:
    python learning/generate_doc.py

Output:
    learning/docs/<month>-<project>-phase<N>.html
"""

import os
import json
from pathlib import Path
from datetime import date
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / "ai-knowledge-feed" / ".env")

DOCS_DIR = Path(__file__).parent / "docs"
DOCS_DIR.mkdir(exist_ok=True)


QUESTIONS = [
    ("phase_name",    "1. What is this phase called and what did you build?\n   → "),
    ("concept",       "2. Explain the core concept in YOUR OWN WORDS (no notes, just your understanding):\n   → "),
    ("hardest_part",  "3. What was the hardest part and exactly how did you solve it?\n   → "),
    ("what_broke",    "4. What broke during this phase? What did breaking it teach you?\n   → "),
    ("whats_next",    "5. How does this phase connect to what comes next?\n   → "),
]

META = [
    ("month_number",   "Month number (1-6): "),
    ("project_name",   "Project name (e.g. RAG System): "),
    ("phase_number",   "Phase number (1-4): "),
]


def ask_questions() -> dict:
    print("\n" + "="*60)
    print("  PHASE DOCUMENTATION GENERATOR")
    print("="*60)
    print("\nAnswer honestly. The system will expand your answers into")
    print("full documentation. No need to be perfect — just real.\n")

    data = {}

    print("── META ──────────────────────────────────────────────────")
    for key, prompt in META:
        data[key] = input(prompt).strip()

    print("\n── YOUR ANSWERS ──────────────────────────────────────────")
    for key, prompt in QUESTIONS:
        print()
        data[key] = input(prompt).strip()

    return data


def generate_with_gemini(answers: dict) -> dict:
    """Use Gemini to expand answers into full documentation sections."""
    try:
        from google import genai
        from google.genai import types

        # Use first available Gemini key from .env
        api_key = (
            os.getenv("GEMINI_KEY_1") or
            os.getenv("GEMINI_KEY_2") or
            os.getenv("GEMINI_API_KEY")
        )
        if not api_key:
            raise ValueError("No Gemini API key found in environment")
        client = genai.Client(api_key=api_key)

        prompt = f"""You are generating learning documentation for an AI engineering student.

Phase: {answers['phase_name']}
Project: {answers['project_name']} (Month {answers['month_number']}, Phase {answers['phase_number']})

Their raw answers:
- What they built: {answers['phase_name']}
- Their concept explanation: {answers['concept']}
- Hardest part: {answers['hardest_part']}
- What broke: {answers['what_broke']}
- Connection to next phase: {answers['whats_next']}

Generate a JSON object with these fields:
{{
  "concept_title": "clean title for the concept learned",
  "concept_explanation": "3-4 paragraph technical explanation of the core concept, written clearly for a developer. Include the intuition, not just the definition. Reference what they described.",
  "architecture_mermaid": "a mermaid.js diagram string showing how this phase's components connect. Use flowchart LR or TD. Make it specific to what they built.",
  "key_insight": "the single most important thing they should remember from this phase — 2 sentences max",
  "what_broke_expanded": "expand on what they said broke — explain WHY it broke technically and what the lesson teaches about the concept",
  "code_concept": "the most important code pattern from this phase — describe it in 3-4 sentences with a conceptual code snippet (pseudocode or real)",
  "decision_made": "the key architectural or implementation decision made in this phase and why it was the right call",
  "connection_to_next": "expand their answer about what comes next — how does this phase's knowledge become the foundation for the next"
}}

Return only valid JSON. No markdown wrapping."""

        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.4,
            )
        )
        return json.loads(response.text)

    except Exception as e:
        print(f"[generator] Gemini error: {e} — using raw answers")
        return {
            "concept_title": answers['phase_name'],
            "concept_explanation": answers['concept'],
            "architecture_mermaid": "flowchart LR\n    A[Input] --> B[Process] --> C[Output]",
            "key_insight": answers['hardest_part'],
            "what_broke_expanded": answers['what_broke'],
            "code_concept": "See your implementation files.",
            "decision_made": "Documented in DECISIONS.md",
            "connection_to_next": answers['whats_next'],
        }


def render_html(answers: dict, expanded: dict) -> str:
    today = date.today().strftime("%B %d, %Y")
    month = answers['month_number']
    project = answers['project_name']
    phase = answers['phase_number']

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>M{month} · Phase {phase} · {project}</title>

<!-- Mermaid for architecture diagrams -->
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<!-- Prism for syntax highlighting -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>

<style>
  :root {{
    --bg: #0f0f13;
    --surface: #1a1a24;
    --border: #2a2a3a;
    --accent: #7c6bff;
    --accent2: #00d4aa;
    --text: #e8e8f0;
    --muted: #8888a0;
    --warning: #ffaa44;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.7;
    padding: 2rem 1rem;
  }}

  .container {{ max-width: 860px; margin: 0 auto; }}

  /* Header */
  .header {{
    border-left: 4px solid var(--accent);
    padding: 1.5rem 2rem;
    background: var(--surface);
    border-radius: 0 12px 12px 0;
    margin-bottom: 2.5rem;
  }}
  .breadcrumb {{
    font-size: 0.75rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
  }}
  .header h1 {{
    font-size: 1.8rem;
    font-weight: 700;
    color: white;
    margin-bottom: 0.3rem;
  }}
  .header .date {{ color: var(--muted); font-size: 0.85rem; }}

  /* Key insight banner */
  .insight-banner {{
    background: linear-gradient(135deg, rgba(124,107,255,0.15), rgba(0,212,170,0.1));
    border: 1px solid rgba(124,107,255,0.3);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 2rem;
    font-size: 1.05rem;
    font-style: italic;
  }}
  .insight-banner::before {{
    content: "Key Insight";
    display: block;
    font-size: 0.7rem;
    font-style: normal;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--accent);
    font-weight: 600;
    margin-bottom: 0.4rem;
  }}

  /* Sections */
  .section {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.75rem;
    margin-bottom: 1.5rem;
  }}
  .section-label {{
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--accent);
    font-weight: 600;
    margin-bottom: 0.75rem;
  }}
  .section h2 {{
    font-size: 1.15rem;
    font-weight: 600;
    color: white;
    margin-bottom: 1rem;
  }}
  .section p {{ color: #c0c0d0; margin-bottom: 0.75rem; }}
  .section p:last-child {{ margin-bottom: 0; }}

  /* Architecture diagram */
  .mermaid-wrap {{
    background: #13131c;
    border-radius: 8px;
    padding: 1.5rem;
    overflow-x: auto;
    margin-top: 0.5rem;
  }}
  .mermaid {{ color: var(--text); }}

  /* What broke */
  .broke-section {{
    border-left-color: var(--warning);
  }}
  .broke-section .section-label {{ color: var(--warning); }}

  /* Decision */
  .decision-section {{
    border-left-color: var(--accent2);
    border-left-width: 3px;
  }}

  /* Your words */
  .raw-answer {{
    background: #13131c;
    border-left: 3px solid var(--muted);
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.25rem;
    margin: 0.75rem 0;
    font-size: 0.9rem;
    color: var(--muted);
    font-style: italic;
  }}
  .raw-answer::before {{
    content: "Your words: ";
    font-style: normal;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    display: block;
    margin-bottom: 0.3rem;
    color: #666680;
  }}

  /* Code block */
  pre[class*="language-"] {{
    border-radius: 8px;
    margin: 0.75rem 0 0;
    font-size: 0.82rem;
  }}

  /* Next phase */
  .next-section {{
    background: linear-gradient(135deg, rgba(0,212,170,0.08), rgba(124,107,255,0.05));
    border: 1px solid rgba(0,212,170,0.2);
  }}
  .next-section .section-label {{ color: var(--accent2); }}

  /* Footer */
  .footer {{
    text-align: center;
    color: var(--muted);
    font-size: 0.75rem;
    margin-top: 2.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border);
  }}

  @media print {{
    body {{ background: white; color: #1a1a1a; padding: 1rem; }}
    .section {{ border: 1px solid #ddd; }}
    .header {{ background: #f5f5f5; }}
  }}
</style>
</head>
<body>
<div class="container">

  <!-- Header -->
  <div class="header">
    <div class="breadcrumb">Month {month} · {project} · Phase {phase}</div>
    <h1>{expanded['concept_title']}</h1>
    <div class="date">Completed {today}</div>
  </div>

  <!-- Key Insight -->
  <div class="insight-banner">
    {expanded['key_insight']}
  </div>

  <!-- Concept Explanation -->
  <div class="section">
    <div class="section-label">Concept</div>
    <h2>What is this?</h2>
    {"".join(f'<p>{p}</p>' for p in expanded['concept_explanation'].split('\n\n') if p.strip())}
    <div class="raw-answer">{answers['concept']}</div>
  </div>

  <!-- Architecture -->
  <div class="section">
    <div class="section-label">Architecture</div>
    <h2>How it connects</h2>
    <div class="mermaid-wrap">
      <div class="mermaid">
{expanded['architecture_mermaid']}
      </div>
    </div>
  </div>

  <!-- What Broke -->
  <div class="section broke-section">
    <div class="section-label">What Broke</div>
    <h2>The real learning</h2>
    {"".join(f'<p>{p}</p>' for p in expanded['what_broke_expanded'].split('\n\n') if p.strip())}
    <div class="raw-answer">{answers['what_broke']}</div>
  </div>

  <!-- Hardest Part -->
  <div class="section">
    <div class="section-label">Hardest Part</div>
    <h2>Where you got stuck</h2>
    <div class="raw-answer">{answers['hardest_part']}</div>
  </div>

  <!-- Code Pattern -->
  <div class="section">
    <div class="section-label">Key Pattern</div>
    <h2>The code concept</h2>
    <p>{expanded['code_concept']}</p>
  </div>

  <!-- Decision -->
  <div class="section decision-section">
    <div class="section-label">Decision Made</div>
    <h2>Why you built it this way</h2>
    <p>{expanded['decision_made']}</p>
  </div>

  <!-- What's Next -->
  <div class="section next-section">
    <div class="section-label">What's Next</div>
    <h2>How this phase sets up Phase {int(phase)+1}</h2>
    {"".join(f'<p>{p}</p>' for p in expanded['connection_to_next'].split('\n\n') if p.strip())}
    <div class="raw-answer">{answers['whats_next']}</div>
  </div>

  <div class="footer">
    Kartavya Joshi · AI Engineering · Month {month} Phase {phase} · {today}
  </div>

</div>
<script>mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});</script>
</body>
</html>"""


def main():
    answers = ask_questions()
    print("\nGenerating documentation with Gemini...")
    expanded = generate_with_gemini(answers)

    html = render_html(answers, expanded)

    month = answers['month_number'].zfill(2)
    project_slug = answers['project_name'].lower().replace(' ', '-')
    phase = answers['phase_number']
    filename = f"m{month}-{project_slug}-phase{phase}.html"
    out_path = DOCS_DIR / filename

    out_path.write_text(html, encoding='utf-8')
    print(f"\nDocumentation saved: {out_path}")
    print(f"Open in browser: file:///{out_path.as_posix()}")


if __name__ == "__main__":
    main()
