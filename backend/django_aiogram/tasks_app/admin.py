from django.contrib import admin
from .models import Task, Category, TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ["telegram_id", "user", "username", "created_at"]
    search_fields = ["telegram_id", "username"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "color", "created_at"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "category", "due_date", "is_completed", "created_at"]
    list_filter = ["is_completed"]
