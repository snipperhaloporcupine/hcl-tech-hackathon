# 🏆 HCL Hackathon Battle Plan — Enterprise Doc Q&A Assistant
## 4.5 Hour Build → Working Prototype

> [!IMPORTANT]
> **Goal:** Build a RAG (Retrieval-Augmented Generation) system that ingests PDF/HTML/MD/TXT docs, retrieves relevant passages, and answers questions with citations — all grounded in evidence.

---

## Recommended Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **Backend** | **Python + FastAPI** | Fastest to prototype, huge ecosystem for AI/NLP |
| **LLM** | **Google Gemini API** (free tier / API key) | Fast, generous free tier, great at grounded answers |
| **Embeddings** | **`sentence-transformers/all-MiniLM-L6-v2`** | Fast, lightweight, runs locally, no API cost |
| **Vector Store** | **ChromaDB** (in-process, no server) | Zero setup, persistent, perfect for hackathons |
| **Document Parsing** | **PyMuPDF (fitz)** for PDF, **BeautifulSoup** for HTML, **markdown** lib for MD | Covers all required formats |
| **Frontend** | **Streamlit** | Beautiful UI in ~50 lines of Python, zero JS needed |
| **Evaluation** | **Custom script + RAGAS** (optional) | Retrieval & answer quality metrics |

> [!TIP]
> **Why NOT LangChain?** For a hackathon, direct API calls are simpler to debug and demo. Less magic, more control, better for judges.

---

## Hour-by-Hour Execution Plan

### ⏱ Hour 1 (0:00 – 1:00) — Foundation & Ingestion Pipeline

**Tasks:**
1. **Project setup** (10 min)
   - Create project structure, virtual env, install deps
   - `pip install fastapi uvicorn streamlit chromadb sentence-transformers pymupdf beautifulsoup4 google-generativeai python-multipart`

2. **Document parsers** (30 min) — `app/ingest/parsers.py`
   - PDF parser using PyMuPDF → extract text per page with page numbers
   - HTML parser using BeautifulSoup → strip tags, preserve headings
   - Markdown parser → convert to plain text, preserve structure
   - TXT parser → direct read
   - Each returns: `{ text, title, source_file, page/section, format }`

3. **Chunking engine** (20 min) — `app/ingest/chunker.py`
   - Recursive text splitter: **chunk_size=500 tokens, overlap=50 tokens**
   - Preserve metadata (doc title, section heading, page number) per chunk
   - Handle heading hierarchy — prepend parent heading to chunks for context

**Deliverable:** Can parse any PDF/HTML/MD/TXT and get clean, metadata-rich chunks.

---

### ⏱ Hour 2 (1:00 – 2:00) — Embedding, Indexing & Retrieval

**Tasks:**
1. **Embedding & indexing** (25 min) — `app/retrieval/indexer.py`
   - Load `all-MiniLM-L6-v2` via sentence-transformers
   - Embed all chunks → store in ChromaDB with metadata
   - ChromaDB collection per "knowledge base" upload session

2. **Retrieval engine** (35 min) — `app/retrieval/retriever.py`
   - Semantic search: embed query → cosine similarity in ChromaDB → top-K (K=5)
   - **Re-ranking** (simple): score by (semantic_sim × 0.7 + keyword_overlap × 0.3)
   - Return ranked passages with metadata + relevance score
   - Handle paraphrases naturally (embeddings already handle this!)

**Deliverable:** Ask a question → get top 5 ranked passages with source info.

---

### ⏱ Hour 3 (2:00 – 3:00) — Answer Generation (The Core RAG)

**Tasks:**
1. **Grounded answer generator** (40 min) — `app/generation/answerer.py`
   - Craft a **system prompt** that enforces:
     - ✅ Answer ONLY from provided passages
     - ✅ Cite `[Source: doc_name, page/section]` for every claim
     - ✅ If passages contradict → surface the conflict explicitly
     - ✅ If evidence is weak/missing → say "I don't have enough information" or ask clarifying questions
     - ✅ Return a confidence level (HIGH / MEDIUM / LOW)
   - Call Gemini API with context passages + question
   - Parse structured response (answer + citations + confidence)

2. **Conflict detection** (20 min) — `app/generation/conflict_detector.py`
   - Before generating: check if retrieved passages contain contradictory info
   - Simple approach: if passages from different docs answer the same sub-question differently, flag it
   - Pass conflict flag to LLM prompt so it highlights it in the answer

