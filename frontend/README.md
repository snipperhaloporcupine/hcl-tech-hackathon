# Fieldnote local retrieval frontend

From the project root, install the locked dependencies once and launch the app:

```bash
uv sync
uv run streamlit run frontend/app.py
```

The first indexing operation (or first search against an indexed library) downloads `nomic-ai/nomic-embed-text-v1.5` into the Hugging Face model cache. Later runs reuse that local model. Uploaded PDF, HTML, Markdown, and TXT files are parsed, split into 300-character chunks with 30-character overlap, embedded locally, and stored in `enterprise_chroma_db/`.

The upload limit is 20 MiB per file. PDF page numbers are retained for citations. Image-only PDFs are not OCR processed. Search returns source passages and cosine similarity scores; it does not generate or synthesize an answer. No file content is sent to Gemini or another hosted generation service. Remove `enterprise_chroma_db/` to clear the local index. The original frontend under `ui/` remains separate.
