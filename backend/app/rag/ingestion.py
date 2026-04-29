"""
Document ingestion module.

Handles parsing, chunking, and embedding documents into the ChromaDB vector store.
Supports text files (.txt) and PDF files (.pdf).
"""

import os
import uuid
import logging
from typing import Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_core.documents import Document

from app.config import settings

logger = logging.getLogger(__name__)


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Initialize Google Generative AI embeddings model."""
    return GoogleGenerativeAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
    )


def get_vector_store() -> Chroma:
    """Get or create the ChromaDB vector store."""
    embeddings = get_embeddings()
    return Chroma(
        collection_name=settings.COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=settings.CHROMA_PERSIST_DIR,
    )


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    """Create a text splitter with configured chunk size and overlap."""
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


def load_document(file_path: str) -> list[Document]:
    """
    Load a document from file path.

    Supports .txt and .pdf files.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {ext}. Supported: .txt, .pdf")

    return loader.load()


def ingest_document(
    file_path: str,
    doc_name: Optional[str] = None,
) -> dict:
    """
    Ingest a single document into the vector store.

    Args:
        file_path: Path to the document file.
        doc_name: Optional human-readable name for the document.

    Returns:
        Dictionary with ingestion results (doc_id, chunk_count, status).
    """
    if doc_name is None:
        doc_name = os.path.basename(file_path)

    doc_id = str(uuid.uuid4())

    logger.info(f"Ingesting document: {doc_name} (ID: {doc_id})")

    # Load the document
    raw_docs = load_document(file_path)
    logger.info(f"Loaded {len(raw_docs)} page(s) from {doc_name}")

    # Split into chunks
    splitter = get_text_splitter()
    chunks = splitter.split_documents(raw_docs)
    logger.info(f"Split into {len(chunks)} chunks")

    # Add metadata to each chunk
    for i, chunk in enumerate(chunks):
        chunk.metadata.update(
            {
                "doc_id": doc_id,
                "doc_name": doc_name,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "source_file": file_path,
            }
        )

    # Store in vector store
    vector_store = get_vector_store()
    vector_store.add_documents(chunks)

    logger.info(f"Successfully ingested {doc_name} ({len(chunks)} chunks)")

    return {
        "doc_id": doc_id,
        "doc_name": doc_name,
        "chunk_count": len(chunks),
        "status": "success",
    }


def ingest_sample_documents() -> list[dict]:
    """
    Ingest all sample documents from the sample_docs directory.

    Returns:
        List of ingestion results for each document.
    """
    sample_dir = settings.SAMPLE_DOCS_DIR
    results = []

    if not os.path.exists(sample_dir):
        logger.warning(f"Sample docs directory not found: {sample_dir}")
        return results

    # Check if documents are already ingested
    vector_store = get_vector_store()
    existing = vector_store.get()
    if existing and len(existing.get("ids", [])) > 0:
        logger.info("Documents already ingested, skipping sample ingestion.")
        return [{"status": "skipped", "message": "Documents already exist"}]

    for filename in sorted(os.listdir(sample_dir)):
        file_path = os.path.join(sample_dir, filename)
        if os.path.isfile(file_path):
            try:
                result = ingest_document(file_path, doc_name=filename)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to ingest {filename}: {e}")
                results.append(
                    {
                        "doc_name": filename,
                        "status": "error",
                        "error": str(e),
                    }
                )

    return results


def get_ingested_documents() -> list[dict]:
    """
    Get a list of all ingested documents with their metadata.

    Returns:
        List of document info dicts.
    """
    vector_store = get_vector_store()
    all_data = vector_store.get()

    if not all_data or not all_data.get("metadatas"):
        return []

    # Deduplicate by doc_id
    docs_map = {}
    for meta in all_data["metadatas"]:
        doc_id = meta.get("doc_id", "unknown")
        if doc_id not in docs_map:
            docs_map[doc_id] = {
                "doc_id": doc_id,
                "doc_name": meta.get("doc_name", "Unknown"),
                "chunk_count": meta.get("total_chunks", 0),
                "source_file": meta.get("source_file", ""),
            }

    return list(docs_map.values())


def delete_document(doc_id: str) -> dict:
    """
    Delete a document and all its chunks from the vector store.

    Args:
        doc_id: The unique document ID.

    Returns:
        Deletion result dict.
    """
    vector_store = get_vector_store()
    all_data = vector_store.get(where={"doc_id": doc_id})

    if not all_data or not all_data.get("ids"):
        return {"status": "error", "message": f"Document {doc_id} not found"}

    vector_store.delete(ids=all_data["ids"])
    logger.info(f"Deleted document {doc_id} ({len(all_data['ids'])} chunks)")

    return {
        "status": "success",
        "doc_id": doc_id,
        "chunks_deleted": len(all_data["ids"]),
    }
