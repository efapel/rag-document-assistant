# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

AcademiQ is a FastAPI backend for RAG over academic PDFs: a user uploads a PDF, then asks questions answered only from retrieved chunks of that document, with the source chunks and similarity scores returned. All code lives in `backend/`; design rationale is in `docs/decisions.md`. It is a small learning project — prefer simple, readable solutions over extra abstraction layers.

## Commands

Run everything from `backend/` — the ChromaDB path (`./chroma_db`) and `app.*` imports are relative to it. The virtualenv lives at the repo root (`../venv`).

```bash
pip install -r requirements.txt                   # app dependencies (direct deps only, pinned)
pip install -r experiments/requirements.txt       # + LangChain, only for experiments/
uvicorn app.main:app --reload                     # API at http://localhost:8000, Swagger at /docs
```

There is no test suite, linter, or formatter configured yet. Verify changes manually through `/docs` (register → login → use the bearer token), or with `fastapi.testclient.TestClient` for endpoints that don't hit OpenAI.

Config comes from `backend/.env` (template: `backend/.env.example`): `DATABASE_URL` (PostgreSQL/Supabase), `OPENAI_API_KEY`, `JWT_SECRET_KEY`. `load_dotenv()` is currently called per module (`core/database.py`, `auth/security.py`, `rag/client.py`); there is no central settings object yet.

## Layout (domain-based)

```
backend/app/
  main.py            FastAPI app, startup hook, router registration
  core/              cross-cutting: database.py (engine, get_session, create_tables), types.py (shared Annotated field types)
  auth/              User model, register/login router, security.py (bcrypt + JWT), dependencies.py (get_current_user)
  documents/         Document model, create/upload/list/get/delete router
  conversations/     Conversation model, POST /ask router
  rag/               FastAPI-independent RAG engine: client.py (OpenAI client), embeddings.py, chunking.py, vector_store.py, llm.py
backend/experiments/ LangChain comparison script, not used by the app
```

Each domain owns its `models.py` (SQLModel tables), `schemas.py` (Pydantic request/response), and `router.py`. Domains may import each other's models (`documents` uses `conversations.models.Conversation` on delete; `conversations` uses `documents.models.Document`). `rag/` must not import from FastAPI or domain packages. When adding a new table, also import its models module in `core/database.create_tables()` so `create_all` registers it.

Business logic still lives in the routers (PDF extraction, indexing rollback, conversation history); moving it into per-domain `service.py` modules is a planned next step.

## Architecture

**Two stores, kept in sync by the routers.** PostgreSQL holds `User`, `Document` (full text, source of truth) and `Conversation` (Q&A history). ChromaDB (`rag/vector_store.py`, single collection `document_chunks`, cosine/HNSW) holds chunk embeddings with metadata `{document_id, chunk_index}` and ids `"{document_id}_{i}"`. Tables are created via `create_all` on startup — there are no migrations. Any code that creates or deletes a document must update both stores: upload rolls back the Postgres row if indexing fails (raw-text `create_document` does not); delete removes conversations, then Chroma chunks, then the document.

**Request flow:**
- Upload: PDF → PyMuPDF (`fitz`) text extraction → `rag.chunking.chunk_text` → `rag.vector_store.add_document_chunks` (embeds each chunk via `rag.embeddings.embed_text`).
- Ask (`POST /ask`): ownership check → `vector_store.query_similar_chunks` (top 5, filtered by `document_id`; similarity = `1 - cosine distance`) → last 3 `Conversation` turns for this user+document replayed as chat history → `rag.llm.answer_question_with_context` (gpt-4o-mini) → turn persisted as a new `Conversation`.

**Chunking (`rag/chunking.py`).** `chunk_text(text, strategy)` dispatches between `"semantic_maxmin"` (current default), `"sentence"` (10 sentences, overlap 1) and `"char"` (500 chars, overlap 50, kept as an evaluation baseline). All sentence-based strategies go through `_split_into_sentences`, which also cleans PDF artifacts (de-hyphenation, paragraph breaks → sentence ends). Semantic max-min embeds every sentence (`embed_texts`, batched 100/call) and grows a chunk while the candidate's max similarity to the chunk exceeds a dynamic threshold derived from the chunk's min internal similarity, capped at 15 sentences. Parameters are intentionally hardcoded until evaluation compares settings. `docs/decisions.md` still describes sentence chunking as the default.

**Auth.** bcrypt password hashing, HS256 JWT (`sub` = user id, 60 min expiry), `OAuth2PasswordBearer` with `tokenUrl="/login"` (login takes form data with `username` = email). Every document/ask endpoint depends on `auth.dependencies.get_current_user` and returns 404 (not 403) for documents owned by another user.

**OpenAI usage** goes through the shared client in `rag/client.py` (`gpt-4o-mini` for answers, `text-embedding-3-small` for embeddings). The hand-written RAG pipeline is deliberate; `experiments/langchain_chain.py` is a reference only.
