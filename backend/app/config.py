import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = "HealthSutra"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000"
    ]

    # LLM Settings (Groq)
    GROQ_API_KEY: str = Field(default="", validation_alias="GROQ_API_KEY")
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Embedding & FAISS Settings
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    FAISS_INDEX_PATH: str = "data/vector_store/healthsutra_faiss.index"
    CHUNKS_METADATA_PATH: str = "data/vector_store/healthsutra_chunks.json"
    DOCUMENT_REGISTRY_PATH: str = "data/processed/document_registry.json"
    
    # Grounding & Retrieval Thresholds
    RELEVANCE_THRESHOLD: float = 0.50
    TOP_K_CHUNKS: int = 5

    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./data/healthsutra.db",
        validation_alias="DATABASE_URL"
    )

    # Security
    ADMIN_API_KEY: str = "healthsutra_admin_secret_key"
    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
