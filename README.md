# Fieldnote — local document search

Fieldnote is a privacy-conscious document search workspace built for the HCL Tech Hackathon. Upload reference material, index it locally, and ask questions to surface the most relevant source passages with citations and similarity scores.

## What it does

- Accepts PDF, HTML, Markdown, and plain-text documents (up to 20 MiB each).
- Extracts text locally and preserves PDF page numbers for returned citations.
- Splits documents into whitespace-aware 300-character chunks with 30-character overlap.
- Uses the local `nomic-ai/nomic-embed-text-v1.5` embedding model and a persistent Chroma vector index.
- Searches the library using cosine similarity and returns the top matching passages.
- Includes bundled sample documents in `dataset/` that can be indexed from the sidebar.

## Quick start

Requirements: Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run streamlit run frontend/app.py
```

Open the local address shown by Streamlit, then either upload documents or select **Index bundled sample library** in the sidebar. The first indexing or search operation downloads the embedding model; subsequent runs reuse its local cache.

## How it works

```text
Document upload → text extraction → overlapping chunks → local embeddings → Chroma index
Question       → query embedding → cosine similarity search → cited source passages
```

The application is retrieval-only: it does not generate synthesized answers. This makes it easier to inspect the exact source text returned for a question.

## Local data and privacy

The persistent vector index is created at `enterprise_chroma_db/` in the project root. It is ignored by Git. Delete that directory to reset the indexed library.

Document contents are parsed, embedded, and searched locally. The first use of the embedding model downloads model files to the Hugging Face cache. The app does not send document contents to Gemini or another hosted text-generation service.

## Supported files and limitations

| File type | Notes |
| --- | --- |
| PDF | Text-based PDFs only; encrypted and image-only/scanned PDFs are not supported. |
| HTML / HTM | Extracted as local markup; linked resources are not fetched. |
| Markdown / TXT | Read as UTF-8 text (with replacement for invalid characters). |

Search results are filtered by a cosine-distance threshold of 0.70, so a question may return no passages when the indexed material is not sufficiently relevant.

## Project layout

```text
frontend/
  app.py              Streamlit user interface
  document_parser.py  Safe local extraction and validation
  chunking.py          Text chunking with overlap and offsets
  embeddings.py        Lazy local embedding-model loader
  vector_store.py      Persistent Chroma indexing and retrieval
dataset/               Bundled sample documents
evaluation/            Evaluation inputs and results
```

For implementation-level details, see [frontend/README.md](frontend/README.md).
