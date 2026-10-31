"""Redesigned document Q&A workspace, backed by local demo responses."""

from __future__ import annotations

from html import escape
from pathlib import Path
import sys

import streamlit as st

# Streamlit may put `frontend/` rather than the project root on sys.path when
# it launches this file directly. Keep the package import stable from either.
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from frontend.document_parser import DocumentParseError, parse_document
from frontend.vector_store import index_document, list_documents, retrieve_passages


st.set_page_config(
    page_title="Fieldnote | Knowledge workspace",
    page_icon="F",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
      --ink: #202720;
      --muted: #727970;
      --paper: #f6f5f0;
      --panel: #fffefa;
      --line: #e6e5dc;
      --moss: #60735a;
      --clay: #b66e4d;
    }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: var(--paper); color: var(--ink); }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebarCollapsedControl"] {
      display:flex !important;
      visibility:visible !important;
      opacity:1 !important;
      color:#202720 !important;
      background:#d8dfc9 !important;
      border:1px solid #60735a !important;
      border-radius:0 7px 7px 0 !important;
      z-index:1001 !important;
    }
    #MainMenu, footer { visibility: hidden; }
    .block-container { max-width: 1120px; padding: 2.3rem 2.6rem 5.5rem; }

    section[data-testid="stSidebar"] {
      background: #242d26;
      border-right: 1px solid #354037;
    }
    section[data-testid="stSidebar"] > div { padding: 1.3rem 1.1rem 1.5rem; }
    section[data-testid="stSidebar"] * { color: #e8ebe4; }
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
      background: #303a32; border: 1px dashed #647163; border-radius: 8px;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
      background: #455342; border: 0; color: #f5f6f2;
    }
    section[data-testid="stSidebar"] .stButton > button {
      color: #e8ebe4; background: #303a32; border: 1px solid #465247;
      text-align: left; border-radius: 7px;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
      border-color: #a9b29e; color: #fff;
    }
    .brand { display:flex; align-items:center; gap:10px; margin: 0 0 2px; }
    .brand-mark { display:grid; place-items:center; width:30px; height:30px; border-radius:8px;
      background:#d8dfc9; color:#243026; font:800 17px 'Manrope',sans-serif; }
    .brand-name { font:700 17px 'Manrope',sans-serif; letter-spacing:-.4px; }
    .side-label { margin: 1.5rem 0 .55rem; color:#9da79b; text-transform:uppercase;
      letter-spacing:.11em; font-size:10px; font-weight:700; }
    .side-meta { color:#aeb6ac; font-size:12px; margin: 3px 0 10px; }
    .doc-row { padding: 10px 8px; margin: 3px 0; border-radius:6px; }
    .doc-title { font-size:12px; font-weight:600; line-height:1.4; }
    .doc-detail { color:#aeb6ac; font-size:10px; margin-top:3px; }
    .file-tag { display:inline-block; color:#ccd5c4; border:1px solid #596455; border-radius:3px;
      padding:1px 5px; font-size:9px; letter-spacing:.05em; margin-right:5px; text-transform:uppercase; }

    .topline { display:flex; align-items:center; gap:9px; color:var(--muted); font-size:12px;
      font-weight:600; letter-spacing:.02em; margin-bottom:13px; }
    .status-dot { width:7px; height:7px; border-radius:50%; background:#7a9870; display:inline-block; }
    h1 { font:700 clamp(30px, 4vw, 43px)/1.15 'Manrope',sans-serif !important;
      letter-spacing:-1.8px !important; color:var(--ink) !important; margin:0 0 10px !important; }
    .intro { color:#697168; font-size:14px; line-height:1.7; max-width:620px; margin-bottom:28px; }
    .section-kicker { color:#8b8e83; font-size:10px; text-transform:uppercase; letter-spacing:.13em;
      font-weight:700; margin:20px 0 9px; }
    .prompt-card { border:1px solid var(--line); border-radius:8px; background:#fbfaf6;
      padding:12px 14px; min-height:67px; color:#454b42; font-size:12px; line-height:1.5; }
    .answer-wrap { background:var(--panel); border:1px solid var(--line); border-radius:10px;
      padding:20px 22px; margin:5px 0 12px; }
    .answer-top { display:flex; align-items:center; justify-content:space-between; gap:10px;
      margin-bottom:15px; color:#7c8075; font-size:11px; }
    .answer-copy { color:#333a32; font-size:14px; line-height:1.78; white-space:pre-line; }
    .conflict { background:#f5eee1; color:#725331; border-left:3px solid #bc8953;
      border-radius:0 6px 6px 0; padding:12px 14px; margin:8px 0 12px; font-size:12px; line-height:1.55; }
    .source-card { background:#fbfaf6; border:1px solid var(--line); border-radius:7px;
      padding:12px 14px; margin:7px 0; }
    .source-name { color:#4f624a; font-size:12px; font-weight:700; }
    .source-meta { color:#8a8d83; font-size:10px; margin:3px 0 8px; }
    .source-quote { color:#575e54; border-left:2px solid #bbc6b1; padding-left:10px;
      font-size:11px; line-height:1.6; }
    .score-line { display:flex; align-items:center; gap:8px; margin:7px 0; }
    .score-track { height:4px; flex:1; background:#e8e9e1; border-radius:3px; overflow:hidden; }
    .score-fill { height:100%; background:#758b6d; border-radius:3px; }
    .score-value { width:32px; text-align:right; color:#727970; font-size:10px; }
    .empty-panel { border:1px dashed #d6d6ca; background:#faf9f5; border-radius:10px;
      padding:27px 25px; margin:18px 0 20px; }
    .empty-mark { display:grid; place-items:center; width:38px; height:38px; border-radius:9px;
      background:#e9ede2; color:#63765b; font:700 17px 'Manrope',sans-serif; margin-bottom:13px; }
    .empty-title { font:700 16px 'Manrope',sans-serif; letter-spacing:-.3px; }
    .empty-copy { color:#787d73; font-size:12px; line-height:1.6; margin-top:5px; }
    div[data-testid="stChatInput"] { border-color:#deded4; background:#fffefa; }
    div[data-testid="stChatInput"] textarea,
    div[data-testid="stChatInput"] textarea:focus {
      color:#202720 !important;
      -webkit-text-fill-color:#202720 !important;
      caret-color:#202720 !important;
      background:#fffefa !important;
      font-size:13px;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
      color:#727970 !important;
      -webkit-text-fill-color:#727970 !important;
      opacity:1;
    }
    div[data-testid="stExpander"] { border-color:var(--line); background:transparent; border-radius:7px; }
    .stButton > button[kind="primary"] { background:#60735a; border-color:#60735a; }
    .stButton > button[kind="primary"]:hover { background:#4e624a; border-color:#4e624a; }

    @media (max-width: 700px) {
      .block-container { padding:1.5rem 1rem 4.5rem; }
      section[data-testid="stSidebar"] > div { padding:.9rem .8rem 1rem; }
      .answer-wrap { padding:16px; }
      h1 { letter-spacing:-1px !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
try:
    st.session_state.documents = list_documents()
    st.session_state.library_error = False
except Exception:
    st.session_state.documents = st.session_state.get("documents", [])
    st.session_state.library_error = True


def render_passage(passage, index: int) -> None:
    percentage = max(0, min(100, round(passage.similarity * 100)))
    location = f"Page {passage.page_number} · " if passage.page_number else ""
    st.markdown(
        f"""<div class="source-card">
          <div class="source-name">[{index}] {escape(passage.title)}</div>
          <div class="source-meta">{escape(passage.filename)} · {location}Passage {passage.chunk_index + 1}</div>
          <div class="score-line"><div class="score-track"><div class="score-fill" style="width:{percentage}%"></div></div><div class="score-value">{percentage}%</div></div>
          <div class="source-meta">Cosine similarity · distance {passage.cosine_distance:.3f}</div>
          <div class="source-quote">{escape(passage.text)}</div>
        </div>""",
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">F</div><div class="brand-name">fieldnote</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-meta">Knowledge workspace</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-label">Add to your library</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Choose documents",
        type=["pdf", "html", "htm", "md", "txt"],
        accept_multiple_files=True,
        help="PDF, HTML, Markdown, and plain text",
    )

    dataset_files = sorted((Path(_project_root) / "dataset").glob("*.md"))
    if dataset_files and st.button(
        f"Index bundled dataset ({len(dataset_files)} files)",
        use_container_width=True,
    ):
        indexed_files = 0
        indexed_chunks = 0
        errors: list[tuple[str, str]] = []
        with st.spinner("Loading the local model and indexing bundled documents…"):
            for dataset_file in dataset_files:
                try:
                    document = parse_document(dataset_file.name, dataset_file.read_bytes())
                    indexed_chunks += index_document(document)
                    indexed_files += 1
                except Exception:
                    errors.append(
                        (dataset_file.name, "Indexing failed. Check model availability and try again.")
                    )
        try:
            st.session_state.documents = list_documents()
            st.session_state.library_error = False
        except Exception:
            st.session_state.library_error = True
        if indexed_files:
            st.success(f"Indexed {indexed_files} dataset file(s) · {indexed_chunks} passages")
        if errors:
            st.warning(f"{len(errors)} dataset file(s) could not be indexed.")
            for filename, message in errors:
                st.text(f"{filename}: {message}")

    if uploaded_files and st.button("Index documents", type="primary", use_container_width=True):
        indexed_files = 0
        indexed_chunks = 0
        errors: list[tuple[str, str]] = []
        seen_filenames: set[str] = set()
        with st.spinner("Parsing files, loading the local model, and indexing passages…"):
            for file in uploaded_files:
                try:
                    document = parse_document(file.name, file.getvalue())
                    normalized_name = document.filename.casefold()
                    if normalized_name in seen_filenames:
                        raise DocumentParseError("Only one file with each name can be indexed at a time.")
                    seen_filenames.add(normalized_name)
                    indexed_chunks += index_document(document)
                    indexed_files += 1
                except DocumentParseError as error:
                    errors.append((Path(file.name).name, str(error)))
                except Exception:
                    errors.append(
                        (Path(file.name).name, "Indexing failed. Check model availability and try again.")
                    )
        try:
            st.session_state.documents = list_documents()
            st.session_state.library_error = False
        except Exception:
            st.session_state.library_error = True
        if indexed_files:
            st.success(f"Indexed {indexed_files} file(s) · {indexed_chunks} passages")
        if errors:
            st.warning(f"{len(errors)} file(s) could not be indexed.")
            for filename, message in errors:
                st.text(f"{filename}: {message}")

    documents = st.session_state.documents
    chunks = sum(document["chunks"] for document in documents)
    st.markdown('<div class="side-label">Your library</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="side-meta">{len(documents)} documents &nbsp;·&nbsp; {chunks} passages</div>', unsafe_allow_html=True)
    if st.session_state.library_error:
        st.warning("The local document index could not be opened.")
    if documents:
        for document in documents:
            pages = f" · {document['pages']} pages" if document.get("pages") else ""
            st.markdown(
                f'<div class="doc-row"><div class="doc-title"><span class="file-tag">{escape(document["format"])}</span>{escape(document["title"])}</div><div class="doc-detail">{escape(document["filename"])}{pages} · {document["chunks"]} passages</div></div>',
                unsafe_allow_html=True,
            )
    else:
        st.caption("Your library is empty. Add a document to get started.")

    st.markdown('<div class="side-label">Explore a question</div>', unsafe_allow_html=True)
    sample_questions = [
        "How do I request a refund?",
        "What is the API rate limit?",
        "What is the onboarding process?",
    ]
    for number, example in enumerate(sample_questions):
        if st.button(example, key=f"sample-{number}", use_container_width=True):
            st.session_state.pending_question = example
            st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()


st.markdown('<div class="topline"><span class="status-dot"></span> DOCUMENT INTELLIGENCE <span style="opacity:.45">/</span> ASK</div>', unsafe_allow_html=True)
st.title("Find the detail\nthat moves work forward.")
st.markdown(
    '<div class="intro">Ask a question across your team’s documents. Fieldnote retrieves relevant passages locally and shows the source and similarity for each match.</div>',
    unsafe_allow_html=True,
)

if not st.session_state.chat_history:
    st.markdown('<div class="section-kicker">A few places to start</div>', unsafe_allow_html=True)
    prompts = [
        "How do I request a refund?",
        "What is the API rate limit?",
        "What is the onboarding process?",
    ]
    columns = st.columns(3)
    for column, prompt in zip(columns, prompts):
        with column:
            st.markdown(f'<div class="prompt-card">{escape(prompt)}<br><span style="color:#8b8e83;font-size:10px">Search the library ↗</span></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="empty-panel"><div class="empty-mark">F</div><div class="empty-title">A clearer path through your documents</div><div class="empty-copy">Ask below to find matching passages in your local library. Each result includes a source, an excerpt, and its similarity score.</div></div>',
        unsafe_allow_html=True,
    )


for entry in st.session_state.chat_history:
    with st.chat_message(entry["role"]):
        if entry["role"] == "user":
            st.markdown(entry["content"])
            continue

        if entry.get("error"):
            st.warning(entry["error"])
        elif not entry["passages"]:
            st.markdown(
                '<div class="answer-wrap"><div class="answer-top"><span>NO CLOSE MATCHES</span></div><div class="answer-copy">No passages were found within the similarity threshold. Try a more specific question or add another document.</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="answer-wrap"><div class="answer-top"><span>RETRIEVED EVIDENCE</span><span>{len(entry["passages"])} MATCHES</span></div><div class="answer-copy">These are the closest passages in your local library. Similarity is a retrieval score, not a guarantee that the passage answers the question.</div></div>',
                unsafe_allow_html=True,
            )
            for index, passage in enumerate(entry["passages"], 1):
                render_passage(passage, index)


pending = st.session_state.pop("pending_question", None)
question = st.chat_input("Ask something about your documents…")
active_question = pending or question
if active_question:
    st.session_state.chat_history.append({"role": "user", "content": active_question})
    try:
        with st.spinner("Searching your local library…"):
            passages = retrieve_passages(active_question)
        response = {"role": "assistant", "passages": passages}
    except Exception:
        response = {
            "role": "assistant",
            "passages": [],
            "error": "Local search could not complete. Check the model and index, then try again.",
        }
    st.session_state.chat_history.append(response)
    st.rerun()
