import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application configuration loaded from environment variables."""

    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-004")

    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    SAMPLE_DOCS_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "sample_docs"
    )
    UPLOAD_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "uploads"
    )

    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))

    COLLECTION_NAME: str = "equity_documents"
    TOP_K_RESULTS: int = 5


settings = Settings()
