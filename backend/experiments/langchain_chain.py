from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_classic.chains import RetrievalQA


def build_langchain_qa(document_id: int) -> RetrievalQA:
    """Build a LangChain RetrievalQA chain over the existing Chroma store.

    Mirrors the hand-written RAG pipeline for comparison. Not used in
    production endpoints — kept to contrast framework vs manual approach.

    Args:
        document_id: Document to restrict retrieval to.

    Returns:
        A RetrievalQA chain that answers questions with source documents.
    """
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vectorstore = Chroma(
        collection_name="document_chunks",
        embedding_function=embeddings,
        persist_directory="./chroma_db",
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 5, "filter": {"document_id": document_id}},
    )

    return RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model="gpt-4o-mini"),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )