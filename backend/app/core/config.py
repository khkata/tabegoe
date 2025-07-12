from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./restaurant_recommendation.db"
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Restaurant Recommendation API"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # OpenAI API settings
    OPENAI_API_KEY: str = ""
    
    # External API settings
    GURUNAVI_API_KEY: str = ""
    GOOGLE_PLACES_API_KEY: str = ""
    
    class Config:
        env_file = ".env"


settings = Settings()

