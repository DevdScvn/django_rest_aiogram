import re

from rest_framework import serializers

from .models import Task, Category

HEX_COLOR_PATTERN = re.compile(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "color", "created_at"]
        read_only_fields = ["created_at"]

    def validate_color(self, value):
        if value and not HEX_COLOR_PATTERN.match(value):
            raise serializers.ValidationError(
                "Цвет должен быть в формате HEX (#RGB или #RRGGBB)"
            )
        return value or "#3498db"


class TaskSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "category", "category_name",
            "due_date", "created_at", "updated_at", "is_completed",
        ]
        read_only_fields = ["created_at", "updated_at"]


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["title", "description", "category", "due_date"]


class TelegramAuthSerializer(serializers.Serializer):
    """Сериализатор для регистрации/привязки по telegram_id."""

    telegram_id = serializers.IntegerField(required=True, min_value=1)
    username = serializers.CharField(required=False, default="", max_length=255, allow_blank=True)
    first_name = serializers.CharField(required=False, default="", max_length=255, allow_blank=True)
    last_name = serializers.CharField(required=False, default="", max_length=255, allow_blank=True)
