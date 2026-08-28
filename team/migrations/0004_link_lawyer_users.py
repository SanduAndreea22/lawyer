from django.contrib.auth.hashers import make_password
from django.db import migrations

DEMO_PASSWORD = "demo12345"

USERNAMES = {
    "Mihai Cassian": "mihai.cassian",
    "Delia Voicu": "delia.voicu",
    "Radu Stoian": "radu.stoian",
    "Ana Petrescu": "ana.petrescu",
}


def link_users(apps, schema_editor):
    Lawyer = apps.get_model("team", "Lawyer")
    User = apps.get_model("auth", "User")
    hashed = make_password(DEMO_PASSWORD)
    for name, username in USERNAMES.items():
        try:
            lawyer = Lawyer.objects.get(name=name)
        except Lawyer.DoesNotExist:
            continue
        first, _, last = name.partition(" ")
        user, _ = User.objects.update_or_create(
            username=username,
            defaults={
                "first_name": first,
                "last_name": last,
                "is_staff": False,
                "password": hashed,
            },
        )
        lawyer.user = user
        lawyer.save(update_fields=["user"])


def unlink_users(apps, schema_editor):
    Lawyer = apps.get_model("team", "Lawyer")
    User = apps.get_model("auth", "User")
    Lawyer.objects.filter(name__in=USERNAMES.keys()).update(user=None)
    User.objects.filter(username__in=USERNAMES.values()).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("team", "0003_lawyer_user"),
    ]

    operations = [
        migrations.RunPython(link_users, unlink_users),
    ]
