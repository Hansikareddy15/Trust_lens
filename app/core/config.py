"""
Application configuration for TrustLens AI.
Loads settings from environment variables and provides centralized configuration.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the repository
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env file if it exists
load_dotenv(dotenv_path=BASE_DIR / ".env")


class Settings:
    # Server Settings (default 127.0.0.1 for local security, 0.0.0.0 inside containers)
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "20"))

    # Upload & Processing Limits
    MAX_UPLOAD_SIZE_BYTES: int = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(10 * 1024 * 1024)))  # 10 MB
    MAX_PDF_PAGES: int = int(os.getenv("MAX_PDF_PAGES", "10"))
    ALLOWED_IMAGE_EXTENSIONS: set = {".png", ".jpg", ".jpeg", ".webp"}
    ALLOWED_DOCUMENT_EXTENSIONS: set = {".pdf", ".txt"}

    # Gemma 4 Model Integration Settings
    # Supports Google AI Studio endpoint for Gemma 4 (gemma-4-31b-it / gemma-4-26b-a4b-it)
    GEMMA_API_KEY: str = os.getenv("GEMMA_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")
    GEMMA_MODEL_ID: str = os.getenv("GEMMA_MODEL_ID", "gemma-4-31b-it")
    GEMMA_API_BASE: str = os.getenv("GEMMA_API_BASE", "https://generativelanguage.googleapis.com/v1beta")
    GEMMA_TIMEOUT_SECONDS: int = int(os.getenv("GEMMA_TIMEOUT_SECONDS", "45"))
    GEMMA_MAX_RETRIES: int = int(os.getenv("GEMMA_MAX_RETRIES", "1"))

    @property
    def has_gemma_key(self) -> bool:
        """Returns True if a valid-format API key is provided."""
        return bool(self.GEMMA_API_KEY and len(self.GEMMA_API_KEY.strip()) > 5)

    @property
    def sanitized_key_hint(self) -> str:
        """Safe server-side key hint for diagnostics without leaking credentials."""
        if not self.has_gemma_key:
            return "NOT_CONFIGURED"
        key = self.GEMMA_API_KEY.strip()
        return f"{key[:4]}...{key[-3:]}" if len(key) >= 8 else "CONFIGURED"


settings = Settings()
