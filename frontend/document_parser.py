"""Safe, local text extraction for supported user-uploaded documents."""

from __future__ import annotations

from io import BytesIO
from pathlib import PurePosixPath

import trafilatura

MAX_UPLOAD_BYTES = 20 * 1024 * 1024
SUPPORTED_FORMATS = {"pdf", "html", "htm", "md", "txt"}


class DocumentParseError(ValueError):
    """A safe-to-display error tied to one uploaded document."""


def _safe_filename(filename: str) -> str:
    normalized = filename.replace("\\", "/")
    name = PurePosixPath(normalized).name.strip()
    if not name or name in {".", ".."}:
        raise DocumentParseError("The uploaded file has no valid filename.")
    return name


def _normalize_text(text: str) -> str:
    return text.replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n").strip()


def parse_document(filename: str, content: bytes) -> "ParsedDocument":
    """Extract text and source metadata from a supported upload.

    No user-provided path is opened and HTML is parsed as input text without
    fetching its links. The size cap is checked before invoking format parsers.
    """
    from frontend.models import ParsedDocument, ParsedPage

    safe_name = _safe_filename(filename)
    suffix = safe_name.rsplit(".", maxsplit=1)[-1].lower() if "." in safe_name else ""
    if suffix not in SUPPORTED_FORMATS:
        raise DocumentParseError("Use a PDF, HTML, Markdown, or TXT file.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise DocumentParseError("The file exceeds the 20 MiB upload limit.")
    if not content:
        raise DocumentParseError("The file is empty.")

    file_format = "html" if suffix == "htm" else suffix
    if suffix == "pdf":
        if not content.startswith(b"%PDF-"):
            raise DocumentParseError("The file does not have a valid PDF signature.")
        try:
            from pypdf import PdfReader

            reader = PdfReader(BytesIO(content), strict=False)
            if reader.is_encrypted:
                raise DocumentParseError("Encrypted PDFs are not supported.")
            pages = tuple(
                ParsedPage(_normalize_text(page.extract_text() or ""), page_number=index + 1)
                for index, page in enumerate(reader.pages)
            )
        except DocumentParseError:
            raise
        except Exception as exc:
            raise DocumentParseError("Could not read this PDF. Check that it is not damaged.") from exc
    elif suffix in {"html", "htm"}:
        markup = content.decode("utf-8", errors="replace")
        extracted = trafilatura.extract(markup, include_comments=False, include_tables=True) or ""
        pages = (ParsedPage(_normalize_text(extracted)),)
    else:
        extracted = content.decode("utf-8", errors="replace")
        pages = (ParsedPage(_normalize_text(extracted)),)

    if not any(page.text for page in pages):
        raise DocumentParseError("No readable text was found in this file. Scanned PDFs need OCR.")

    title = safe_name.rsplit(".", maxsplit=1)[0] if "." in safe_name else safe_name
    return ParsedDocument(
        filename=safe_name,
        title=title.replace("_", " ").strip(),
        file_format=file_format,
        pages=pages,
    )
