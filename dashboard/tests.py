import datetime as dt

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from booking.models import Appointment
from dashboard.models import Case, Invoice
from practice_areas.models import PracticeArea
from team.models import Lawyer


def _next_weekday_at(hour, days_ahead=7):
    day = timezone.localdate() + dt.timedelta(days=days_ahead)
    while day.weekday() >= 5:
        day += dt.timedelta(days=1)
    return timezone.make_aware(dt.datetime.combine(day, dt.time(hour, 0)))


class DashboardScopingTests(TestCase):
    def setUp(self):
        self.area = PracticeArea.objects.create(
            name="Test Commercial Law",
            slug="test-commercial-law",
            short_description="x",
            extended_description="x",
            who_its_for="x",
            next_steps="x",
        )
        self.user_a = User.objects.create_user("lawyer.a", password="testpass123")
        self.user_b = User.objects.create_user("lawyer.b", password="testpass123")
        self.lawyer_a = Lawyer.objects.create(
            user=self.user_a, name="Lawyer A", specialization="Commercial Law",
            years_experience=5, bio="x",
        )
        self.lawyer_b = Lawyer.objects.create(
            user=self.user_b, name="Lawyer B", specialization="Commercial Law",
            years_experience=5, bio="x",
        )
        self.case_a = Case.objects.create(
            client_name="Client A",
            client_phone="0700000001",
            lawyer=self.lawyer_a,
            practice_area=self.area,
        )

    def test_unauthenticated_user_is_redirected_to_login(self):
        response = self.client.get(reverse("dashboard:overview"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("dashboard:login"), response.url)

    def test_lawyer_cannot_view_another_lawyers_case(self):
        self.client.login(username="lawyer.b", password="testpass123")
        response = self.client.get(reverse("dashboard:case_detail", args=[self.case_a.pk]))
        self.assertEqual(response.status_code, 404)

    def test_lawyer_can_view_own_case(self):
        self.client.login(username="lawyer.a", password="testpass123")
        response = self.client.get(reverse("dashboard:case_detail", args=[self.case_a.pk]))
        self.assertEqual(response.status_code, 200)

    def test_superuser_sees_every_lawyers_case(self):
        User.objects.create_superuser("admin", "admin@example.com", "testpass123")
        self.client.login(username="admin", password="testpass123")
        response = self.client.get(reverse("dashboard:case_detail", args=[self.case_a.pk]))
        self.assertEqual(response.status_code, 200)


class AppointmentManagementTests(TestCase):
    def setUp(self):
        self.area = PracticeArea.objects.create(
            name="Test Family Law",
            slug="test-family-law",
            short_description="x",
            extended_description="x",
            who_its_for="x",
            next_steps="x",
        )
        self.user = User.objects.create_user("lawyer.a", password="testpass123")
        self.lawyer = Lawyer.objects.create(
            user=self.user, name="Lawyer A", specialization="Family Law",
            years_experience=5, bio="x",
        )
        self.lawyer.practice_areas.add(self.area)
        self.appointment = Appointment.objects.create(
            client_name="Client A",
            client_phone="0700000001",
            practice_area=self.area,
            lawyer=self.lawyer,
            start_time=_next_weekday_at(9),
            status=Appointment.Status.CONFIRMED,
        )
        self.client.login(username="lawyer.a", password="testpass123")

    def test_confirm_and_open_case_flow(self):
        self.appointment.status = Appointment.Status.PENDING
        self.appointment.save(update_fields=["status"])

        response = self.client.post(
            reverse("dashboard:appointment_confirm", args=[self.appointment.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, Appointment.Status.CONFIRMED)

        response = self.client.post(
            reverse("dashboard:appointment_open_case", args=[self.appointment.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Case.objects.filter(appointment=self.appointment).count(), 1)

        # Calling it again should reuse the existing case, not create a second one.
        self.client.post(reverse("dashboard:appointment_open_case", args=[self.appointment.pk]))
        self.assertEqual(Case.objects.filter(appointment=self.appointment).count(), 1)

    def test_reschedule_to_a_free_slot_moves_the_appointment(self):
        new_start = _next_weekday_at(11)
        start_iso = new_start.strftime("%Y%m%d%H%M")
        url = reverse(
            "dashboard:appointment_reschedule_confirm",
            args=[self.appointment.pk, start_iso],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.start_time, new_start)

    def test_reschedule_rejects_a_slot_taken_by_another_appointment(self):
        other_start = _next_weekday_at(11)
        Appointment.objects.create(
            client_name="Someone Else",
            client_phone="0700000002",
            practice_area=self.area,
            lawyer=self.lawyer,
            start_time=other_start,
            status=Appointment.Status.CONFIRMED,
        )
        start_iso = other_start.strftime("%Y%m%d%H%M")
        url = reverse(
            "dashboard:appointment_reschedule_confirm",
            args=[self.appointment.pk, start_iso],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.appointment.refresh_from_db()
        self.assertNotEqual(self.appointment.start_time, other_start)


class InvoiceTests(TestCase):
    def setUp(self):
        self.area = PracticeArea.objects.create(
            name="Test Civil Litigation",
            slug="test-civil-litigation",
            short_description="x",
            extended_description="x",
            who_its_for="x",
            next_steps="x",
        )
        self.user = User.objects.create_user("lawyer.a", password="testpass123")
        self.lawyer = Lawyer.objects.create(
            user=self.user, name="Lawyer A", specialization="Civil Litigation",
            years_experience=5, bio="x",
        )
        self.case = Case.objects.create(
            client_name="Client A",
            client_phone="0700000001",
            lawyer=self.lawyer,
            practice_area=self.area,
        )
        self.client.login(username="lawyer.a", password="testpass123")

    def test_creating_an_invoice_from_the_case_detail_page(self):
        url = reverse("dashboard:case_detail", args=[self.case.pk])
        response = self.client.post(
            url,
            {
                "create_invoice": "1",
                "amount": "450.00",
                "description": "Follow-up review",
                "due_date": "2026-10-01",
            },
        )
        self.assertEqual(response.status_code, 302)
        invoice = Invoice.objects.get(case=self.case)
        self.assertEqual(str(invoice.amount), "450.00")
        self.assertEqual(invoice.status, Invoice.Status.UNPAID)

    def test_toggle_paid_flips_status(self):
        invoice = Invoice.objects.create(
            case=self.case, amount="200.00", due_date="2026-10-01"
        )
        url = reverse("dashboard:invoice_toggle_paid", args=[invoice.pk])
        self.client.post(url)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.Status.PAID)
