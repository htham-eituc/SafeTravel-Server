from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Gemini AI
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"
    
    # # Database
    # database_url: str
    
    # # Firebase
    # firebase_credentials_path: str
    
    # API
    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()