from celery import Celery

app = Celery("django_aiogram")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "check-due-tasks": {
        "task": "tasks_app.tasks.check_due_tasks",
        "schedule": 28800.0,  # каждые 8 часов
    },
}
