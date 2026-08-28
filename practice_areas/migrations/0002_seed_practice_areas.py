from django.db import migrations

AREAS = [
    {
        "name": "Commercial Law",
        "slug": "commercial-law",
        "order": 1,
        "short_description": "Business structuring, commercial contracts, and mergers and acquisitions for companies at every stage.",
        "extended_description": (
            "We advise on company formation and structuring, shareholder and "
            "founder agreements, commercial contracts with suppliers and "
            "clients, and mergers, acquisitions, and investment rounds. "
            "Whether you're setting up a new venture or negotiating your "
            "next deal, we translate the legal side into decisions you can "
            "actually make."
        ),
        "who_its_for": (
            "Founders setting up a company for the first time, business "
            "owners negotiating contracts they don't want to sign blind, "
            "and companies preparing for a sale, merger, or investment round."
        ),
        "next_steps": (
            "We review what you bring — a contract, a term sheet, or simply "
            "a plan — and tell you plainly what it means, what's missing, "
            "and what we'd change before you sign anything."
        ),
    },
    {
        "name": "Real Estate Law",
        "slug": "real-estate-law",
        "order": 2,
        "short_description": "Transactions, due diligence, and disputes involving property — from purchase to litigation.",
        "extended_description": (
            "We handle purchase and sale transactions, title and due "
            "diligence checks before you commit, lease agreements, and "
            "disputes between owners, tenants, or neighbors when a "
            "property deal goes wrong."
        ),
        "who_its_for": (
            "Anyone buying or selling a property who wants a proper check "
            "before signing, landlords and tenants with a lease dispute, "
            "and owners in a boundary or title conflict."
        ),
        "next_steps": (
            "Bring the documents you already have — a preliminary contract, "
            "a land registry extract, a lease — and we'll walk through "
            "exactly what they mean for you."
        ),
    },
    {
        "name": "Family Law",
        "slug": "family-law",
        "order": 3,
        "short_description": "Discreet guidance through sensitive moments — divorce, custody, and asset division — with a focus on solutions, not prolonged conflict.",
        "extended_description": (
            "We handle divorce, child custody and visitation arrangements, "
            "division of shared assets, and maintenance obligations. Our "
            "approach favors a fair, negotiated resolution wherever "
            "possible, with litigation as the option when negotiation "
            "isn't."
        ),
        "who_its_for": (
            "Anyone going through a separation or divorce, parents working "
            "out custody arrangements, and families needing a fair, "
            "documented division of assets."
        ),
        "next_steps": (
            "This first conversation is private and unhurried. We listen "
            "to your situation first, then explain the realistic paths "
            "forward — there's no pressure to decide anything on the spot."
        ),
    },
    {
        "name": "Civil Litigation",
        "slug": "civil-litigation",
        "order": 4,
        "short_description": "Court representation, built on an honest assessment of the risks — not empty promises.",
        "extended_description": (
            "We represent clients in civil disputes before the courts — "
            "contract breaches, debt recovery, liability claims, and "
            "disputes between individuals or businesses — with a strategy "
            "built on the actual merits of the case."
        ),
        "who_its_for": (
            "Anyone facing a civil claim, or considering bringing one, who "
            "wants a clear-eyed view of their chances before committing "
            "time and cost to a court process."
        ),
        "next_steps": (
            "We review the facts and any documents you have, give you an "
            "honest read on the strength of the case, and outline what "
            "litigation would actually involve — time, cost, and likely "
            "outcome."
        ),
    },
]


def seed_areas(apps, schema_editor):
    PracticeArea = apps.get_model("practice_areas", "PracticeArea")
    for area in AREAS:
        PracticeArea.objects.update_or_create(slug=area["slug"], defaults=area)


def remove_areas(apps, schema_editor):
    PracticeArea = apps.get_model("practice_areas", "PracticeArea")
    PracticeArea.objects.filter(slug__in=[a["slug"] for a in AREAS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("practice_areas", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_areas, remove_areas),
    ]
