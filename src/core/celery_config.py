from celery import Celery

from src.core.settings import settings

celery_app = Celery(
    main="src",
    broker=f"{settings.redis_settings.redis_url}/0",
    backend=f"{settings.redis_settings.redis_url}/1")

celery_app.autodiscover_tasks(packages=["src.tasks"])
