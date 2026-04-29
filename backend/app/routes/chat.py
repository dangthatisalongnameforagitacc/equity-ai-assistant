"""
Chat API routes.

Provides endpoints for querying the RAG pipeline and managing chat sessions.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.rag.retriever import query_rag, get_conversation_history, clear_conversation_history

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Request body for chat queries."""

    question: str = Field(..., min_length=1, max_length=2000, description="The question to ask")
    session_id: Optional[str] = Field(default="default", description="Session ID for conversation memory")


class SourceInfo(BaseModel):
    """Source citation information."""

    document: str
    chunk_index: int
    relevance_snippet: str


class ChatResponse(BaseModel):
    """Response body for chat queries."""

    answer: str
    sources: list[SourceInfo]
    session_id: str


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a question to the Equity AI Assistant.

    The assistant will search through ingested documents and provide
    an answer with source citations.
    """
    try:
        result = await query_rag(
            question=request.question,
            session_id=request.session_id,
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/history/{session_id}")
async def get_history(session_id: str):
    """Get the conversation history for a session."""
    history = get_conversation_history(session_id)
    messages = []
    for msg in history:
        messages.append(
            {
                "role": "user" if isinstance(msg, dict) and msg.get("type") == "human" else
                        "user" if hasattr(msg, "type") and msg.type == "human" else "assistant",
                "content": msg.content if hasattr(msg, "content") else str(msg),
            }
        )
    return {"session_id": session_id, "messages": messages}


@router.delete("/history/{session_id}")
async def clear_history(session_id: str):
    """Clear the conversation history for a session."""
    clear_conversation_history(session_id)
    return {"status": "success", "message": f"History cleared for session {session_id}"}
