"""
Equity AI Assistant — FastAPI Application

A RAG-powered knowledge base and chatbot for equity management,
ESOPs, cap tables, and corporate governance documents.

Built with LangChain, Google Gemini, and ChromaDB.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.rag.ingestion import ingest_sample_documents
from app.routes import chat, documents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events — runs on startup and shutdown."""
    # Startup: Ingest sample documents
    logger.info("🚀 Starting Equity AI Assistant...")
    try:
        results = ingest_sample_documents()
        for result in results:
            if result.get("status") == "success":
                logger.info(f"  ✅ Ingested: {result['doc_name']} ({result['chunk_count']} chunks)")
            elif result.get("status") == "skipped":
                logger.info(f"  ⏭️  {result.get('message', 'Skipped')}")
            else:
                logger.error(f"  ❌ Failed: {result.get('doc_name', 'Unknown')} — {result.get('error', '')}")
        logger.info("✅ Equity AI Assistant is ready!")
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        logger.info("⚠️  Starting without sample documents. Upload documents via the API.")

    yield  # App is running

    # Shutdown
    logger.info("👋 Shutting down Equity AI Assistant...")


# Create FastAPI app
app = FastAPI(
    title="Equity AI Assistant",
    description=(
        "A RAG-powered knowledge base and chatbot for equity management. "
        "Ask questions about ESOPs, cap tables, vesting schedules, and more."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(chat.router)
app.include_router(documents.router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "name": "Equity AI Assistant",
        "version": "1.0.0",
        "status": "running",
        "description": "RAG-powered equity management chatbot",
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check with system status."""
    from app.rag.ingestion import get_ingested_documents

    docs = get_ingested_documents()
    return {
        "status": "healthy",
        "documents_count": len(docs),
        "documents": [d["doc_name"] for d in docs],
    }
