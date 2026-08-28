import uuid

from django.db import migrations


def populate_tokens(apps, schema_editor):
    Appointment = apps.get_model("booking", "Appointment")
    for appointment in Appointment.objects.filter(confirmation_token__isnull=True):
        appointment.confirmation_token = uuid.uuid4()
        appointment.save(update_fields=["confirmation_token"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("booking", "0002_appointment_confirmation_token"),
    ]

    operations = [
        migrations.RunPython(populate_tokens, noop),
    ]
