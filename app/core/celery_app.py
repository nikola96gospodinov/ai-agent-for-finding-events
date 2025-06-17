from celery import Celery

# celery -A app.core.celery_app worker --loglevel=info

celery_app = Celery(
    'ai_agents',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

celery_app.autodiscover_tasks(['app.services.agent'])