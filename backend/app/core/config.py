# backend/app/core/config.py
import os
from pydantic_settings import BaseSettings
from typing import List, Union

class Settings(BaseSettings):
    PROJECT_NAME: str = "AfyaPlate KE API"
    API_V1_STR: str = "/api/v1"

    # Backend CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]

    # LLM Provider Settings (Groq as default)
    LLM_API_KEY: str = "YOUR_LLM_API_KEY"
    LLM_BASE_URL: str = "https://api.groq.com/openai/v1"
    LLM_MODEL: str = "llama3-8b-8192" # Or other models like mixtral-8x7b-32768

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
