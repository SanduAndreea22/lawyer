import datetime as dt

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from practice_areas.models import PracticeArea
from team.models import Lawyer

from .models import Appointment
from .services import get_available_slots


def _next_weekday_at(hour, days_ahead=7):
    day = timezone.localdate() + dt.timedelta(days=days_ahead)
    while day.weekday() >= 5:
        day += dt.timedelta(days=1)
    return timezone.make_aware(dt.datetime.combine(day, dt.time(hour, 0)))


class BookingConcurrencyTests(TestCase):
    def setUp(self):
        self.area = PracticeArea.objects.create(
            name="Test Commercial Law",
            slug="test-commercial-law",
            short_description="x",
            extended_description="x",
            who_its_for="x",
            next_steps="x",
        )
        self.lawyer = Lawyer.objects.create(
            name="Mihai Cassian",
            specialization="Commercial Law",
            years_experience=10,
            bio="x",
        )
        self.lawyer.practice_areas.add(self.area)
        self.slot = _next_weekday_at(10)

    def test_db_constraint_blocks_duplicate_active_slot(self):
        Appointment.objects.create(
            client_name="Ion Popescu",
            client_phone="0722123456",
            practice_area=self.area,
            lawyer=self.lawyer,
            start_time=self.slot,
            status=Appointment.Status.PENDING,
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Appointment.objects.create(
                    client_name="Vasile Marin",
                    client_phone="0733111222",
                    practice_area=self.area,
                    lawyer=self.lawyer,
                    start_time=self.slot,
                    status=Appointment.Status.PENDING,
                )

    def test_cancelled_slot_can_be_rebooked(self):
        first = Appointment.objects.create(
            client_name="Ion Popescu",
            client_phone="0722123456",
            practice_area=self.area,
            lawyer=self.lawyer,
            start_time=self.slot,
            status=Appointment.Status.PENDING,
        )
        first.status = Appointment.Status.CANCELLED
        first.save(update_fields=["status"])

        second = Appointment.objects.create(
            client_name="Vasile Marin",
            client_phone="0733111222",
            practice_area=self.area,
            lawyer=self.lawyer,
            start_time=self.slot,
            status=Appointment.Status.PENDING,
        )
        self.assertIsNotNone(second.pk)

    def _confirm_url(self):
        start_iso = self.slot.strftime("%Y%m%d%H%M")
        return reverse(
            "booking:confirm",
            args=[self.area.slug, self.lawyer.pk, start_iso],
        )

    def test_second_booking_of_same_slot_is_rejected(self):
        url = self._confirm_url()
        payload = {
            "client_name": "Ion Popescu",
            "client_phone": "0722123456",
            "note": "First booking",
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Appointment.objects.count(), 1)

        second_payload = {
            "client_name": "Vasile Marin",
            "client_phone": "0733111222",
            "note": "Second attempt on the same slot",
        }
        response = self.client.post(url, second_payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "no longer available")
        self.assertEqual(Appointment.objects.count(), 1)


class AvailableSlotsTests(TestCase):
    def setUp(self):
        self.area = PracticeArea.objects.create(
            name="Test Family Law",
            slug="test-family-law",
            short_description="x",
            extended_description="x",
            who_its_for="x",
            next_steps="x",
        )
        self.lawyer_a = Lawyer.objects.create(
            name="Delia Voicu", specialization="Family Law", years_experience=10, bio="x"
        )
        self.lawyer_b = Lawyer.objects.create(
            name="Ana Petrescu", specialization="Family Law", years_experience=8, bio="x"
        )
        self.lawyer_a.practice_areas.add(self.area)
        self.lawyer_b.practice_areas.add(self.area)

    def test_any_available_offers_the_other_lawyer_when_one_is_booked(self):
        slot = _next_weekday_at(9)
        Appointment.objects.create(
            client_name="Booked Client",
            client_phone="0700000000",
            practice_area=self.area,
            lawyer=self.lawyer_a,
            start_time=slot,
            status=Appointment.Status.CONFIRMED,
        )

        slots_by_day = get_available_slots(self.area, lawyer=None)
        day = slot.date()
        day_slots = slots_by_day.get(day, [])
        matching = [s for s in day_slots if s["start"] == slot]
        self.assertTrue(matching, "expected the 09:00 slot to still be offered via the other lawyer")
        self.assertEqual(matching[0]["lawyer"], self.lawyer_b)
