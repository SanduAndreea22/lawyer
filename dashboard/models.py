from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

from booking.models import phone_validator
from practice_areas.models import PracticeArea
from team.models import Lawyer

MAX_DOCUMENT_UPLOAD_MB = 15
ALLOWED_DOCUMENT_EXTENSIONS = ["pdf", "doc", "docx", "odt", "rtf", "txt", "jpg", "jpeg", "png"]


def validate_document_size(file):
    limit_bytes = MAX_DOCUMENT_UPLOAD_MB * 1024 * 1024
    if file.size > limit_bytes:
        raise ValidationError(f"File is larger than {MAX_DOCUMENT_UPLOAD_MB} MB.")


class Case(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In progress"
        CLOSED = "closed", "Closed"

    client_name = models.CharField(max_length=120)
    client_phone = models.CharField(max_length=20, validators=[phone_validator])
    lawyer = models.ForeignKey(Lawyer, on_delete=models.PROTECT, related_name="cases")
    practice_area = models.ForeignKey(
        PracticeArea, on_delete=models.PROTECT, related_name="cases"
    )
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.OPEN)
    description = models.TextField(blank=True)
    appointment = models.ForeignKey(
        "booking.Appointment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cases",
        help_text="The consultation this case originated from, if any.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.client_name} — {self.practice_area.name}"


class Document(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="documents")
    file = models.FileField(
        upload_to="case_documents/%Y/%m/",
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_DOCUMENT_EXTENSIONS),
            validate_document_size,
        ],
        help_text=f"Max {MAX_DOCUMENT_UPLOAD_MB} MB. Allowed types: "
        + ", ".join(ALLOWED_DOCUMENT_EXTENSIONS),
    )
    label = models.CharField(max_length=150, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.label or self.file.name


class Invoice(models.Model):
    class Status(models.TextChoices):
        UNPAID = "unpaid", "Unpaid"
        PAID = "paid", "Paid"

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="invoices")
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.UNPAID)
    description = models.CharField(max_length=200, blank=True)
    issued_at = models.DateField(auto_now_add=True)
    due_date = models.DateField()

    class Meta:
        ordering = ["due_date"]

    def __str__(self):
        return f"Invoice for {self.case.client_name} — {self.amount} RON"