**Deliverable:** Full RAG pipeline — question in → grounded answer with citations out.

---

### ⏱ Hour 4 (3:00 – 4:00) — Frontend + API + Polish

**Tasks:**
1. **FastAPI backend** (15 min) — `app/api.py`
   - `POST /upload` → accept multiple files, run ingestion pipeline
   - `POST /ask` → accept question, return answer + citations + confidence
   - `GET /documents` → list indexed documents

2. **Streamlit frontend** (30 min) — `app/ui.py`
   - Sidebar: file uploader (multi-file, drag & drop)
   - Main area: chat-style Q&A interface
   - Answer display: formatted answer + expandable citations with highlighted excerpts
   - Confidence badge: 🟢 HIGH / 🟡 MEDIUM / 🔴 LOW
   - Conflict alerts: ⚠️ banner when sources disagree

3. **Integration testing** (15 min)
   - Upload sample docs, ask test questions, fix bugs

**Deliverable:** Fully working web app you can demo live.

---

### ⏱ Hour 4.5 (4:00 – 4:30) — Evaluation & Documentation

**Tasks:**
1. **Test set creation** (10 min) — `evaluation/test_set.json`
   - Create 10-15 labelled questions:
     - 5 directly answerable
     - 3 paraphrased versions
     - 2 with conflicting evidence across docs
     - 2 unanswerable (out of scope)
     - 2 ambiguous

2. **Evaluation script** (10 min) — `evaluation/evaluate.py`
   - Retrieval: check if gold passage appears in top-K (Recall@K, MRR)
   - Groundedness: verify claims trace to citations (manual spot check)
   - Fallback: verify "not found" for unanswerable questions

3. **README & report** (10 min)
   - Setup instructions, architecture diagram, design decisions
   - Evaluation results table
   - Known limitations & trade-offs

**Deliverable:** Complete submission package.

---

## Project Structure

```
hcl-tech-hackathon/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry
│   ├── ui.py                 # Streamlit frontend
│   ├── config.py             # API keys, settings
│   ├── ingest/
│   │   ├── __init__.py
│   │   ├── parsers.py        # PDF, HTML, MD, TXT parsers
│   │   └── chunker.py        # Text splitting + metadata
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── indexer.py        # Embedding + ChromaDB storage
│   │   └── retriever.py      # Semantic search + re-ranking
│   └── generation/
│       ├── __init__.py
│       ├── answerer.py       # Gemini RAG answer generation
│       └── conflict_detector.py
├── evaluation/
│   ├── test_set.json         # Labelled Q&A pairs
│   └── evaluate.py           # Metrics computation
├── data/
│   └── sample_docs/          # Test documents
├── chroma_db/                # ChromaDB persistent storage
├── requirements.txt
├── README.md
└── EVALUATION_REPORT.md
```

---

## Key Design Decisions (for judges)

| Decision | Rationale |
|---|---|
| **ChromaDB over FAISS** | Persistent storage, metadata filtering, simpler API |
| **Small embedding model** | Runs locally, no API dependency for embeddings, fast indexing |
| **Gemini for generation** | Free tier sufficient, excellent at following grounding instructions |
| **500-token chunks with 50 overlap** | Balance between context preservation and retrieval precision |
| **No LangChain** | Direct control over prompts and pipeline, easier to debug and explain |
| **Confidence scoring** | Maps directly to FR-07, differentiates from basic RAG demos |
| **Conflict detection** | Maps directly to FR-06, most teams will skip this |

---

## What Will Impress Judges 🎯

1. **Conflict handling** (FR-06) — Most teams will ignore this. Show a demo where two docs disagree and your system surfaces it.
2. **"I don't know" responses** (FR-07) — Ask something out of scope and show it gracefully declines.
3. **Rich citations** — Don't just say "Source: doc.pdf". Show `[Source: billing_guide.pdf, Page 12, Section: "Refund Policy"]` with the relevant excerpt highlighted.
4. **Evaluation metrics** — Even basic Recall@5 and MRR show rigor.
5. **Clean live demo** — Upload docs live, ask questions, show the system working in real time.

> [!CAUTION]
> **Common pitfalls to avoid:**
> - Don't spend time on user auth, databases, or deployment — it's a prototype
> - Don't over-engineer chunking — simple recursive split works great
> - Don't use LangChain/LlamaIndex if you can't explain every step to judges
> - Don't forget to handle the "unanswerable question" case — judges WILL test this
