"""Отправка сообщений в Telegram."""
import asyncio

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from django.conf import settings


async def send_telegram_message(chat_id: int, text: str) -> None:
    """Отправить сообщение пользователю в Telegram."""
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not configured")

    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        await bot.send_message(chat_id=chat_id, text=text)
    finally:
        await bot.session.close()


def send_telegram_message_sync(chat_id: int, text: str) -> None:
    """Синхронная обёртка для использования в Celery."""
    asyncio.run(send_telegram_message(chat_id, text))
