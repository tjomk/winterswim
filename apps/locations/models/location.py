"""
Domain model for winter swimming locations.
"""

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _


class LocationType(models.TextChoices):
    """Types of swimming locations."""
    WILD = 'wild', _('Wild spot')
    COMMERCIAL = 'commercial', _('Commercial facility')
    CLUB = 'club', _('Swimming club')
    PUBLIC = 'public', _('Public facility')


class Facility(models.TextChoices):
    """Available facilities at locations."""
    SAUNA = 'sauna', _('Sauna')
    CHANGING_ROOM = 'changing_room', _('Changing room')
    SHOWER = 'shower', _('Shower')
    LOCKERS = 'lockers', _('Lockers')
    PARKING = 'parking', _('Parking')
    DISABLED_ACCESS = 'disabled_access', _('Disabled access')
    TOILET = 'toilet', _('Toilet')
    CAFE = 'cafe', _('Café')


class Location(models.Model):
    """
    Represents a winter swimming location.

    This is a domain entity - pure data with minimal behavior.
    Business logic should be in services layer.
    """

    # Basic information
    name = models.CharField(
        max_length=200,
        verbose_name=_('Name'),
        help_text=_('Name of the swimming location')
    )

    description = models.TextField(
        verbose_name=_('Description'),
        help_text=_('Detailed description of the location'),
        blank=True
    )

    # Geographic data
    location = models.PointField(
        verbose_name=_('Location'),
        help_text=_('Geographic coordinates'),
        srid=4326  # WGS84 coordinate system
    )

    address = models.CharField(
        max_length=500,
        verbose_name=_('Address'),
        help_text=_('Human-readable address'),
        blank=True
    )

    # Location details
    location_type = models.CharField(
        max_length=20,
        choices=LocationType.choices,
        default=LocationType.WILD,
        verbose_name=_('Location type')
    )

    facilities = models.JSONField(
        default=list,
        verbose_name=_('Facilities'),
        help_text=_('Available facilities (sauna, changing rooms, etc.)'),
        blank=True
    )

    access_instructions = models.TextField(
        verbose_name=_('Access instructions'),
        help_text=_('How to access this location'),
        blank=True
    )

    # Contact and web presence
    website = models.URLField(
        verbose_name=_('Website'),
        blank=True
    )

    email = models.EmailField(
        verbose_name=_('Email'),
        blank=True
    )

    phone = models.CharField(
        max_length=50,
        verbose_name=_('Phone'),
        blank=True
    )

    # Pricing
    is_free = models.BooleanField(
        default=True,
        verbose_name=_('Free access'),
        help_text=_('Whether access is free')
    )

    pricing_details = models.TextField(
        verbose_name=_('Pricing details'),
        help_text=_('Details about pricing if not free'),
        blank=True
    )

    # Moderation
    is_approved = models.BooleanField(
        default=False,
        verbose_name=_('Approved'),
        help_text=_('Whether this location has been approved by moderators')
    )

    submitted_by_name = models.CharField(
        max_length=200,
        verbose_name=_('Submitted by'),
        help_text=_('Name of person who submitted this location'),
        blank=True
    )

    submitted_by_email = models.EmailField(
        verbose_name=_('Submitter email'),
        help_text=_('Email of person who submitted (for follow-up)'),
        blank=True
    )

    moderation_notes = models.TextField(
        verbose_name=_('Moderation notes'),
        help_text=_('Internal notes for moderators'),
        blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    class Meta:
        verbose_name = _('Location')
        verbose_name_plural = _('Locations')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_approved', '-created_at']),
            models.Index(fields=['location_type']),
        ]

    def __str__(self):
        return self.name

    @property
    def latitude(self):
        """Get latitude from Point field."""
        return self.location.y if self.location else None

    @property
    def longitude(self):
        """Get longitude from Point field."""
        return self.location.x if self.location else None
