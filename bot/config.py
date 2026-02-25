import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


class Settings:
    TELEGRAM_BOT_TOKEN: str
    DJANGO_API_URL: str

    def __init__(self) -> None:
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError(
                "Установите TELEGRAM_BOT_TOKEN в .env или переменных окружения. "
                "Формат: TELEGRAM_BOT_TOKEN=1234567890:ABCdef..."
            )

        self.DJANGO_API_URL = os.getenv("DJANGO_API_URL", "http://localhost:8000")


settings = Settings()