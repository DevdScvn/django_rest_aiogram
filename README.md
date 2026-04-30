# Django + Aiogram ToDo List

Telegram-бот для управления задачами с Django REST API в качестве бэкенда. Пользователи создают задачи, назначают категории и сроки, получают уведомления о приближающихся дедлайнах.

---

## Содержание

- [Возможности](#возможности)
- [Структура проекта](#структура-проекта)
- [Модули и компоненты](#модули-и-компоненты)
- [Требования](#требования)
- [Установка через uv](#установка-через-uv)
- [Запуск](#запуск)
- [Запуск через Docker](#запуск-через-docker)
- [Использование бота](#использование-бота)
- [API](#api)

---

## Возможности

- **Задачи** — создание, просмотр, отметка выполненными, удаление
- **Категории** — создание и удаление категорий для группировки задач
- **Уведомления** — Celery проверяет просроченные и приближающиеся задачи каждые 8 часов и отправляет напоминания в Telegram

---

## Структура проекта

```
aiogram_django_rest_v2/
│
├── bot/                          # Telegram-бот (aiogram 3.x)
│   ├── main.py                   # Точка входа, инициализация бота
│   ├── config.py                 # Настройки из .env
│   ├── api_client.py             # HTTP-клиент для Django API
│   ├── add_task.py               # Диалог добавления задачи (aiogram-dialog)
│   ├── list_tasks.py             # Список и управление задачами
│   ├── categories.py             # Управление категориями
│   ├── keyboards.py              # Клавиатуры бота
│   ├── states.py                 # FSM-состояния
│   ├── handlers/                 # Обработчики команд
│   │   ├── start.py              # /start
│   │   └── add_task.py           # Обработчик кнопки «Добавить задачу»
│   └── utils/
│       └── date_parser.py        # Парсинг дат из текста
│
├── backend/
│   └── django_aiogram/           # Django-проект
│       ├── manage.py
│       ├── django_aiogram/       # Настройки Django
│       │   ├── settings.py
│       │   ├── urls.py
│       │   ├── celery.py         # Конфигурация Celery
│       │   └── wsgi.py / asgi.py
│       │
│       └── tasks_app/            # Приложение «Задачи»
│           ├── models/           # Модели БД
│           │   ├── user.py       # TelegramUser
│           │   ├── task.py       # Task
│           │   └── category.py   # Category
│           ├── views.py          # REST API (ViewSet)
│           ├── serializers.py
│           ├── urls.py
│           ├── tasks.py          # Celery-задачи (проверка дедлайнов)
│           ├── authentication.py # Аутентификация по Telegram ID
│           ├── middleware.py
│           ├── admin.py
│           ├── services/
│           │   └── telegram_auth.py
│           └── notifications/
│               └── telegram.py   # Отправка сообщений в Telegram
│
├── pyproject.toml                # Зависимости (uv / pip)
├── uv.lock                       # Lock-файл uv
├── .env_example                  # Пример переменных окружения
├── docker-compose.yaml           # Docker: PostgreSQL, Redis, Django, Celery, бот
└── Dockerfile
```

---

## Модули и компоненты

| Модуль / компонент | Назначение |
|--------------------|------------|
| **bot** | Telegram-бот на aiogram 3.x. Обрабатывает команды, показывает списки задач и категорий, ведёт диалог добавления задачи через aiogram-dialog. |
| **bot.api_client** | Асинхронный HTTP-клиент для запросов к Django REST API (задачи, категории, аутентификация). |
| **bot.add_task** | Диалог пошагового создания задачи: название → описание → категория → срок. |
| **bot.list_tasks** | Просмотр списка задач, отметка выполненными, удаление. |
| **bot.categories** | Создание и удаление категорий. |
| **backend/django_aiogram** | Django-проект: REST API, админка, Celery. |
| **tasks_app** | Django-приложение: модели User, Task, Category; ViewSet'ы; Celery-задачи; уведомления в Telegram. |
| **tasks_app.tasks** | Celery: `check_due_tasks` — поиск задач с дедлайном в ближайшие 24 часа; `send_telegram_notification` — отправка напоминания. |
| **tasks_app.notifications.telegram** | Синхронная отправка сообщений в Telegram по `telegram_id`. |

---

## Требования

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — пакетный менеджер (рекомендуется)
- Redis — брокер для Celery
- PostgreSQL — при запуске через Docker (опционально; локально можно использовать SQLite)

---

## Установка через uv

### 1. Установите uv

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux / macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Клонируйте репозиторий и перейдите в каталог
```bash
git clone https://github.com/DevdScvn/django_rest_aiogram
```

```bash
cd aiogram_django_rest_v2z
```

### 3. Создайте виртуальное окружение и установите зависимости

```bash
uv sync
```

Команда `uv sync`:
- создаёт виртуальное окружение (если его нет);
- устанавливает зависимости из `pyproject.toml`;
- использует версии из `uv.lock` для воспроизводимой сборки.

### 4. Активируйте окружение (опционально)

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
source .venv/bin/activate
```

> Если используете `uv run`, активация не обязательна — uv сам подхватит окружение.

### 5. Создайте файл `.env`

Скопируйте `.env_example` в `.env` и заполните:

```env
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
DJANGO_API_URL=http://localhost:8000
```

### 6. Примените миграции Django

```bash
uv run python backend/django_aiogram/manage.py migrate
```

---

## Запуск

Запустите компоненты в отдельных терминалах.

**1. Django-сервер**

```bash
uv run python backend/django_aiogram/manage.py runserver
```

**2. Celery worker** (обработка задач)

```bash
cd backend/django_aiogram
uv run celery -A django_aiogram worker -l info
```

**3. Celery beat** (периодическая проверка дедлайнов)

```bash
cd backend/django_aiogram
uv run celery -A django_aiogram beat -l info
```

**4. Telegram-бот**

```bash
uv run python -m bot.main
```

> Бот запускается из корня проекта, где находится модуль `bot`.

---

## Запуск через Docker

Все сервисы (PostgreSQL, Redis, Django, Celery worker, Celery beat, бот) поднимаются одной командой:

```bash
docker compose up -d
```

Перед запуском создайте `.env` с `TELEGRAM_BOT_TOKEN` и при необходимости скорректируйте переменные в `docker-compose.yaml`.

---

## Использование бота

1. Найдите бота в Telegram и отправьте `/start`.
2. Меню:
   - **📋 Мои задачи** — список задач, удаление, отметка выполненными
   - **➕ Добавить задачу** — диалог создания задачи (название, описание, категория, срок)
   - **📁 Мои категории** — управление категориями

---

## API

REST API доступен по адресу `http://localhost:8000/api/`:

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET, POST | `/api/tasks/` | Список и создание задач |
| GET, PUT, DELETE | `/api/tasks/{id}/` | Одна задача |
| GET, POST | `/api/categories/` | Категории |
| POST | `/api/auth/telegram/` | Регистрация/аутентификация по Telegram ID |
   
