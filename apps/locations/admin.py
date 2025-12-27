"""
Django admin configuration for Location models.

Provides moderation interface for submitted locations.
"""

from django import forms
from django.contrib import admin
from django.contrib.gis import admin as gis_admin
from django.contrib.gis.geos import Point
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin

from .models import Location, LocationPhoto
from .models.location import Facility
from .repositories import bulk_approve_locations, bulk_reject_locations


class LocationAdminForm(forms.ModelForm):
    """Custom form for Location admin with manual lat/lon input."""

    latitude = forms.FloatField(
        required=False,
        label=_('Latitude'),
        help_text=_('Latitude (e.g., 59.437222)'),
        widget=forms.NumberInput(attrs={'step': 'any'})
    )

    longitude = forms.FloatField(
        required=False,
        label=_('Longitude'),
        help_text=_('Longitude (e.g., 24.753889)'),
        widget=forms.NumberInput(attrs={'step': 'any'})
    )

    facilities = forms.MultipleChoiceField(
        required=False,
        label=_('Facilities'),
        help_text=_('Select available facilities'),
        choices=Facility.choices,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Location
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """Initialize form with current lat/lon and facilities values."""
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            if self.instance.location:
                self.fields['latitude'].initial = self.instance.latitude
                self.fields['longitude'].initial = self.instance.longitude
            if self.instance.facilities:
                self.fields['facilities'].initial = self.instance.facilities

    def clean(self):
        """Validate and update location Point from lat/lon fields and facilities."""
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')

        # If lat/lon are provided, update the location Point field
        if latitude is not None and longitude is not None:
            try:
                cleaned_data['location'] = Point(longitude, latitude, srid=4326)
            except (ValueError, TypeError) as e:
                raise forms.ValidationError(
                    _('Invalid coordinates: %(error)s') % {'error': str(e)}
                )

        # Convert facilities from form (list of selected values) to JSONField format
        facilities = cleaned_data.get('facilities', [])
        cleaned_data['facilities'] = list(facilities) if facilities else []

        return cleaned_data


class LocationPhotoInline(admin.TabularInline):
    """Inline admin for location photos."""
    model = LocationPhoto
    extra = 1
    fields = ('image', 'caption', 'order')
    readonly_fields = ('uploaded_at',)


@admin.register(Location)
class LocationAdmin(gis_admin.GISModelAdmin, TranslationAdmin):
    """
    Admin interface for Location model with moderation features.
    """
    form = LocationAdminForm

    # Configure the map widget with OpenStreetMap tiles
    gis_widget_kwargs = {
        'attrs': {
            'default_lon': 25.0,
            'default_lat': 59.0,
            'default_zoom': 7,
        },
    }

    # Use custom OpenLayers template with OpenStreetMap tiles
    map_template = 'gis/openlayers.html'
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'

    list_display = (
        'name',
        'location_type',
        'is_approved_badge',
        'submitted_by_name',
        'created_at',
    )

    list_filter = (
        'is_approved',
        'location_type',
        'is_free',
        'created_at',
    )

    search_fields = (
        'name',
        'description',
        'address',
        'submitted_by_name',
        'submitted_by_email',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
        'submitted_by_name',
        'submitted_by_email',
        'location_map',
    )

    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'name',
                'description',
                'location_type',
            )
        }),
        (_('Location'), {
            'fields': (
                'location',
                'latitude',
                'longitude',
                'address',
                'access_instructions',
                'location_map',
            ),
            'description': _('You can either use the map to set coordinates, or manually enter latitude and longitude below.')
        }),
        (_('Facilities'), {
            'fields': (
                'facilities',
                'is_free',
                'pricing_details',
            )
        }),
        (_('Contact Information'), {
            'fields': (
                'website',
                'email',
                'phone',
            ),
            'classes': ('collapse',)
        }),
        (_('Moderation'), {
            'fields': (
                'is_approved',
                'moderation_notes',
                'submitted_by_name',
                'submitted_by_email',
            )
        }),
        (_('Timestamps'), {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    inlines = [LocationPhotoInline]

    actions = ['approve_locations', 'reject_locations']

    def is_approved_badge(self, obj):
        """Display approval status as colored badge."""
        if obj.is_approved:
            return format_html(
                '<span style="color: {}; font-weight: bold;">✓ Approved</span>',
                'green'
            )
        return format_html(
            '<span style="color: {}; font-weight: bold;">⧗ Pending</span>',
            'orange'
        )
    is_approved_badge.short_description = _('Status')

    def location_map(self, obj):
        """Display a small preview of the location on the map."""
        if obj.location:
            return format_html(
                '<a href="https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=15/{lat}/{lon}" '
                'target="_blank">View on OpenStreetMap</a>',
                lat=obj.latitude,
                lon=obj.longitude
            )
        return '-'
    location_map.short_description = _('Map preview')

    def approve_locations(self, request, queryset):
        """Bulk action to approve selected locations."""
        location_ids = list(queryset.values_list('pk', flat=True))
        updated = bulk_approve_locations(location_ids)
        self.message_user(
            request,
            _('%(count)d location(s) have been approved.') % {'count': updated}
        )
    approve_locations.short_description = _('Approve selected locations')

    def reject_locations(self, request, queryset):
        """Bulk action to reject (un-approve) selected locations."""
        location_ids = list(queryset.values_list('pk', flat=True))
        updated = bulk_reject_locations(location_ids)
        self.message_user(
            request,
            _('%(count)d location(s) have been rejected.') % {'count': updated}
        )
    reject_locations.short_description = _('Reject selected locations')


@admin.register(LocationPhoto)
class LocationPhotoAdmin(admin.ModelAdmin):
    """Admin interface for LocationPhoto model."""

    list_display = ('location', 'caption', 'order', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('location__name', 'caption')
    readonly_fields = ('uploaded_at',)

    fieldsets = (
        (None, {
            'fields': ('location', 'image', 'caption', 'order')
        }),
        (_('Metadata'), {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )
