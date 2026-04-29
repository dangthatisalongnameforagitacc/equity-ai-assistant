"""
RAG retriever module.

Handles question answering using LangChain's retrieval chain with
Google Gemini LLM and ChromaDB vector store. Provides source-grounded
citations with every answer.
"""

import logging
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from app.config import settings
from app.rag.ingestion import get_vector_store

logger = logging.getLogger(__name__)

# System prompt for the equity AI assistant
SYSTEM_PROMPT = """You are an AI-powered Equity Management Assistant for a company. 
Your role is to help employees, founders, and investors understand equity-related 
topics including ESOPs, cap tables, vesting schedules, board resolutions, and 
share-related policies.

IMPORTANT INSTRUCTIONS:
1. Answer ONLY based on the provided context documents. Do not make up information.
2. If the context doesn't contain enough information to answer, say so clearly.
3. Always cite your sources by mentioning the document name where you found the information.
4. Format your answers clearly with bullet points or numbered lists when appropriate.
5. When discussing numbers (shares, percentages, valuations), be precise and quote exact figures from the documents.
6. If a question is ambiguous, provide the most relevant interpretation based on the context.

CONTEXT FROM DOCUMENTS:
{context}
"""

# Conversation memory store (in-memory for simplicity)
_conversation_histories: dict[str, list] = {}


def get_llm() -> ChatGoogleGenerativeAI:
    """Initialize the Google Gemini LLM."""
    return ChatGoogleGenerativeAI(
        model=settings.MODEL_NAME,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.3,
        convert_system_message_to_human=True,
    )


def format_docs(docs) -> str:
    """Format retrieved documents into a single context string with source info."""
    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("doc_name", "Unknown")
        chunk_idx = doc.metadata.get("chunk_index", "?")
        total = doc.metadata.get("total_chunks", "?")
        formatted.append(
            f"[Source: {source} | Section {chunk_idx + 1}/{total}]\n{doc.page_content}"
        )
    return "\n\n---\n\n".join(formatted)


def extract_sources(docs) -> list[dict]:
    """Extract source citation information from retrieved documents."""
    sources = []
    seen = set()

    for doc in docs:
        doc_name = doc.metadata.get("doc_name", "Unknown")
        if doc_name not in seen:
            seen.add(doc_name)
            sources.append(
                {
                    "document": doc_name,
                    "chunk_index": doc.metadata.get("chunk_index", 0),
                    "relevance_snippet": doc.page_content[:200] + "..."
                    if len(doc.page_content) > 200
                    else doc.page_content,
                }
            )

    return sources


def get_conversation_history(session_id: str) -> list:
    """Retrieve conversation history for a session."""
    return _conversation_histories.get(session_id, [])


def clear_conversation_history(session_id: str) -> None:
    """Clear conversation history for a session."""
    _conversation_histories.pop(session_id, None)


async def query_rag(
    question: str,
    session_id: Optional[str] = "default",
) -> dict:
    """
    Query the RAG pipeline with a question.

    Args:
        question: The user's question.
        session_id: Session ID for conversation memory.

    Returns:
        Dictionary with answer, sources, and session info.
    """
    logger.info(f"Processing query: {question[:100]}...")

    # Get vector store and create retriever
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": settings.TOP_K_RESULTS},
    )

    # Retrieve relevant documents
    retrieved_docs = retriever.invoke(question)
    logger.info(f"Retrieved {len(retrieved_docs)} relevant chunks")

    if not retrieved_docs:
        return {
            "answer": "I couldn't find any relevant information in the documents to answer your question. "
            "Please try rephrasing your question or make sure relevant documents have been uploaded.",
            "sources": [],
            "session_id": session_id,
        }

    # Format context from retrieved docs
    context = format_docs(retrieved_docs)
    sources = extract_sources(retrieved_docs)

    # Build conversation history
    history = get_conversation_history(session_id)

    # Create the prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ]
    )

    # Create and run the chain (with retry for rate limits)
    import asyncio

    llm = get_llm()
    chain = prompt | llm | StrOutputParser()

    answer = None
    for attempt in range(3):
        try:
            answer = await chain.ainvoke(
                {
                    "context": context,
                    "history": history,
                    "question": question,
                }
            )
            break
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                wait = (attempt + 1) * 10
                logger.warning(f"Rate limited, retrying in {wait}s (attempt {attempt + 1}/3)")
                await asyncio.sleep(wait)
            else:
                raise

    # Update conversation history
    if session_id not in _conversation_histories:
        _conversation_histories[session_id] = []

    _conversation_histories[session_id].extend(
        [
            HumanMessage(content=question),
            AIMessage(content=answer),
        ]
    )

    # Keep only last 10 messages to prevent context overflow
    if len(_conversation_histories[session_id]) > 20:
        _conversation_histories[session_id] = _conversation_histories[session_id][-20:]

    logger.info("Query processed successfully")

    return {
        "answer": answer,
        "sources": sources,
        "session_id": session_id,
    }
