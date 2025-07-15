from celery import Celery
from app.core.upstash_connection_link import get_upstash_redis_url

celery_app = Celery(
    'ai_agents',
    broker=get_upstash_redis_url(),
    backend=get_upstash_redis_url(),
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

celery_app.autodiscover_tasks(['app.services.agent'])