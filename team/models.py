from django.conf import settings
from django.db import models

from practice_areas.models import PracticeArea


class Lawyer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lawyer_profile",
        help_text="Staff login linked to this lawyer, for dashboard access.",
    )
    name = models.CharField(max_length=120)
    specialization = models.CharField(max_length=150)
    practice_areas = models.ManyToManyField(PracticeArea, related_name="lawyers")
    years_experience = models.PositiveIntegerField()
    bio = models.TextField(help_text="One or two sentences — who they are, not a full CV.")
    photo = models.ImageField(upload_to="lawyers/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    @property
    def initials(self):
        parts = self.name.split()
        return "".join(part[0] for part in parts[:2]).upper()
