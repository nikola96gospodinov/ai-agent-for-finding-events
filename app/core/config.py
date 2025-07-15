from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Agent for Event Discovery"
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    
    # LLM/OpenAI
    GEMINI_API_KEY: str = ""
    
    # Email (Mailgun)
    MAILGUN_API_KEY: str = ""
    MAILGUN_DOMAIN: str = ""
    
    # Upstash Redis
    UPSTASH_REDIS_REST_URL: str = ""
    UPSTASH_REDIS_REST_TOKEN: str = ""
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"

settings = Settings() 