from django.db import models

from booking.models import phone_validator


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, validators=[phone_validator])
    message = models.CharField(max_length=280, help_text="A short description of the situation.")
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.created_at:%Y-%m-%d %H:%M}"
