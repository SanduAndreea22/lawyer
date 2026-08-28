from django.test import TestCase
from django.urls import reverse

from practice_areas.models import PracticeArea

from .models import Lawyer


class TeamViewTests(TestCase):
    def setUp(self):
        self.area = PracticeArea.objects.create(
            name="Test Family Law",
            slug="test-family-law",
            short_description="x",
            extended_description="x",
            who_its_for="x",
            next_steps="x",
        )
        self.active_lawyer = Lawyer.objects.create(
            name="Delia Voicu",
            specialization="Family Law",
            years_experience=12,
            bio="Handles family law matters.",
        )
        self.active_lawyer.practice_areas.add(self.area)
        self.inactive_lawyer = Lawyer.objects.create(
            name="Retired Lawyer",
            specialization="Family Law",
            years_experience=30,
            bio="No longer practicing.",
            is_active=False,
        )

    def test_list_page_shows_only_active_lawyers(self):
        response = self.client.get(reverse("team:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.active_lawyer.name)
        self.assertNotContains(response, self.inactive_lawyer.name)

    def test_initials_property(self):
        self.assertEqual(self.active_lawyer.initials, "DV")

    def test_initials_property_handles_single_word_name(self):
        solo = Lawyer.objects.create(name="Madonna", specialization="x", years_experience=1, bio="x")
        self.assertEqual(solo.initials, "M")
