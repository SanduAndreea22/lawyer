from django import forms

from config.antispam import HoneypotMixin

from .models import Appointment


class AppointmentContactForm(HoneypotMixin, forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["client_name", "client_phone", "note"]
        widgets = {
            "client_name": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Your full name"}
            ),
            "client_phone": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "07xx xxx xxx"}
            ),
            "note": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "placeholder": "A short description of your situation (optional)",
                    "rows": 3,
                }
            ),
        }
        labels = {
            "client_name": "Full name",
            "client_phone": "Phone number",
            "note": "A few words about your situation",
        }
        error_messages = {
            "client_name": {"required": "Let us know your name, so we know who to expect."},
            "client_phone": {"required": "We'll need a phone number to confirm your booking."},
        }
