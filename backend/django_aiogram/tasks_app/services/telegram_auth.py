"""Сервис регистрации и привязки пользователей по Telegram."""
from django.contrib.auth.models import User

from ..models import TelegramUser


def register_or_link_telegram_user(
    telegram_id: int,
    *,
    username: str = "",
    first_name: str = "",
    last_name: str = "",
) -> tuple[TelegramUser, bool]:
    """
    Зарегистрировать или привязать пользователя по telegram_id.

    Returns:
        Кортеж (TelegramUser, created: bool)
    """
    user, _ = User.objects.get_or_create(
        username=f"tg_{telegram_id}",
        defaults={"first_name": first_name or str(telegram_id)},
    )
    tg_user, created = TelegramUser.objects.update_or_create(
        telegram_id=telegram_id,
        defaults={
            "user": user,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
        },
    )
    return tg_user, created
