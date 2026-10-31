"""Lazy local Nomic text embeddings for documents and search queries."""

from __future__ import annotations

from functools import lru_cache

MODEL_NAME = "nomic-ai/nomic-embed-text-v1.5"
EMBED_BATCH_SIZE = 32


@lru_cache(maxsize=1)
def get_embedder():
    """Load the local encoder only when a user first indexes or searches."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def embed_documents(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    vectors = get_embedder().encode(
        [f"search_document: {text}" for text in texts],
        batch_size=EMBED_BATCH_SIZE,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return vectors.tolist()


def embed_query(query: str) -> list[float]:
    vector = get_embedder().encode(
        [f"search_query: {query}"],
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return vector[0].tolist()
