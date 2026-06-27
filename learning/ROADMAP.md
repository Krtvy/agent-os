# 6-Month AI Engineer Learning Roadmap
## Kartavya Joshi — Target: AI Engineer title

### Learning Flow (every phase, every concept)
1. I give you → exact resources to read/watch (specific, not generic)
2. You research → read those, take notes
3. I explain → concept explanation tailored to what you read
4. We build → implement together step by step
5. You answer 5 questions → run `python learning/generate_doc.py`
6. System generates → beautiful HTML documentation

---

## MONTH 1 — RAG SYSTEM FROM SCRATCH
**Goal: Build a document Q&A system that actually works and is evaluated**
**Concepts: Chunking, Embeddings, Vector Search, Retrieval, Evaluation**

### Phase 1 — Chunking & Embeddings
**What you build:** Load a PDF, split it into chunks 3 ways, embed them, compare quality
**Concept taught:** Why chunking strategy changes everything. What embeddings actually are.

Resources to read before we build:
- https://www.pinecone.io/learn/chunking-strategies/ (20 min)
- https://simonwillison.net/2023/Oct/23/embeddings/ (15 min)
- Watch: https://www.youtube.com/watch?v=ySus5ZS0b94 (Greg Kamradt, 20 min)

After reading → I explain → we build → 5 questions → `generate_doc.py`

---

### Phase 2 — Vector Database & Retrieval
**What you build:** Store chunks in pgvector, retrieve top-K, understand why naive retrieval fails
**Concept taught:** How vector search works. Cosine similarity. ANN. Why top-K alone isn't enough.

Resources:
- https://www.pinecone.io/learn/vector-database/ (25 min)
- https://supabase.com/docs/guides/ai/vector-columns (practical pgvector, 15 min)
- https://www.sbert.net/examples/applications/retrieve_rerank/README.html (reranking, 15 min)

---

### Phase 3 — RAG Evaluation with RAGAS
**What you build:** 20-question golden dataset. Score your RAG. Find where it fails.
**Concept taught:** How to MEASURE if AI is working. The 3 RAGAS metrics. LLM-as-judge.

Resources:
- https://docs.ragas.io/en/latest/concepts/metrics/ (30 min)
- https://hamel.dev/blog/posts/evals/ (Hamel Husain, 20 min — the definitive eval guide)

---

### Phase 4 — Deploy & Document
**What you build:** Docker container. FastAPI endpoint. Deploy to Render (free).
**Concept taught:** Production deployment. API design. README that impresses.

Resources:
- https://fastapi.tiangolo.com/tutorial/ (skim the key parts, 30 min)
- https://docs.docker.com/get-started/ (Part 1 only, 20 min)

**End of Month 1 deliverable:** Live URL. 4 phase HTMLs. GitHub repo with DECISIONS.md.

---

## MONTH 2 — TOOL-CALLING AGENT
**Goal: Build a research agent that searches, reads, synthesises with memory**
**Concepts: LangGraph state machines, tool design, agent memory, trajectory evaluation**

### Phase 1 — LangGraph Fundamentals
**What you build:** A graph with 3 nodes and 2 conditional edges
**Concept taught:** Why graphs beat chains. State, nodes, edges. When to use conditional routing.

Resources:
- https://langchain-ai.github.io/langgraph/concepts/ (official concepts, 30 min)
- https://www.youtube.com/watch?v=R8KB-Zcynxc (LangGraph crash course, 25 min)

---

### Phase 2 — Tool Design & Execution
**What you build:** Agent with WebSearch + ArXiv + GitHub tools. It picks the right one.
**Concept taught:** Tool schemas. Why tool descriptions matter as much as prompts. Error recovery.

Resources:
- https://docs.anthropic.com/en/docs/build-with-claude/tool-use (official, 20 min)
- https://blog.langchain.dev/tool-calling-with-langchain/ (15 min)

---

### Phase 3 — Agent Memory
**What you build:** Agent remembers past research sessions using OpenMemory
**Concept taught:** Short vs long-term memory. Why memory architecture matters.

Resources:
- https://mem0.ai/blog/state-of-ai-agent-memory-2026 (25 min)
- OpenMemory docs (already installed in your stack)

---

### Phase 4 — Trajectory Evaluation
**What you build:** Eval that scores not just output but whether agent took right steps
**Concept taught:** Why final-output eval misses 30% of failures. Trajectory scoring.

---

## MONTH 3 — FINE-TUNING A SMALL MODEL
**Goal: Fine-tune Llama 3.2-3B on a specific task. Prove it improved with evals.**
**Concepts: Transformers intuition, HuggingFace, LoRA/PEFT, Dataset creation, Before/after eval**

### Phase 1 — Transformer Intuition (NO MATH)
**What you build:** Nothing yet. You READ and I explain until you can describe attention in plain English.
**Concept taught:** What transformers actually do. Attention mechanism intuition. Tokens.

Resources:
- https://jalammar.github.io/illustrated-transformer/ (the best visual explanation, 45 min)
- https://www.youtube.com/watch?v=wjZofJX0v4M (Andrej Karpathy, 15 min excerpt)

---

### Phase 2 — HuggingFace & Datasets
**What you build:** Load a model, tokenise text, understand what happens
**Concept taught:** HuggingFace ecosystem. How models are stored and loaded. Dataset formats.

Resources:
- https://huggingface.co/learn/nlp-course/chapter1/1 (Chapter 1 only, 30 min)

---

### Phase 3 — LoRA Fine-Tuning
**What you build:** Fine-tune Llama 3.2-3B on Google Colab (free T4 GPU)
**Concept taught:** Why LoRA works. What rank means. How PEFT saves GPU memory.

Resources:
- https://huggingface.co/blog/lora (official LoRA blog, 20 min)
- https://www.youtube.com/watch?v=eC6Hd1hFvos (LoRA explained visually, 15 min)

---

### Phase 4 — Eval Before/After
**What you build:** Score the base model vs fine-tuned on 20 test cases. Publish to HuggingFace Hub.
**Concept taught:** How to prove a model improved. Benchmark design.

---

## MONTH 4 — LLM EVALUATION PLATFORM (Tool others can use)
**Goal: Build something other engineers will use. GitHub stars = credibility.**
**Concepts: RAGAS deep, LLM-as-judge, CI gates, Regression tracking**

Phases: RAGAS integration → LLM judge → GitHub Action CI → Streamlit dashboard

---

## MONTH 5 — COST-OPTIMISED LLM GATEWAY
**Goal: Cut LLM costs 50%. Immediately valuable to freelance clients.**
**Concepts: Model routing, Semantic caching, Token budgeting, LiteLLM**

Phases: LiteLLM proxy → model routing logic → semantic caching → cost dashboard

---

## MONTH 6 — POLISH & LAND THE JOB
**Goal: 5 deployed projects. 20 phase docs. Active applications.**

Week 1-2: Polish every project (README, DECISIONS.md, live URL, demo video)
Week 3: System design interview prep (AI-specific questions)
Week 4: Apply to 5 companies + 10 Upwork proposals + Turing assessment

---

## HOW TO USE THIS
Each phase starts with a conversation:
"I'm starting Month X, Phase Y — give me the resources and then explain the concept."

After building, run:
```
cd C:\Users\Rawdy\agents\observer-test
python learning/generate_doc.py
```

Docs save to: `learning/docs/`
