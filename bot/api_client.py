import aiohttp

from bot.utils.date_parser import parse_due_date


class DjangoAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """Закрывает HTTP-сессию. Вызывать при завершении работы бота."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    def _headers(self, telegram_id: int) -> dict:
        return {
            "X-Telegram-ID": str(telegram_id),
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def register_telegram_user(
        self,
        telegram_id: int,
        username: str,
        first_name: str,
        last_name: str,
    ) -> dict:
        session = await self._get_session()
        async with session.post(
            f"{self.base_url}/api/auth/telegram/",
            json={
                "telegram_id": telegram_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
            },
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"Auth failed {resp.status}: {text[:200]}")
            return await resp.json()

    async def get_tasks(self, telegram_id: int) -> list:
        session = await self._get_session()
        async with session.get(
            f"{self.base_url}/api/tasks/",
            headers=self._headers(telegram_id),
        ) as resp:
            if resp.status != 200:
                return []
            return await resp.json()

    async def update_task(self, telegram_id: int, task_id: str | int, data: dict) -> dict:
        """Обновляет задачу (например, is_completed)."""
        session = await self._get_session()
        async with session.patch(
            f"{self.base_url}/api/tasks/{task_id}/",
            headers=self._headers(telegram_id),
            json=data,
        ) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "application/json" not in content_type:
                text = await resp.text()
                raise Exception(
                    f"API returned non-JSON (status={resp.status}): {text[:300]}"
                )
            result = await resp.json()
            if resp.status >= 400:
                raise Exception(f"API error {resp.status}: {result}")
            return result

    async def delete_task(self, telegram_id: int, task_id: str | int) -> None:
        session = await self._get_session()
        async with session.delete(
            f"{self.base_url}/api/tasks/{task_id}/",
            headers=self._headers(telegram_id),
        ) as resp:
            if resp.status not in (200, 204):
                text = await resp.text()
                raise Exception(f"Delete failed {resp.status}: {text[:200]}")

    async def delete_all_tasks(self, telegram_id: int) -> int:
        """Удаляет все задачи пользователя. Возвращает количество удалённых."""
        tasks = await self.get_tasks(telegram_id)
        count = 0
        for t in tasks:
            await self.delete_task(telegram_id, t["id"])
            count += 1
        return count

    async def get_categories(self, telegram_id: int) -> list:
        session = await self._get_session()
        async with session.get(
            f"{self.base_url}/api/categories/",
            headers=self._headers(telegram_id),
        ) as resp:
            if resp.status != 200:
                return []
            return await resp.json()

    async def delete_category(self, telegram_id: int, category_id: str | int) -> None:
        session = await self._get_session()
        async with session.delete(
            f"{self.base_url}/api/categories/{category_id}/",
            headers=self._headers(telegram_id),
        ) as resp:
            if resp.status not in (200, 204):
                text = await resp.text()
                raise Exception(f"Delete failed {resp.status}: {text[:200]}")

    async def create_category(
        self, telegram_id: int, name: str, color: str = "#3498db"
    ) -> dict:
        session = await self._get_session()
        async with session.post(
            f"{self.base_url}/api/categories/",
            headers=self._headers(telegram_id),
            json={"name": name.strip(), "color": color},
        ) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "application/json" not in content_type:
                text = await resp.text()
                raise Exception(
                    f"API returned non-JSON (status={resp.status}): {text[:300]}"
                )
            result = await resp.json()
            if resp.status >= 400:
                raise Exception(f"API error {resp.status}: {result}")
            return result

    async def create_task(self, telegram_id: int, data: dict) -> dict:
        cat_id = data.get("category_id")
        payload = {
            "title": data["title"],
            "description": data.get("description", ""),
            "category": cat_id if cat_id else None,
            "due_date": parse_due_date(data.get("due_date")),
        }
        session = await self._get_session()
        async with session.post(
            f"{self.base_url}/api/tasks/",
            headers=self._headers(telegram_id),
            json=payload,
        ) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "application/json" not in content_type:
                text = await resp.text()
                raise Exception(
                    f"API returned non-JSON (status={resp.status}): {text[:300]}"
                )
            result = await resp.json()
            if resp.status >= 400:
                raise Exception(f"API error {resp.status}: {result}")
            return result
