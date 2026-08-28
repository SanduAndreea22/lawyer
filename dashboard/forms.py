from django import forms

from .models import Case, Document


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
