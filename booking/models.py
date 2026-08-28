import uuid

from django.core.validators import RegexValidator
from django.db import models

from practice_areas.models import PracticeArea
from team.models import Lawyer

phone_validator = RegexValidator(
    regex=r"^[0-9+()\-\s]{7,20}$",
    message="Enter a valid phone number.",
)


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    confirmation_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Opaque public identifier — used in URLs instead of the "
        "sequential id, so a booking can't be looked up by guessing/"
        "incrementing a number.",
    )
    client_name = models.CharField(max_length=120)
    client_phone = models.CharField(max_length=20, validators=[phone_validator])
    practice_area = models.ForeignKey(
        PracticeArea, on_delete=models.PROTECT, related_name="appointments"
    )
    lawyer = models.ForeignKey(
        Lawyer,
        on_delete=models.PROTECT,
        related_name="appointments",
        null=True,
        blank=True,
        help_text="Left blank means the client asked for the next available lawyer.",
    )
    start_time = models.DateTimeField()
    note = models.CharField(
        max_length=280,
        blank=True,
        help_text="A short description of the client's situation.",
    )
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["lawyer", "start_time"],
                condition=models.Q(status__in=["pending", "confirmed"]),
                name="unique_active_slot_per_lawyer",
            )
        ]

    def __str__(self):
        return f"{self.client_name} — {self.start_time:%Y-%m-%d %H:%M}"
