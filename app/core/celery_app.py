from celery import Celery
from app.core.config import settings

# celery -A app.core.celery_app worker --loglevel=info

celery_app = Celery(
    'ai_agents',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

celery_app.autodiscover_tasks(['app.services.agent'])