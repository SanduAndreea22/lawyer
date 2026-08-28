from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from team.models import Lawyer

DEMO_PASSWORD = "demo12345"

USERNAMES = {
    "Mihai Cassian": "mihai.cassian",
    "Delia Voicu": "delia.voicu",
    "Radu Stoian": "radu.stoian",
    "Ana Petrescu": "ana.petrescu",
}


class Command(BaseCommand):
    help = (
        "Create/link demo staff logins for the seeded lawyers, all sharing "
        "the same password (see DEMO_PASSWORD in this file). For local "
        "development and demos only - never run this against a real "
        "deployment with real client data."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default=DEMO_PASSWORD,
            help="Password to set for every seeded account (default: %(default)s).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        password = options["password"]
        for name, username in USERNAMES.items():
            try:
                lawyer = Lawyer.objects.get(name=name)
            except Lawyer.DoesNotExist:
                self.stderr.write(f"Skipping {name}: no matching Lawyer record.")
                continue

            first, _, last = name.partition(" ")
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": first, "last_name": last, "is_staff": False},
            )
            user.first_name = first
            user.last_name = last
            user.set_password(password)
            user.save()

            lawyer.user = user
            lawyer.save(update_fields=["user"])

            verb = "Created" if created else "Updated"
            self.stdout.write(f"{verb} login for {name}: {username}")

        self.stdout.write(self.style.SUCCESS(f"Done. Password for all accounts: {password}"))
