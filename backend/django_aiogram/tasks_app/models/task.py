from django.conf import settings
from django.db import models

from ..utils.id_generator import generate_id


def task_id_default():
    return generate_id("task")


class Task(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=20,
        editable=False,
        default=task_id_default,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
