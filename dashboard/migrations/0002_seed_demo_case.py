import datetime as dt

from django.db import migrations


def seed_demo_case(apps, schema_editor):
    Lawyer = apps.get_model("team", "Lawyer")
    PracticeArea = apps.get_model("practice_areas", "PracticeArea")
    Case = apps.get_model("dashboard", "Case")
    Invoice = apps.get_model("dashboard", "Invoice")

    try:
        lawyer = Lawyer.objects.get(name="Mihai Cassian")
        area = PracticeArea.objects.get(slug="commercial-law")
    except (Lawyer.DoesNotExist, PracticeArea.DoesNotExist):
        return

    case, created = Case.objects.update_or_create(
        client_name="Bogdan Ilie",
        lawyer=lawyer,
        practice_area=area,
        defaults={
            "client_phone": "0744123456",
            "status": "in_progress",
            "description": "Reviewing a supplier contract ahead of renewal — checking termination and liability clauses.",
        },
    )
    Invoice.objects.update_or_create(
        case=case,
        description="Initial contract review",
        defaults={
            "amount": "1200.00",
            "status": "unpaid",
            "due_date": dt.date.today() + dt.timedelta(days=14),
        },
    )


def remove_demo_case(apps, schema_editor):
    Case = apps.get_model("dashboard", "Case")
    Case.objects.filter(client_name="Bogdan Ilie").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0001_initial"),
        ("team", "0004_link_lawyer_users"),
        ("practice_areas", "0002_seed_practice_areas"),
    ]

    operations = [
        migrations.RunPython(seed_demo_case, remove_demo_case),
    ]
