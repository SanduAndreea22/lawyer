from django import forms

from config.antispam import HoneypotMixin

from .models import ContactMessage


class ContactMessageForm(HoneypotMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "phone", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Your full name"}),
            "phone": forms.TextInput(attrs={"class": "form-input", "placeholder": "07xx xxx xxx"}),
            "message": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "placeholder": "A short description of your situation",
                    "rows": 3,
                }
            ),
        }
        labels = {
            "name": "Full name",
            "phone": "Phone number",
            "message": "A few words about your situation",
        }
        error_messages = {
            "name": {"required": "Let us know your name, so we know who to expect."},
            "phone": {"required": "We'll need a phone number to call you back."},
            "message": {"required": "A line or two helps us understand your situation."},
        }
