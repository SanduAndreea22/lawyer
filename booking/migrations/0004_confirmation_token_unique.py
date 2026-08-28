import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking", "0003_populate_confirmation_token"),
    ]

    operations = [
        migrations.AlterField(
            model_name="appointment",
            name="confirmation_token",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                unique=True,
                help_text="Opaque public identifier — used in URLs instead of the "
                "sequential id, so a booking can't be looked up by guessing/"
                "incrementing a number.",
            ),
        ),
    ]
