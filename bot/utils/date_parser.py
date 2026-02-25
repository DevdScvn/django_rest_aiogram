"""Утилиты для парсинга дат."""


def parse_due_date(value: str | None) -> str | None:
    """Преобразует DD.MM.YYYY в YYYY-MM-DD для Django."""
    if not value or not isinstance(value, str):
        return None
    value = value.strip()
    if not value:
        return None
    parts = value.replace(".", " ").replace("-", " ").replace("/", " ").split()
    if len(parts) == 3:
        try:
            d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
            if 1 <= d <= 31 and 1 <= m <= 12 and 1900 <= y <= 2100:
                return f"{y:04d}-{m:02d}-{d:02d}"
        except (ValueError, IndexError):
            pass
    return None


def plural_tasks(n: int) -> str:
    """Склонение слова 'задача' для числа n."""
    if n % 10 == 1 and n % 100 != 11:
        return "задачу"
    if 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        return "задачи"
    return "задач"
