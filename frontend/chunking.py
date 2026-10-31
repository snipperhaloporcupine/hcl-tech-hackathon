"""Whitespace-aware overlapping text chunks with source offsets."""

from frontend.models import TextChunk

DEFAULT_CHUNK_SIZE = 300
DEFAULT_CHUNK_OVERLAP = 30


def _last_whitespace(text: str, start: int, end: int) -> int | None:
    for index in range(min(end, len(text)) - 1, start - 1, -1):
        if text[index].isspace():
            return index
    return None


def chunk_text_with_overlap(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
    *,
    page_number: int | None = None,
) -> list[TextChunk]:
    """Split text into bounded character windows, preserving useful overlap.

    Chunk boundaries move to nearby whitespace when at least half of the
    requested window remains. If a single token is longer than the window,
    hard splitting is used to guarantee forward progress.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")
    if not text or not text.strip():
        return []

    chunks: list[TextChunk] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            boundary = _last_whitespace(text, start + chunk_size // 2, end)
            if boundary is not None:
                end = boundary

        raw_text = text[start:end]
        leading = len(raw_text) - len(raw_text.lstrip())
        chunk_text = raw_text.strip()
        if chunk_text:
            char_start = start + leading
            char_end = char_start + len(chunk_text)
            chunks.append(
                TextChunk(
                    text=chunk_text,
                    chunk_index=len(chunks),
                    char_start=char_start,
                    char_end=char_end,
                    page_number=page_number,
                )
            )

        if end >= len(text):
            break

        next_start = max(start + 1, end - overlap)
        # Move a chunk start to the next word boundary where possible. This can
        # shorten overlap, but avoids embedding fragments cut from word starts.
        if next_start > 0 and not text[next_start - 1].isspace() and not text[next_start].isspace():
            next_boundary = next(
                (index for index in range(next_start, end) if text[index].isspace()),
                None,
            )
            if next_boundary is not None:
                next_start = next_boundary + 1
        start = next_start

    return chunks
