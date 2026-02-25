from rest_framework import authentication, exceptions

from .models import TelegramUser


class TelegramAuthentication(authentication.BaseAuthentication):
    """Аутентификация по заголовку X-Telegram-ID."""

    def authenticate(self, request):
        telegram_id = request.headers.get("X-Telegram-ID") or request.data.get("telegram_id")
        if not telegram_id:
            return None

        try:
            telegram_id = int(telegram_id)
        except (ValueError, TypeError):
            raise exceptions.AuthenticationFailed("Invalid telegram_id")

        try:
            tg_user = TelegramUser.objects.select_related("user").get(telegram_id=telegram_id)
            return (tg_user.user, tg_user)
        except TelegramUser.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                "User not found. Send /start to the bot first."
            )
