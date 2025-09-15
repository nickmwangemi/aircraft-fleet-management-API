from celery import Celery
from app.config import settings

celery_app = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.api.tasks.report_tasks"],
)

celery_app.conf.update(
    task_track_started=True,
)
