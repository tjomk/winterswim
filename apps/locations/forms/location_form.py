"""
Forms for location submission.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.locations.models import Location, LocationType, Facility


class LocationSubmissionForm(forms.Form):
    """
    Form for submitting a new location (no authentication required).

    This is a simplified form for public submission.
    Moderators will review and approve submissions via Django admin.
    """

    # Basic information
    name = forms.CharField(
        max_length=200,
        label=_('Location name'),
        help_text=_('What is this place called?'),
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': _('e.g., Pirita Beach'),
        })
    )

    description = forms.CharField(
        label=_('Description'),
        help_text=_('Describe this swimming location'),
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 4,
            'placeholder': _('Tell us about this location...'),
        })
    )

    # Location
    latitude = forms.FloatField(
        label=_('Latitude'),
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'step': '0.000001',
            'placeholder': '59.0',
        })
    )

    longitude = forms.FloatField(
        label=_('Longitude'),
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'step': '0.000001',
            'placeholder': '25.0',
        })
    )

    address = forms.CharField(
        max_length=500,
        required=False,
        label=_('Address'),
        help_text=_('Nearest address or landmark'),
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': _('e.g., Pirita tee 1, Tallinn'),
        })
    )

    # Type and facilities
    location_type = forms.ChoiceField(
        choices=LocationType.choices,
        initial=LocationType.WILD,
        label=_('Location type'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    facilities = forms.MultipleChoiceField(
        choices=Facility.choices,
        required=False,
        label=_('Available facilities'),
        help_text=_('Select all that apply'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox'})
    )

    access_instructions = forms.CharField(
        required=False,
        label=_('Access instructions'),
        help_text=_('How to get there and find the swimming spot'),
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 3,
            'placeholder': _('e.g., Park at the beach parking lot, walk 200m north...'),
        })
    )

    # Contact information
    website = forms.URLField(
        required=False,
        label=_('Website'),
        widget=forms.URLInput(attrs={
            'class': 'form-input',
            'placeholder': 'https://...',
        })
    )

    email = forms.EmailField(
        required=False,
        label=_('Contact email'),
        help_text=_('Email for inquiries about this location'),
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'info@example.com',
        })
    )

    phone = forms.CharField(
        max_length=50,
        required=False,
        label=_('Phone number'),
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+372...',
        })
    )

    # Pricing
    is_free = forms.BooleanField(
        required=False,
        initial=True,
        label=_('Free access'),
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )

    pricing_details = forms.CharField(
        required=False,
        label=_('Pricing details'),
        help_text=_('If not free, describe the pricing'),
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 2,
            'placeholder': _('e.g., €5 per visit, €50 monthly membership'),
        })
    )

    # Submitter information
    submitted_by_name = forms.CharField(
        max_length=200,
        required=False,
        label=_('Your name'),
        help_text=_('Optional: Let us know who suggested this location'),
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': _('Your name'),
        })
    )

    submitted_by_email = forms.EmailField(
        required=False,
        label=_('Your email'),
        help_text=_('Optional: We may contact you about this submission'),
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'your@email.com',
        })
    )

    def clean(self):
        """Custom validation for the entire form."""
        cleaned_data = super().clean()

        # Validate coordinates
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')

        if latitude is not None and not (-90 <= latitude <= 90):
            self.add_error('latitude', _('Latitude must be between -90 and 90'))

        if longitude is not None and not (-180 <= longitude <= 180):
            self.add_error('longitude', _('Longitude must be between -180 and 180'))

        # If location is not free, pricing details should be provided
        is_free = cleaned_data.get('is_free', True)
        pricing_details = cleaned_data.get('pricing_details', '').strip()

        if not is_free and not pricing_details:
            self.add_error(
                'pricing_details',
                _('Please provide pricing details if access is not free')
            )

        return cleaned_data
