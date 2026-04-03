from django import forms
from .models import IssueReport, ISSUE_CATEGORIES


class LocationForm(forms.Form):
    latitude = forms.DecimalField(
        required=False,
        widget=forms.HiddenInput(),
    )
    longitude = forms.DecimalField(
        required=False,
        widget=forms.HiddenInput(),
    )
    address_text = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter street address or landmark…',
            'class': 'text-input',
            'autocomplete': 'street-address',
        })
    )

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get('latitude')
        lng = cleaned.get('longitude')
        address = cleaned.get('address_text', '').strip()
        if not lat and not address:
            raise forms.ValidationError(
                'Please provide your location using GPS or by typing an address.'
            )
        return cleaned


class ReportSubmitForm(forms.ModelForm):
    class Meta:
        model = IssueReport
        fields = ['category', 'description', 'photo', 'reporter_name', 'reporter_phone']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'placeholder': 'Describe the issue in detail…',
                'rows': 4,
                'class': 'form-textarea',
                'id': 'description-field',
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'file-input',
                'accept': 'image/*',
                'capture': 'environment',
            }),
            'reporter_name': forms.TextInput(attrs={
                'placeholder': 'Your name (optional)',
                'class': 'form-input',
            }),
            'reporter_phone': forms.TextInput(attrs={
                'placeholder': '+27 00 000 0000 (optional, for WhatsApp updates)',
                'class': 'form-input',
                'type': 'tel',
            }),
        }
        labels = {
            'category': 'Issue Type',
            'description': 'Description',
            'photo': 'Add Photo',
            'reporter_name': 'Your Name',
            'reporter_phone': 'WhatsApp Number',
        }
