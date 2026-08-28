from django.db import migrations

LAWYERS = [
    {
        "name": "Mihai Cassian",
        "specialization": "Commercial Law",
        "years_experience": 22,
        "bio": (
            "Co-founder of the firm. Mihai has closed deals for companies "
            "from their first contract to their eventual sale, and still "
            "prefers a plain-language explanation over a thick binder."
        ),
        "order": 1,
        "areas": ["commercial-law"],
    },
    {
        "name": "Delia Voicu",
        "specialization": "Family Law",
        "years_experience": 19,
        "bio": (
            "Co-founder of the firm. Delia has guided hundreds of families "
            "through separation and custody arrangements, with a steady "
            "preference for resolution over prolonged conflict."
        ),
        "order": 2,
        "areas": ["family-law"],
    },
    {
        "name": "Radu Stoian",
        "specialization": "Real Estate Law",
        "years_experience": 14,
        "bio": (
            "Radu has handled property transactions and disputes across "
            "Bucharest for over a decade, and reads a land registry "
            "extract the way most people read a headline."
        ),
        "order": 3,
        "areas": ["real-estate-law"],
    },
    {
        "name": "Ana Petrescu",
        "specialization": "Civil Litigation",
        "years_experience": 11,
        "bio": (
            "Ana represents clients in court with a straightforward "
            "promise: an honest read on the odds before you commit to a "
            "case, not after."
        ),
        "order": 4,
        "areas": ["civil-litigation"],
    },
]


def seed_lawyers(apps, schema_editor):
    Lawyer = apps.get_model("team", "Lawyer")
    PracticeArea = apps.get_model("practice_areas", "PracticeArea")
    for entry in LAWYERS:
        entry = dict(entry)
        areas = entry.pop("areas")
        lawyer, _ = Lawyer.objects.update_or_create(
            name=entry["name"], defaults=entry
        )
        lawyer.practice_areas.set(
            PracticeArea.objects.filter(slug__in=areas)
        )


def remove_lawyers(apps, schema_editor):
    Lawyer = apps.get_model("team", "Lawyer")
    Lawyer.objects.filter(name__in=[l["name"] for l in LAWYERS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("team", "0001_initial"),
        ("practice_areas", "0002_seed_practice_areas"),
    ]

    operations = [
        migrations.RunPython(seed_lawyers, remove_lawyers),
    ]
