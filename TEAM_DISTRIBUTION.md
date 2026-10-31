# 👥 Team Work Distribution — 4 Members × 4.5 Hours

## Role Assignments

| Member | Role | Core Responsibility |
|---|---|---|
| **Member A** | 🔧 **Ingestion Engineer** | Document parsing, chunking, metadata extraction |
| **Member B** | 🔍 **Retrieval Engineer** | Embeddings, ChromaDB, search & re-ranking |
| **Member C** | 🧠 **RAG / Generation Lead** | Gemini prompts, grounded answers, conflict detection, confidence |
| **Member D** | 🖥️ **Frontend + Eval Lead** | Streamlit UI, API wiring, test set, evaluation report, README |

> [!IMPORTANT]
> **Integration contract:** All members code against shared data classes defined in `app/models.py` (created in the first 15 min by Member A). This lets everyone work in parallel without waiting.

---

## Shared Data Models (agree on these FIRST — 10 min all together)

```python
# app/models.py — everyone imports from here
from dataclasses import dataclass

@dataclass
class DocumentChunk:
    chunk_id: str
    text: str
    source_file: str
    doc_title: str
    page_number: int | None
    section_heading: str | None
    file_format: str          # "pdf" | "html" | "md" | "txt"

@dataclass
class RetrievedPassage:
    chunk: DocumentChunk
    relevance_score: float
    excerpt: str              # highlighted relevant portion

@dataclass
class Answer:
    text: str
    citations: list[dict]     # [{source, page, section, excerpt}]
    confidence: str           # "HIGH" | "MEDIUM" | "LOW"
    has_conflict: bool
    conflict_details: str | None
```

---

## Hour-by-Hour Per-Member Breakdown

### ⏱ Hour 1 (0:00 – 1:00)

| Member | Task | Details | Output |
|---|---|---|---|
| **A** 🔧 | **Build all 4 parsers** | PDF (PyMuPDF), HTML (BeautifulSoup), MD, TXT. Each returns raw text + metadata (title, pages, headings). | `app/ingest/parsers.py` — `parse_pdf()`, `parse_html()`, `parse_md()`, `parse_txt()` |
| **B** 🔍 | **Set up ChromaDB + embedding pipeline** | Initialize ChromaDB persistent collection, load `all-MiniLM-L6-v2`, write `index_chunks(List[DocumentChunk])` and `search(query, top_k)` functions. | `app/retrieval/indexer.py`, `app/retrieval/retriever.py` (skeleton) |
| **C** 🧠 | **Craft the Gemini prompt + answer parser** | Design the system prompt enforcing grounding, citation format, conflict surfacing, and confidence. Write the `generate_answer(question, passages)` function. Test with hardcoded passages. | `app/generation/answerer.py` |
| **D** 🖥️ | **Scaffold Streamlit UI + FastAPI routes** | Create the full UI layout (sidebar uploader, chat area, citation expanders, confidence badges). Wire placeholder API calls. Set up FastAPI skeleton with `/upload`, `/ask`, `/documents` routes. | `app/ui.py`, `app/main.py` |

> [!TIP]
> **Member C can work completely independently** in Hour 1 — just hardcode 3-4 sample passages and test prompts against Gemini. No need to wait for parsers or retrieval.

---

### ⏱ Hour 2 (1:00 – 2:00)

| Member | Task | Details | Output |
|---|---|---|---|
| **A** 🔧 | **Build chunker + integrate with parsers** | Recursive text splitter (500 tokens, 50 overlap). Prepend section headings to chunks. Write the full `ingest_document(file) → List[DocumentChunk]` pipeline. | `app/ingest/chunker.py` — tested end-to-end |
| **B** 🔍 | **Build re-ranking + retrieval polish** | Add keyword overlap scoring alongside semantic similarity. Combine scores (0.7 semantic + 0.3 keyword). Return `List[RetrievedPassage]` with scores. | `app/retrieval/retriever.py` — fully working |
| **C** 🧠 | **Build conflict detection** | Compare retrieved passages: if two passages from different docs answer the same question differently, flag conflict. Feed conflict info into the Gemini prompt. Add confidence scoring logic. | `app/generation/conflict_detector.py` |
| **D** 🖥️ | **Gather sample docs + start test set** | Find/create 3-5 sample enterprise docs (billing FAQ, product config guide, troubleshooting manual — can be fake). Start writing the 10-15 labelled test questions in JSON. | `data/sample_docs/`, `evaluation/test_set.json` (partial) |

#### 🔗 Integration Point @ 2:00 — "Ingestion → Retrieval Handshake"
> **A hands off to B:** Member A's `ingest_document()` produces `List[DocumentChunk]` → Member B's `index_chunks()` consumes them. Quick 5-min test together.

---

### ⏱ Hour 3 (2:00 – 3:00)

