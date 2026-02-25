FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir \
    django djangorestframework django-filter celery redis \
    aiogram aiogram-dialog aiohttp python-dotenv dj-database-url \
    "psycopg[binary]"

COPY . .

ENV PYTHONPATH=/app/backend/django_aiogram
ENV DJANGO_SETTINGS_MODULE=django_aiogram.settings

EXPOSE 8000
CMD ["python", "backend/django_aiogram/manage.py", "runserver", "0.0.0.0:8000"]
