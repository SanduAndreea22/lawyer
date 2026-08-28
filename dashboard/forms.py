from django import forms

from .models import Case, Document, Invoice


class CaseStatusForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ["status", "description"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(
                attrs={"class": "form-input", "rows": 4}
            ),
        }


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["file", "label"]
        widgets = {
            "label": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "e.g. Signed contract"}
            ),
        }


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ["amount", "description", "due_date"]
        widgets = {
            "amount": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "e.g. 1200.00", "step": "0.01"}
            ),
            "description": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "e.g. Initial contract review"}
            ),
            "due_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
        }
        labels = {"amount": "Amount (RON)"}
