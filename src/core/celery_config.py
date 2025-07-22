from celery import Celery

from src.core.settings import settings

celery_app = Celery(main="scr", broker=settings.redis_settings.redis_url, backend=settings.redis_settings.redis_url)

celery_app.autodiscover_tasks(packages=["scr.apps"])