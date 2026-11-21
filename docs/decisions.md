Design Decisions

The "why" behind key choices. README covers what and how; this file covers why.

FastAPI (over Flask)

Async support, auto-generated Swagger docs, and Pydantic validation from type hints. Flask would need several extra libraries for the same typed-JSON-API ergonomics.

SQLModel (over separate SQLAlchemy + Pydantic)

One class serves as both the ORM model and the validation schema, so table structure and request/response shape aren't defined twice and can't drift apart.

ChromaDB (over pgvector)

Persistent, zero-config vector store callable directly from Python, with built-in cosine + HNSW search and no separate server. pgvector would reuse the existing Postgres instance but couples vector search to the relational DB and needs manual index tuning.

Two stores: PostgreSQL + ChromaDB

Different queries: PostgreSQL for exact lookups ("get document 15"), ChromaDB for vector search ("chunks most similar to this question"). Full text stays in PostgreSQL as source of truth, so the vector store can be rebuilt anytime.

Hand-written RAG (over LangChain)

Kept the manual pipeline in production for visibility, full control over the response shape (similarity scores + chunk indices), and fewer dependencies. The LangChain version (experiments/langchain_chain.py) is a reference to show the tradeoff, not a dependency.

Chunking: semantic Max–Min by default (over sentence- and char-based)

chunk_text defaults to semantic_maxmin, an implementation of Max–Min semantic chunking (Kiss, Nagy & Szilágyi, "Max–Min semantic chunking of documents for RAG application", Discover Computing, 2025, https://doi.org/10.1007/s10791-025-09638-7). Sentences are read in order and each one joins the current chunk only if its highest similarity to the chunk's sentences reaches a threshold built from the chunk's lowest internal similarity, scaled by a sigmoid of chunk size and floored at hard_thr; a one-sentence chunk uses a fixed initial threshold, and max_sentences caps chunk length. Chunk boundaries therefore follow topic shifts instead of a fixed size, and a chunk still never cuts mid-sentence (so a negation like "is not bad" stays intact). Sentence-based and char-based strategies are kept as evaluation baselines. Parameters stay hardcoded until evaluation compares settings (YAGNI).
