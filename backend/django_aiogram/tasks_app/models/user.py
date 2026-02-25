from django.contrib.auth.models import User
from django.db import models

from ..utils.id_generator import generate_id


def telegram_user_id_default():
    return generate_id("telegram_user")


class TelegramUser(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=20,
        editable=False,
        default=telegram_user_id_default,
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="telegram_user")
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    username = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Telegram пользователь"
        verbose_name_plural = "Telegram пользователи"

    def __str__(self):
        return f"{self.user.username} ({self.telegram_id})"
