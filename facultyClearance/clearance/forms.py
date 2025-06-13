from django import forms
from .models import ClearanceDocument


class ClearanceDocumentForm(forms.ModelForm):
    class Meta:
        model = ClearanceDocument
        fields = ['document_type', 'file']
        widgets = {
            'document_type': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
