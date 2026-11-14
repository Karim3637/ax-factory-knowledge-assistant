# 🏭 AX Factory Knowledge Assistant: RAG Demo for LG Electronics Egypt

An internal AI assistant that answers employees' questions from company documents
(SOPs, maintenance manuals, safety and HR policies) using **Retrieval-Augmented Generation**,
and shows the exact source behind every answer.

> Built by Karim Taha as an application demo for the **Junior Software & AI Automation Engineer** role at LG Electronics Egypt (10th of Ramadan),
> showing how GenAI can support the plant's AI Transformation (AX) by reducing time spent searching manuals.

![screenshot](screenshot.png)

## Why it matters
- Technicians get alarm-handling steps in seconds instead of searching PDFs.
- Answers are **grounded** in company documents only; if the answer isn't there, the assistant says so.
- Every answer shows its **sources** (document + page) for traceability.
- Works in **English and Arabic**.

## Architecture
```
Documents (PDF/TXT) → Chunking (paragraph-aware, overlap)
   → Embeddings (all-MiniLM-L6-v2) → FAISS vector index
Question → Embed → Top-k retrieval → LLM (Llama 3.3 via Groq) → Answer + citations
```

## Tech stack
Python · Streamlit · Sentence-Transformers · FAISS · OpenAI-compatible LLM API (Groq / OpenAI) · PyPDF

## Run locally
```bash
python -m venv venv
venv\Scripts\activate        # Windows  (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env       # then put your API key inside
streamlit run app.py
```
Add your own PDFs to `docs/` or upload them from the sidebar.

## Possible next steps
- Connect to a CMMS/ERP database (SQL) to answer live questions like "open tickets on Line 2".
- Add user feedback (👍/👎) to evaluate answer quality.
- Deploy on the company intranet with role-based access.

*Independent demo, not an official LG product. All documents in `docs/` are fictional samples.*
