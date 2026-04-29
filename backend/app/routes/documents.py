"""
Document management API routes.

Provides endpoints for uploading, listing, and deleting documents
from the RAG knowledge base.
"""

import os
import shutil
import uuid

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

from app.config import settings
from app.rag.ingestion import ingest_document, get_ingested_documents, delete_document

router = APIRouter(prefix="/api/documents", tags=["documents"])


class DocumentInfo(BaseModel):
    """Document information response."""

    doc_id: str
    doc_name: str
    chunk_count: int
    source_file: str


class UploadResponse(BaseModel):
    """Response for document upload."""

    doc_id: str
    doc_name: str
    chunk_count: int
    status: str


@router.get("", response_model=list[DocumentInfo])
async def list_documents():
    """List all ingested documents in the knowledge base."""
    try:
        docs = get_ingested_documents()
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and ingest a document into the knowledge base.

    Supports .txt and .pdf files.
    """
    # Validate file type
    allowed_extensions = {".txt", ".pdf"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(allowed_extensions)}",
        )

    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Save the uploaded file
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Ingest the document
        result = ingest_document(file_path, doc_name=file.filename)
        return UploadResponse(**result)

    except Exception as e:
        # Clean up the file if ingestion fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@router.delete("/{doc_id}")
async def remove_document(doc_id: str):
    """Delete a document and its chunks from the knowledge base."""
    try:
        result = delete_document(doc_id)
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")
