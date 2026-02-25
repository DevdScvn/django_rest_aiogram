# Django + Aiogram ToDo List

Telegram-бот для управления задачами с Django REST API в качестве бэкенда.

## Возможности

- **Задачи** — создание, просмотр, отметка выполненными, удаление
- **Категории** — создание и удаление категорий для группировки задач
- **Уведомления** — Celery проверяет просроченные задачи каждые 8 часов

## Требования

- Python 3.12+
- Redis (для Celery)

## Установка

1. Клонируйте репозиторий и перейдите в каталог проекта.

2. Установите зависимости:

```bash
pip install -e .
```

3. Создайте файл `.env` в корне проекта (можно скопировать `.env.example`):

```env
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
DJANGO_API_URL=http://localhost:8000
```

4. Примените миграции Django:

```bash
cd backend/django_aiogram
python manage.py migrate
```

## Запуск

Запустите все компоненты в отдельных терминалах:

**1. Django-сервер**

```bash
cd backend/django_aiogram
python manage.py runserver
```

**2. Celery worker и beat** (для уведомлений о просроченных задачах)

```bash
cd backend/django_aiogram
celery -A django_aiogram worker -l info
celery -A django_aiogram beat -l info
```

**3. Telegram-бот**

```bash
python -m bot.main
```

> Запуск бота выполняется из корня проекта, где находится модуль `bot`.

## Использование бота

1. Найдите бота в Telegram и отправьте `/start`
2. Меню:
   - **📋 Мои задачи** — список задач, удаление, отметка выполненными
   - **➕ Добавить задачу** — диалог создания задачи (название, описание, категория, срок)
   - **📁 Мои категории** — управление категориями

## API

REST API доступен по адресу `http://localhost:8000/api/`:

- `GET/POST /api/tasks/` — список и создание задач
- `GET/PUT/DELETE /api/tasks/{id}/` — одна задача
- `GET/POST /api/categories/` — категории
- `POST /api/auth/telegram/` — регистрация пользователя по Telegram ID

## Структура проекта

```
django_aiogram/
├── bot/                 # Telegram-бот (aiogram)
│   ├── main.py          # Точка входа
│   ├── add_task.py      # Диалог добавления задачи
│   ├── list_tasks.py    # Список и управление задачами
│   ├── categories.py    # Категории
│   └── api_client.py    # Клиент Django API
└── backend/django_aiogram/
    ├── django_aiogram/  # Настройки Django
    └── tasks_app/       # Модели, API, Celery-задачи
```
