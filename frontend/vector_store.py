"""Persistent local Chroma collection for uploaded document chunks."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from functools import lru_cache
from pathlib import Path

import chromadb

from frontend.chunking import chunk_text_with_overlap
from frontend.embeddings import embed_documents, embed_query
from frontend.models import ParsedDocument, RetrievedPassage, TextChunk

DATABASE_PATH = Path(__file__).resolve().parents[1] / "enterprise_chroma_db"
COLLECTION_NAME = "enterprise_knowledge"
MAX_COSINE_DISTANCE = 0.70


@lru_cache(maxsize=1)
def get_collection():
    client = chromadb.PersistentClient(path=str(DATABASE_PATH))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def _document_id(filename: str) -> str:
    return sha256(filename.casefold().encode("utf-8")).hexdigest()[:24]


def _document_chunks(document: ParsedDocument) -> list[TextChunk]:
    chunks: list[TextChunk] = []
    for page in document.pages:
        page_chunks = chunk_text_with_overlap(page.text, page_number=page.page_number)
        for chunk in page_chunks:
            chunks.append(
                TextChunk(
                    text=chunk.text,
                    chunk_index=len(chunks),
                    char_start=chunk.char_start,
                    char_end=chunk.char_end,
                    page_number=chunk.page_number,
                )
            )
    return chunks


def index_document(document: ParsedDocument) -> int:
    """Embed and persist one document, replacing older chunks of the same name."""
    chunks = _document_chunks(document)
    if not chunks:
        raise ValueError("No readable text was found in this file.")

    document_id = _document_id(document.filename)
    chunk_ids = [f"{document_id}:{chunk.chunk_index}" for chunk in chunks]
    embeddings = embed_documents([chunk.text for chunk in chunks])
    indexed_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    metadatas = []
    for chunk in chunks:
        metadata = {
            "document_id": document_id,
            "filename": document.filename,
            "title": document.title,
            "file_format": document.file_format,
            "chunk_index": chunk.chunk_index,
            "char_start": chunk.char_start,
            "char_end": chunk.char_end,
            "indexed_at": indexed_at,
        }
        if chunk.page_number is not None:
            metadata["page_number"] = chunk.page_number
        metadatas.append(metadata)

    collection = get_collection()
    previous = collection.get(
        where={"document_id": document_id},
        include=["metadatas"],
    )
    collection.upsert(
        ids=chunk_ids,
        documents=[chunk.text for chunk in chunks],
        embeddings=embeddings,
        metadatas=metadatas,
    )
    stale_ids = set(previous.get("ids", [])) - set(chunk_ids)
    if stale_ids:
        collection.delete(ids=sorted(stale_ids))
    return len(chunks)


def list_documents() -> list[dict]:
    """Summarize persisted document metadata for the frontend library."""
    records = get_collection().get(include=["metadatas"])
    grouped: dict[str, dict] = {}
    page_sets: dict[str, set[int]] = {}
    for metadata in records.get("metadatas", []):
        if not metadata:
            continue
        document_id = str(metadata["document_id"])
        entry = grouped.setdefault(
            document_id,
            {
                "filename": str(metadata["filename"]),
                "title": str(metadata["title"]),
                "format": str(metadata["file_format"]),
                "pages": None,
                "chunks": 0,
                "uploaded_at": str(metadata["indexed_at"]),
            },
        )
        entry["chunks"] += 1
        page_number = metadata.get("page_number")
        if isinstance(page_number, int):
            page_sets.setdefault(document_id, set()).add(page_number)

    for document_id, pages in page_sets.items():
        grouped[document_id]["pages"] = len(pages)
    return sorted(grouped.values(), key=lambda document: document["filename"].casefold())


def retrieve_passages(query: str, top_k: int = 5) -> list[RetrievedPassage]:
    """Return cosine-nearest evidence within the configured distance guardrail."""
    if not query.strip() or top_k <= 0:
        return []

    collection = get_collection()
    count = collection.count()
    if count == 0:
        return []

    results = collection.query(
        query_embeddings=[embed_query(query)],
        n_results=min(top_k, count),
        include=["documents", "metadatas", "distances"],
    )
    documents = results.get("documents") or [[]]
    metadatas = results.get("metadatas") or [[]]
    distances = results.get("distances") or [[]]
    ids = results.get("ids") or [[]]
    passages: list[RetrievedPassage] = []
    for chunk_id, text, metadata, distance in zip(
        ids[0], documents[0], metadatas[0], distances[0]
    ):
        distance_value = float(distance)
        if distance_value > MAX_COSINE_DISTANCE or not metadata or not text:
            continue
        passages.append(
            RetrievedPassage(
                chunk_id=chunk_id,
                text=text,
                filename=str(metadata["filename"]),
                title=str(metadata["title"]),
                file_format=str(metadata["file_format"]),
                chunk_index=int(metadata["chunk_index"]),
                page_number=metadata.get("page_number"),
                char_start=int(metadata["char_start"]),
                char_end=int(metadata["char_end"]),
                cosine_distance=distance_value,
                similarity=max(0.0, min(1.0, 1.0 - distance_value)),
            )
        )
    return passages
