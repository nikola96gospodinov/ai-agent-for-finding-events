from app.core.config import settings
from urllib.parse import urlparse

def get_upstash_redis_url():
    """
    Convert Upstash REST URL to Redis URL for Celery
    Current Upstash format: REST URL + Token
    Celery needs: rediss://host:port with authentication
    """
    rest_url = settings.UPSTASH_REDIS_REST_URL
    token = settings.UPSTASH_REDIS_REST_TOKEN
    
    if not rest_url or not token:
        return "redis://localhost:6379/0"
    
    # Extract host from REST URL (e.g., https://xxx-xxx-xxx.upstash.io)
    parsed = urlparse(rest_url)
    host = parsed.netloc
    
    # Convert to Redis URL format with SSL and authentication
    # Using rediss:// for SSL connection as recommended by Upstash
    redis_url = f"rediss://:{token}@{host}:6379?ssl_cert_reqs=required"
    
    return redis_url