"""
Configuration management for ORCA Backend
Loads environment variables and application settings
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "ORCA Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))

    # API Keys for external services
    INCOIS_API_KEY: Optional[str] = os.getenv("INCOIS_API_KEY")
    IMD_API_KEY: Optional[str] = os.getenv("IMD_API_KEY")
    ISRO_BHUVAN_API_KEY: Optional[str] = os.getenv("ISRO_BHUVAN_API_KEY")

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/orca")
    MONGODB_URL: Optional[str] = os.getenv("MONGODB_URL")

    # Vector store settings
    VECTOR_STORE_TYPE: str = os.getenv("VECTOR_STORE_TYPE", "faiss")  # faiss or pgvector
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    # LLM settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")  # openai, anthropic, local, groq
    LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    
    # Risk thresholds file path
    THRESHOLDS_FILE: str = os.getenv("THRESHOLDS_FILE", "app/rules/thresholds.yaml")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

# Global settings instance
settings = Settings()