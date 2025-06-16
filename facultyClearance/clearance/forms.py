from django import forms
from .models import Upload, Requirement


class UploadForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            role = None
            if hasattr(user, 'facultymember'):
                role = 'part_timer' if user.facultymember.is_part_time else 'faculty'
            elif hasattr(user, 'departmentchair'):
                role = 'chair'
            elif hasattr(user, 'collegedean'):
                role = 'dean'

            if role:
                self.fields['requirement'].queryset = Requirement.objects.filter(applicable_to=role)
            else:
                self.fields['requirement'].queryset = Requirement.objects.none()

        # If a requirement is already provided via `initial`, disable the dropdown
        if self.initial.get('requirement'):
            self.fields['requirement'].disabled = True  # makes it read-only in the form
