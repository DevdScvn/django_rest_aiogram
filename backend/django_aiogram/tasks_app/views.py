from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Task, Category
from .serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    CategorySerializer,
    TelegramAuthSerializer,
)
from .authentication import TelegramAuthentication
from .services.telegram_auth import register_or_link_telegram_user


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    authentication_classes = [TelegramAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).select_related("category")

    def get_serializer_class(self):
        if self.action == "create":
            return TaskCreateSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    authentication_classes = [TelegramAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TelegramAuthView(APIView):
    """Регистрация/привязка пользователя по telegram_id."""

    def post(self, request):
        serializer = TelegramAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tg_user, created = register_or_link_telegram_user(
            telegram_id=serializer.validated_data["telegram_id"],
            username=serializer.validated_data.get("username", ""),
            first_name=serializer.validated_data.get("first_name", ""),
            last_name=serializer.validated_data.get("last_name", ""),
        )
        return Response({"user_id": tg_user.user.id, "created": created})
