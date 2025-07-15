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
    
    parsed = urlparse(rest_url)
    host = parsed.netloc
    
    redis_url = f"rediss://:{token}@{host}:6379?ssl_cert_reqs=none&ssl_check_hostname=false"
    
    return redis_url