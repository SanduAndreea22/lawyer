from django.test import TestCase
from django.urls import reverse

from .models import ContactMessage


class ContactFormTests(TestCase):
    def test_valid_submission_creates_message_and_redirects(self):
        response = self.client.post(
            reverse("pages:contact"),
            {
                "name": "Ion Popescu",
                "phone": "0722123456",
                "message": "Need advice on a supplier contract.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)
        message = ContactMessage.objects.get()
        self.assertEqual(message.name, "Ion Popescu")

    def test_invalid_phone_is_rejected(self):
        response = self.client.post(
            reverse("pages:contact"),
            {"name": "Ion Popescu", "phone": "not-a-phone!!", "message": "x"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)


class PublicPagesSmokeTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("pages:home"))
        self.assertEqual(response.status_code, 200)

    def test_contact_page_loads(self):
        response = self.client.get(reverse("pages:contact"))
        self.assertEqual(response.status_code, 200)
