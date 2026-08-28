from django.db import models
from django.urls import reverse


class PracticeArea(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=110, unique=True)
    short_description = models.CharField(
        max_length=220,
        help_text="One or two plain-language sentences, shown on the homepage card.",
    )
    extended_description = models.TextField(
        help_text="What this practice area covers, in plain language."
    )
    who_its_for = models.TextField(help_text="Who this practice area is a good fit for.")
    next_steps = models.TextField(help_text="What happens after the first conversation.")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Practice area"
        verbose_name_plural = "Practice areas"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("practice_areas:detail", args=[self.slug])
