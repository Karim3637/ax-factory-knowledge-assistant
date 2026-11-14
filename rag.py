"""
Core RAG pipeline: load documents -> chunk -> embed -> index (FAISS) -> retrieve -> generate.
"""
import os
import re
from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np
from openai import OpenAI
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")


@dataclass
class Chunk:
    text: str
    source: str
    page: int


# ---------- Loading ----------
def load_file(path: Path) -> list[Chunk]:
    """Return one 'page' Chunk per page (PDF) or per file (txt/md)."""
    pages = []
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        for i, p in enumerate(reader.pages, start=1):
            txt = (p.extract_text() or "").strip()
            if txt:
                pages.append(Chunk(txt, path.name, i))
    elif path.suffix.lower() in {".txt", ".md"}:
        pages.append(Chunk(path.read_text(encoding="utf-8"), path.name, 1))
    return pages


def chunk_text(page: Chunk, size: int = 700, overlap: int = 120) -> list[Chunk]:
    """Split by paragraphs, then pack into ~size-char chunks with overlap."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", page.text) if p.strip()]
    chunks, buf = [], ""
    for para in paras:
        if len(buf) + len(para) + 1 <= size:
            buf = f"{buf}\n{para}" if buf else para
        else:
            if buf:
                chunks.append(Chunk(buf, page.source, page.page))
            tail = buf[-overlap:] if buf else ""
            buf = f"{tail}\n{para}" if tail else para
            while len(buf) > size:  # very long paragraph
                chunks.append(Chunk(buf[:size], page.source, page.page))
                buf = buf[size - overlap:]
    if buf:
        chunks.append(Chunk(buf, page.source, page.page))
    return chunks


# ---------- Index ----------
class RAGIndex:
    def __init__(self):
        self.embedder = SentenceTransformer(EMBED_MODEL)
        self.index = None
        self.chunks: list[Chunk] = []

    def build(self, paths: list[Path]):
        self.chunks = []
        for p in paths:
            for page in load_file(p):
                self.chunks.extend(chunk_text(page))
        if not self.chunks:
            raise ValueError("No readable text found in the documents.")
        vecs = self._embed([c.text for c in self.chunks])
        self.index = faiss.IndexFlatIP(vecs.shape[1])  # cosine (vectors normalized)
        self.index.add(vecs)

    def _embed(self, texts: list[str]) -> np.ndarray:
        v = self.embedder.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(v, dtype="float32")

    def search(self, query: str, k: int = 4) -> list[tuple[Chunk, float]]:
        q = self._embed([query])
        scores, ids = self.index.search(q, min(k, len(self.chunks)))
        return [(self.chunks[i], float(s)) for i, s in zip(ids[0], scores[0]) if i != -1]


# ---------- Generation ----------
SYSTEM_PROMPT = """You are an internal assistant for factory employees.
Answer ONLY from the provided context. If the answer is not in the context, say:
"I couldn't find this in the available documents. Please contact the responsible department."
Be concise and practical. Use numbered steps for procedures.
Cite sources inline like [1], [2] matching the context numbers.
Reply in the same language as the question (English or Arabic)."""


_MODEL_CACHE: dict[str, str] = {}
# Preferred models in order (first one available on the account is used)
PREFERRED = [
    "openai/gpt-oss-120b", "llama-3.3-70b", "llama-4", "qwen", "gpt-oss",
    "gpt-4.1-mini", "gpt-4o-mini", "gpt-5-mini", "llama", "gemma", "mixtral",
]
EXCLUDE = ("whisper", "guard", "tts", "embed", "audio", "vision", "image", "moderation", "playai", "compound")


def pick_model(client: OpenAI, api_key: str) -> str:
    """Use LLM_MODEL if available, otherwise auto-pick a working chat model from the account."""
    if api_key in _MODEL_CACHE:
        return _MODEL_CACHE[api_key]
    try:
        ids = [m.id for m in client.models.list().data]
    except Exception:
        return LLM_MODEL
    chat_ids = [i for i in ids if not any(x in i.lower() for x in EXCLUDE)]
    chosen = LLM_MODEL if LLM_MODEL in ids else None
    if not chosen:
        for pref in PREFERRED:
            match = next((i for i in chat_ids if pref in i.lower()), None)
            if match:
                chosen = match
                break
    chosen = chosen or (chat_ids[0] if chat_ids else LLM_MODEL)
    _MODEL_CACHE[api_key] = chosen
    return chosen


def answer(question: str, hits: list[tuple[Chunk, float]], api_key: str) -> str:
    context = "\n\n".join(
        f"[{i}] (source: {c.source}, page {c.page})\n{c.text}" for i, (c, _) in enumerate(hits, 1)
    )
    client = OpenAI(api_key=api_key, base_url=LLM_BASE_URL)
    resp = client.chat.completions.create(
        model=pick_model(client, api_key),
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )
    return resp.choices[0].message.content