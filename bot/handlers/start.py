from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.api_client import DjangoAPIClient
from bot.keyboards import get_main_menu

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, api_client: DjangoAPIClient):
    await api_client.register_telegram_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username or "",
        first_name=message.from_user.first_name or "",
        last_name=message.from_user.last_name or "",
    )
    await message.answer(
        "Привет! Используй меню для работы с задачами.",
        reply_markup=get_main_menu(),
    )
