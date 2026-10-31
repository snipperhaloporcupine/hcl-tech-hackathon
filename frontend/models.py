"""Data contracts shared by local ingestion, retrieval, and the UI."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedPage:
    text: str
    page_number: int | None = None


@dataclass(frozen=True)
class ParsedDocument:
    filename: str
    title: str
    file_format: str
    pages: tuple[ParsedPage, ...]


@dataclass(frozen=True)
class TextChunk:
    text: str
    chunk_index: int
    char_start: int
    char_end: int
    page_number: int | None = None


@dataclass(frozen=True)
class RetrievedPassage:
    chunk_id: str
    text: str
    filename: str
    title: str
    file_format: str
    chunk_index: int
    page_number: int | None
    char_start: int
    char_end: int
    cosine_distance: float
    similarity: float
