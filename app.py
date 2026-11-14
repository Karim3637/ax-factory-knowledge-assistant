"""
AX Factory Knowledge Assistant - RAG demo prepared for LG Electronics Egypt (10th of Ramadan)
Run:  streamlit run app.py
"""
import os
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()
from rag import RAGIndex, answer  # noqa: E402

DOCS_DIR = Path(__file__).parent / "docs"
SUPPORTED = {".pdf", ".txt", ".md"}
CANDIDATE = "Karim Taha"
ROLE = "Junior Software & AI Automation Engineer"

st.set_page_config(page_title="AX Factory Assistant | Demo for LG Electronics Egypt", page_icon="🏭", layout="wide")

st.markdown(
    """
    <style>
    .hero {background: linear-gradient(90deg,#A50034 0%,#6b0022 100%); color:#fff;
           padding:22px 28px; border-radius:14px; margin-bottom:14px;}
    .hero h1 {color:#fff; margin:0; font-size:2rem;}
    .hero p {color:#f3d9e1; margin:6px 0 0 0;}
    .tag {display:inline-block; background:rgba(255,255,255,.15); padding:3px 10px;
          border-radius:20px; font-size:.8rem; margin-right:6px; margin-top:10px;}
    .card {border:1px solid #eee; border-left:4px solid #A50034; border-radius:10px;
           padding:12px 14px; height:100%;}
    .card b {color:#A50034;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Indexing documents...")
def get_index(file_keys: tuple[str, ...]) -> RAGIndex:
    idx = RAGIndex()
    idx.build([Path(k) for k in file_keys])
    return idx


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown(f"### 👋 Prepared by {CANDIDATE}")
    st.caption(f"Candidate for **{ROLE}**\nLG Electronics Egypt — 10th of Ramadan")
    st.divider()

    st.header("⚙️ Settings")
    api_key = st.text_input(
        "LLM API key (Groq / OpenAI)", value=os.getenv("LLM_API_KEY", ""), type="password"
    )
    top_k = st.slider("Chunks to retrieve", 2, 8, 4)

    st.header("📄 Knowledge base")
    uploads = st.file_uploader("Add your own PDFs / TXT", type=["pdf", "txt", "md"], accept_multiple_files=True)

    files = sorted(str(p) for p in DOCS_DIR.iterdir() if p.suffix.lower() in SUPPORTED)
    if uploads:
        tmp = Path(tempfile.gettempdir()) / "rag_uploads"
        tmp.mkdir(exist_ok=True)
        for u in uploads:
            dest = tmp / u.name
            dest.write_bytes(u.getbuffer())
            files.append(str(dest))

    for f in files:
        st.caption(f"• {Path(f).name}")

    st.divider()
    st.caption(
        "Independent demo built for a job application. Not an official LG product. "
        "All documents are fictional samples."
    )

# ---------- Header ----------
st.markdown(
    f"""
    <div class="hero">
      <h1>🏭 AX Factory Knowledge Assistant</h1>
      <p>A GenAI concept to support LG Electronics Egypt's <b>AI Transformation (AX)</b> journey
      at the 10th of Ramadan plant: instant, sourced answers from SOPs, maintenance manuals,
      quality and HR policies.</p>
      <span class="tag">RAG</span><span class="tag">Python</span><span class="tag">FAISS</span>
      <span class="tag">LLM</span><span class="tag">Streamlit</span><span class="tag">EN / AR</span>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("💡 Why this fits the AX initiative and how it could scale", expanded=False):
    c1, c2, c3 = st.columns(3)
    c1.markdown(
        '<div class="card"><b>Reduce manual work</b><br>Technicians and operators get alarm-handling '
        "steps and procedures in seconds instead of searching binders or calling other departments.</div>",
        unsafe_allow_html=True,
    )
    c2.markdown(
        '<div class="card"><b>Integrate with existing systems</b><br>Next step: connect to CMMS / ERP '
        "via SQL &amp; APIs, e.g. “open tickets on Line 2” or “spare parts stock for heater bands”.</div>",
        unsafe_allow_html=True,
    )
    c3.markdown(
        '<div class="card"><b>Safe &amp; traceable</b><br>Answers come only from approved documents, '
        "with sources shown. If the answer isn't documented, the assistant says so.</div>",
        unsafe_allow_html=True,
    )

if not files:
    st.warning("Add documents to the `docs/` folder or upload them from the sidebar.")
    st.stop()

index = get_index(tuple(files))

# ---------- Example questions ----------
st.markdown("##### Try a question")
examples = [
    "Injection molding machine shows alarm E-104. What should I do?",
    "What is the end-of-line test procedure for washing machines?",
    "What PPE is required in the welding area?",
    "ما هي خطوات الإغلاق والتأمين (LOTO) قبل الصيانة؟",
]
cols = st.columns(len(examples))
for col, ex in zip(cols, examples):
    if col.button(ex, use_container_width=True):
        st.session_state["q"] = ex

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("Ask about procedures, alarms, safety, quality or HR...") or st.session_state.pop("q", None)

if question:
    st.session_state.history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        if not api_key:
            st.error("Add your API key in the sidebar (free key: console.groq.com).")
            st.stop()
        hits = index.search(question, k=top_k)
        with st.spinner("Searching documents..."):
            reply = answer(question, hits, api_key)
        st.markdown(reply)
        with st.expander("📚 Sources"):
            for i, (c, score) in enumerate(hits, 1):
                st.markdown(f"**[{i}] {c.source} — page {c.page}** · relevance `{score:.2f}`")
                st.caption(c.text[:400] + ("..." if len(c.text) > 400 else ""))
    st.session_state.history.append({"role": "assistant", "content": reply})
