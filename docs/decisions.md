# Design Decisions

The "why" behind key choices. README covers what and how; this file covers why.

## FastAPI (over Flask)
Async support, auto-generated Swagger docs, and Pydantic validation from type
hints. Flask would need several extra libraries for the same typed-JSON-API
ergonomics.

## SQLModel (over separate SQLAlchemy + Pydantic)
One class serves as both the ORM model and the validation schema, so table
structure and request/response shape aren't defined twice and can't drift apart.

## ChromaDB (over pgvector)
Persistent, zero-config vector store callable directly from Python, with built-in
cosine + HNSW search and no separate server. pgvector would reuse the existing
Postgres instance but couples vector search to the relational DB and needs manual
index tuning.

## Two stores: PostgreSQL + ChromaDB
Different queries: PostgreSQL for exact lookups ("get document 15"), ChromaDB for
vector search ("chunks most similar to this question"). Full text stays in
PostgreSQL as source of truth, so the vector store can be rebuilt anytime.

## Hand-written RAG (over LangChain)
Kept the manual pipeline in production for visibility, full control over the
response shape (similarity scores + chunk indices), and fewer dependencies. The
LangChain version (`experiments/langchain_chain.py`) is a reference to show the
tradeoff, not a dependency.

## Chunking: sentence by default
`chunk_text` dispatches over two strategies. Sentence-based is default: it never
cuts mid-sentence, so a chunk can't lose a critical word (e.g. a negation like
"is *not* bad"), which reduces synthesis errors. Char-based gives uniform,
token-predictable chunks and is kept as an evaluation baseline. Parameters stay
hardcoded until evaluation compares settings (YAGNI).