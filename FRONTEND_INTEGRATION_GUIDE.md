# Frontend UI & Integration Guide

This guide explains how the Streamlit frontend is structured, how it appears clean and professional, and the exact spots where real modules will replace the dummy data once your teammates finish their parts.

---

## 1. How Components Interlink

The frontend is built to operate independently today, but cleanly interface with the team's modules tomorrow.

```
┌─────────────────────────────────────────────────────────────┐
│                     app/ui.py (Streamlit)                   │
└──────────────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
   [TODAY: Dummy Mode]                 [LATER: Production Mode]
   Imports from:                       Imports directly or via FastAPI:
   app/dummy_data.py                   1. Document List
   • dummy_get_documents()                └── app.retrieval.indexer.list_indexed_documents()
   • dummy_upload_documents()          2. Ingestion Pipeline
   • dummy_ask_question()                 └── app.ingest.parsers.parse()
                                          └── app.ingest.chunker.chunk()
                                          └── app.retrieval.indexer.index()
                                       3. Q&A / RAG Pipeline
                                          └── app.retrieval.retriever.retrieve()
                                          └── app.generation.conflict_detector.detect()
                                          └── app.generation.answerer.generate()
```

Both dummy mode and production mode share the exact same data contracts in [`app/models.py`](file:///C:/Users/tejas/hcl-tech-hackathon/app/models.py). This guarantees zero UI refactoring when switching to real logic.

---

## 2. Where to Replace Stuff in [`app/ui.py`](file:///C:/Users/tejas/hcl-tech-hackathon/app/ui.py)

There are only **3 replacement hooks** in `app/ui.py`:

### Hook 1: Document Listing (Sidebar)
* **Current location**: Lines ~18-20 and Line ~200
* **Current call**: `dummy_get_documents()`
* **What to replace with**:
  ```python
  # from app.retrieval.indexer import list_indexed_documents
  st.session_state.documents = list_indexed_documents()
  ```
* **Data shape expected**: List of dicts with:
  `{"filename": str, "title": str, "format": str, "pages": int | None, "chunks": int}`

---

### Hook 2: Document Ingestion (File Uploader)
* **Current location**: Lines ~230-245
* **Current call**: `result = dummy_upload_documents(uploaded_files)`
* **What to replace with**:
  ```python
  # from app.ingest.parsers import parse_document
  # from app.ingest.chunker import chunk_document
  # from app.retrieval.indexer import index_chunks

  total_chunks = 0
  for file in uploaded_files:
      raw_doc = parse_document(file)
      chunks = chunk_document(raw_doc)
      index_chunks(chunks)
      total_chunks += len(chunks)
  ```

---

### Hook 3: Query & Grounded Answer (Chat Area)
* **Current location**: Lines ~320-335
* **Current call**: `answer, passages = dummy_ask_question(active_question)`
* **What to replace with**:
  ```python
  # from app.retrieval.retriever import retrieve_passages
  # from app.generation.conflict_detector import detect_conflicts
  # from app.generation.answerer import generate_grounded_answer

  # 1. Retrieve top-k passages with relevance scores
  passages = retrieve_passages(active_question, top_k=5)

  # 2. Check if passages from different sources disagree
  has_conflict, conflict_summary = detect_conflicts(passages)

  # 3. Call Gemini with strict grounding system prompt
  answer = generate_grounded_answer(
      question=active_question,
      passages=passages,
      has_conflict=has_conflict,
      conflict_summary=conflict_summary
  )
  ```

---

## 3. UI Styling: Clean & "Less AI"

Instead of dark futuristic cyber themes, robotic avatars, or generic chat bubbles, this UI uses an **enterprise document search design**:

1. **Subtle Neutrals**: Clean off-white canvas (`#ffffff`), soft slate message boxes (`#f0f2f5`), and crisp borders (`#e2e5ea`).
2. **Confidence Badges**: Explicit `HIGH CONFIDENCE`, `MEDIUM CONFIDENCE`, or `LOW CONFIDENCE` tags to meet FR-07 immediately.
3. **Dispute / Conflict Alerts**: Amber banner (`#fff8e1` with `#f9a825` border) when sources contradict (FR-06).
4. **Inspectable Citations**: Expandable source cards showing Document Title, Page Number, Section Header, and exact highlighted excerpts (FR-05).
5. **Retrieval Score Bars**: Visual relevance percentages for every retrieved passage so judges can inspect retrieval ranking quality (Evaluation Guidance).

---

## 4. How to Run & Demo the Frontend Right Now

Once dependencies finish installing:

```powershell
# In terminal inside c:\Users\tejas\hcl-tech-hackathon:
.\venv\Scripts\streamlit.exe run app/ui.py
```

### Try These 3 Questions to Demonstrate Capabilities:
1. **Direct Answer (High Confidence)**:
   > *"How do I request a refund?"*
   * Shows: 30-day policy, citations to `billing_policy_2024.pdf` with page numbers.
2. **Contradictory Sources (Conflict Handling)**:
   > *"What is the API rate limit?"*
   * Shows: Warning banner showing the disagreement between `Product Configuration Guide` (1,000 req/min) and `Troubleshooting FAQ` (500 req/min).
3. **Out-of-Scope (Fallback / Not Found)**:
   > *"What is the onboarding process?"*
   * Shows: Low confidence badge and a clear "information not found in knowledge base" disclaimer rather than a hallucinated answer.

