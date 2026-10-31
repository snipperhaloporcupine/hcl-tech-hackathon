# hcl-tech-hackathon

## Run the local document search frontend

From the project root, install the locked dependencies and start Streamlit:

```bash
uv sync
uv run streamlit run frontend/app.py
```

The app starts without ChromaDB data or the embedding model already downloaded. It creates the local Chroma database on first use, and downloads the embedding model when you first index a document or search an indexed library. To start the connected legacy UI instead, run `uv run streamlit run ui/app/ui.py`. Both interfaces use the same parser, local embeddings, and persistent Chroma index. See [frontend/README.md](frontend/README.md) for supported files and storage details.
