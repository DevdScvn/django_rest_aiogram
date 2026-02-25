from django.conf import settings
from django.db import models

from ..utils.id_generator import generate_id


def category_id_default():
    return generate_id("category")


class Category(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=20,
        editable=False,
        default=category_id_default,
    )
    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
    )
    color = models.CharField(max_length=7, default="#3498db", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_user_category",
            ),
        ]

    def __str__(self):
        return self.name
