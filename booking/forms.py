from django import forms

from .models import Appointment


class AppointmentContactForm(forms.ModelForm):
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
