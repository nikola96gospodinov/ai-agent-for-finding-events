from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Agent for Event Discovery"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 