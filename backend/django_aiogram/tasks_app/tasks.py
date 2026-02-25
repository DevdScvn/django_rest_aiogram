from datetime import timedelta

from celery import shared_task
from django.utils import timezone


@shared_task
def check_due_tasks():
    from .models import Task, TelegramUser

    now = timezone.now()
    window_end = now + timedelta(hours=24)

    tasks = Task.objects.filter(
        due_date__gte=now,
        due_date__lte=window_end,
        is_completed=False,
    ).select_related("user__telegram_user")

    for task in tasks:
        try:
            telegram_id = task.user.telegram_user.telegram_id
        except TelegramUser.DoesNotExist:
            continue
        send_telegram_notification.delay(
            telegram_id,
            task.title,
            task.due_date.strftime("%Y-%m-%d"),
        )


@shared_task
def send_telegram_notification(telegram_id: int, title: str, due_date_str: str):
    """Отправка уведомления в Telegram."""
    from .notifications.telegram import send_telegram_message_sync

    text = f"⏰ Напоминание: задача «{title}» должна быть выполнена до {due_date_str}"
    send_telegram_message_sync(telegram_id, text)