| Member | Task | Details | Output |
|---|---|---|---|
| **A** 🔧 | **Integration: wire ingestion → indexing** | Connect parser → chunker → embedder → ChromaDB. Test with all 4 formats. Handle edge cases (empty pages, huge files, encoding issues). | Full ingestion pipeline tested |
| **B** 🔍 | **Integration: wire retrieval → generation** | Connect `search()` → `conflict_detector()` → `generate_answer()`. Test the full RAG chain end-to-end via script. | Full RAG pipeline tested |
| **C** 🧠 | **Prompt tuning + edge cases** | Test with: conflicting docs, unanswerable questions, ambiguous queries. Tune the Gemini prompt until citations are clean, conflicts are surfaced, and "I don't know" works. | Battle-tested prompts |
| **D** 🖥️ | **Wire real API into Streamlit** | Replace placeholder calls with actual FastAPI endpoints. Add: loading spinners, error handling, file upload progress, document list. | UI talking to real backend |

#### 🔗 Integration Point @ 3:00 — "Full Pipeline Smoke Test"
> **All 4 members:** Upload a sample doc through the UI → ask a question → see a grounded answer with citations. Fix any breaks. **15-min joint debug session.**

---

### ⏱ Hour 4 (3:00 – 4:00)

| Member | Task | Details | Output |
|---|---|---|---|
| **A** 🔧 | **Polish ingestion + help D with UI** | Add upload progress feedback, file format validation, better error messages. Help Member D polish the citation display. | Production-quality ingestion |
| **B** 🔍 | **Optimize retrieval + help C test** | Tune top-K, chunk size if needed. Help Member C run the full test set through the system. | Optimized retrieval |
| **C** 🧠 | **Run full evaluation** | Execute all test questions, record retrieval hits (Recall@5, MRR), check groundedness, verify fallback behavior, document failures. | `evaluation/evaluate.py` + results |
| **D** 🖥️ | **UI polish + demo prep** | Add confidence badges (🟢🟡🔴), conflict warning banners (⚠️), expandable citation cards with highlighted excerpts. Prepare the 5 demo questions. | Demo-ready UI |

---

### ⏱ Hour 4.5 (4:00 – 4:30) — Final Sprint

| Member | Task | Time |
|---|---|---|
| **A** 🔧 | Write **README.md** — setup instructions, architecture, design decisions | 20 min |
| **B** 🔍 | Write **technical doc section** — retrieval approach, embedding choice, re-ranking strategy | 20 min |
| **C** 🧠 | Write **EVALUATION_REPORT.md** — metrics table, failure analysis, limitations | 20 min |
| **D** 🖥️ | **Final demo dry run** — prep 5 example questions, test screen recording if needed, check everything works | 20 min |
| **ALL** | **Merge docs, final commit, sanity check** | Last 10 min |

---

## Dependency & Sync Timeline

```mermaid
flowchart LR
    subgraph Hour1["Hour 1 — All Parallel"]
        A1["A: Parsers"]
        B1["B: ChromaDB + Embeddings"]
        C1["C: Gemini Prompts"]
        D1["D: UI Scaffold + API"]
    end

    subgraph Hour2["Hour 2 — Mostly Parallel"]
        A2["A: Chunker"]
        B2["B: Re-ranking"]
        C2["C: Conflict Detection"]
        D2["D: Sample Docs + Test Set"]
    end

    subgraph Sync1["🔗 Sync @ 2:00 (5 min)"]
        S1["A+B: Ingestion → Retrieval handshake"]
    end

    subgraph Hour3["Hour 3 — Integration"]
        A3["A: Wire ingestion pipeline"]
        B3["B: Wire RAG pipeline"]
        C3["C: Prompt tuning"]
        D3["D: Wire UI to API"]
    end

    subgraph Sync2["🔗 Sync @ 3:00 (15 min)"]
        S2["ALL: Full pipeline smoke test"]
    end

    subgraph Hour4["Hour 4 — Polish & Eval"]
        A4["A: Polish + help UI"]
        B4["B: Optimize + help test"]
        C4["C: Run evaluation"]
        D4["D: UI polish + demo prep"]
    end

    subgraph Final["Last 30 min — Docs & Demo"]
        A5["A: README"]
        B5["B: Technical docs"]
        C5["C: Eval report"]
        D5["D: Demo dry run"]
    end

    Hour1 --> Hour2 --> Sync1 --> Hour3 --> Sync2 --> Hour4 --> Final
```

---

## Communication Rules 📢

| Rule | Why |
|---|---|
| **Everyone codes against `app/models.py`** | No integration surprises |
| **Use a shared Git repo from minute 1** | Each member works on their own files — minimal merge conflicts |
| **Two sync checkpoints (@ 2:00 and @ 3:00)** | Catch integration bugs early, not at 4:00 |
| **Member D owns the demo** | One person practices the demo flow — smoother presentation |
| **If stuck > 15 min, ask for help** | No one should be blocked silently in a 4.5-hour hackathon |

> [!WARNING]
> **The #1 risk is integration at Hour 3.** If parsers output a different format than what ChromaDB expects, you lose 30+ minutes. That's why the shared `models.py` and the sync checkpoint at 2:00 are critical.
