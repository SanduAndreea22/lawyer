from django.test import TestCase
from django.urls import reverse

from .models import PracticeArea


class PracticeAreaViewTests(TestCase):
    def setUp(self):
        self.active_area = PracticeArea.objects.create(
            name="Test Commercial Law",
            slug="test-commercial-law",
            short_description="Short description.",
            extended_description="Extended description.",
            who_its_for="Business owners.",
            next_steps="We review your documents.",
        )
        self.inactive_area = PracticeArea.objects.create(
            name="Test Retired Area",
            slug="test-retired-area",
            short_description="x",
            extended_description="x",
            who_its_for="x",
            next_steps="x",
            is_active=False,
        )

    def test_list_page_shows_only_active_areas(self):
        response = self.client.get(reverse("practice_areas:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.active_area.name)
        self.assertNotContains(response, self.inactive_area.name)

    def test_detail_page_for_active_area(self):
        response = self.client.get(
            reverse("practice_areas:detail", args=[self.active_area.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.active_area.who_its_for)

    def test_detail_page_404s_for_inactive_area(self):
        response = self.client.get(
            reverse("practice_areas:detail", args=[self.inactive_area.slug])
        )
        self.assertEqual(response.status_code, 404)

    def test_detail_page_404s_for_unknown_slug(self):
        response = self.client.get(
            reverse("practice_areas:detail", args=["does-not-exist"])
        )
        self.assertEqual(response.status_code, 404)

    def test_get_absolute_url(self):
        self.assertEqual(
            self.active_area.get_absolute_url(),
            reverse("practice_areas:detail", args=[self.active_area.slug]),
        )
