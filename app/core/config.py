from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Agent for Event Discovery"
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"

settings = Settings() 