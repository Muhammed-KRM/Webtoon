"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    PROJECT_NAME: str = "Webtoon AI Translator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # File Storage
    STORAGE_PATH: str = "./storage"
    CACHE_PATH: str = "./cache"
    FONTS_PATH: str = "./fonts"
    
    # OCR Settings
    OCR_LANGUAGES: List[str] = ["en"]  # Add "tr" if needed
    OCR_GPU: bool = False
    
    # Image Processing
    DEFAULT_FONT_SIZE: int = 20
    MIN_FONT_SIZE: int = 10
    MAX_FONT_SIZE: int = 40
    USE_WEBP: bool = True  # Use WebP format for better compression
    IMAGE_QUALITY: int = 90  # WebP/JPEG quality (0-100)
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        Path(self.STORAGE_PATH).mkdir(parents=True, exist_ok=True)
        Path(self.CACHE_PATH).mkdir(parents=True, exist_ok=True)
        Path(self.FONTS_PATH).mkdir(parents=True, exist_ok=True)


settings = Settings()

