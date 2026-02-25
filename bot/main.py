import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs


from bot.api_client import DjangoAPIClient
from bot.add_task import add_task_dialog
from bot.config import settings
from bot.list_tasks import router as list_tasks_router
from bot.categories import router as categories_router
from bot.handlers.start import router as start_router
from bot.handlers.add_task import router as add_task_handler_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)
api_client = DjangoAPIClient(base_url=settings.DJANGO_API_URL)


class APIClientMiddleware:
    def __init__(self, client: DjangoAPIClient):
        self.client = client

    async def __call__(self, handler, event, data: dict):
        data["api_client"] = self.client
        return await handler(event, data)


dp.message.middleware(APIClientMiddleware(api_client))
dp.callback_query.middleware(APIClientMiddleware(api_client))

dp.include_router(start_router)
dp.include_router(list_tasks_router)
dp.include_router(categories_router)
dp.include_router(add_task_handler_router)
dp.include_router(add_task_dialog)
setup_dialogs(dp)


async def main():
    bot = Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        await dp.start_polling(bot)
    finally:
        await api_client.close()


if __name__ == "__main__":
    asyncio.run(main())
