from .celery import app as celery_app

__all__ = ("celery_app",)
celery = celery_app  # Celery -A django_aiogram ищет атрибут 'celery'
