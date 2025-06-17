import redis

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=1,  # Using db 1 to separate from Celery's db 0
    decode_responses=True  # Automatically decode responses to strings
)