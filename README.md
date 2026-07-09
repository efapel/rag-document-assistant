# AcademiQ

A self-hosted RAG system for asking questions about academic PDFs. Upload a
document, ask a question, and get an answer grounded only in that document —
with the exact source passages the answer is based on.

## How it works

Upload:  PDF → extract text → split into chunks → embed → store in ChromaDB
Ask:     question → embed → retrieve most similar chunks → send to LLM → answer + sources

The LLM never sees the whole document. It only sees the chunks most relevant to
the question, retrieved by semantic similarity. This keeps token cost low and
grounds answers in specific passages rather than the full text.

## Features

- PDF upload with automatic text extraction (PyMuPDF)
- Sentence-based chunking (keeps chunks on sentence boundaries)
- Semantic retrieval over ChromaDB using cosine similarity
- Answers cite their source chunks, each with a similarity score
- Full document text stored in PostgreSQL; chunk embeddings in ChromaDB

## Tech stack

- **API:** FastAPI, Pydantic
- **Database:** PostgreSQL (via Supabase), SQLModel ORM
- **Vector store:** ChromaDB (persistent, cosine similarity)
- **PDF parsing:** PyMuPDF
- **LLM & embeddings:** OpenAI (gpt-4o-mini, text-embedding-3-small)

## Setup

Requires Python 3.13+, a PostgreSQL database, and an OpenAI API key.

```bash
# 1. Clone and enter the backend
cd academiq/backend

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# then edit .env with your DATABASE_URL and OPENAI_API_KEY

# 5. Run the server
uvicorn app.main:app --reload
```

The API is now at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/health` | Health check |
| POST   | `/documents/upload` | Upload a PDF; extracts, chunks, and embeds it |
| POST   | `/documents` | Create a document from raw text |
| GET    | `/documents` | List all documents |
| GET    | `/documents/{id}` | Get one document |
| DELETE | `/documents/{id}` | Delete a document and its chunks |
| POST   | `/ask` | Ask a question about a document |

Full request/response schemas are available in the interactive docs at `/docs`.

### Example: asking a question

```json
POST /ask
{
    "question": "How does drift velocity change if wire diameter doubles?",
    "document_id": 15
}
```

Response:

```json
{
    "answer": "If the diameter doubles while current stays constant, drift velocity is halved...",
    "document_id": 15,
    "document_title": "physics.pdf",
    "source_chunks": [
        {"text": "...", "chunk_index": 39, "similarity_score": 0.61}
    ]
}
```

## Design decisions

Key architectural choices (why ChromaDB, why hand-written RAG over LangChain,
chunking strategy) are documented in [docs/decisions.md](docs/decisions.md).