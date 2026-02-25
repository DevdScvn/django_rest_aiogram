# Generated manually - replace unique_together with UniqueConstraint

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tasks_app", "0001_initial"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="category",
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name="category",
            constraint=models.UniqueConstraint(
                fields=("user", "name"),
                name="unique_user_category",
            ),
        ),
    ]
