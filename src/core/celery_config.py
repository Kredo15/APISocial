from celery import Celery

from src.core.settings import settings

celery_app = Celery(
    main="src",
    broker=f"{settings.redis_settings.redis_url}/0",
    backend=f"{settings.redis_settings.redis_url}/1",
    include=["src.tasks.confirmation_email"]
)

celery_app.conf.update(
    timezone="Europe/Moscow",  # Часовой пояс
    enable_utc=True,  # Использовать UTC для внутренних операций

    # Настройки отслеживания
    task_track_started=True,  # Отслеживать начало выполнения задач
    task_ignore_result=False,  # Сохранять результаты задач

    # Настройки таймаутов
    task_time_limit=30 * 60,  # Максимальное время выполнения задачи (30 минут)

    # Настройки воркера
    worker_prefetch_multiplier=1,  # Количество задач, которые воркер берёт одновременно
    worker_max_tasks_per_child=1000,  # Максимальное количество задач на дочерний процесс

    # Настройки очередей
    task_default_queue="default",  # Очередь по умолчанию
    task_acks_late=True,  # Подтверждать выполнение задачи только после успешного завершения
    worker_disable_rate_limits=False,  # Не отключать ограничения скорости

    # Настройки логирования
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s",
)
