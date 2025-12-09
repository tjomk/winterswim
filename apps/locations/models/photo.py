"""
Domain model for location photos.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from infrastructure.storage.backends import get_photo_storage


class LocationPhoto(models.Model):
    """
    Represents a photo of a swimming location.

    Uses abstract storage backend for flexibility.
    """

    location = models.ForeignKey(
        'locations.Location',
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name=_('Location')
    )

    image = models.ImageField(
        upload_to='location_photos/%Y/%m/',
        storage=get_photo_storage,
        verbose_name=_('Image')
    )

    caption = models.CharField(
        max_length=200,
        verbose_name=_('Caption'),
        help_text=_('Optional caption for the photo'),
        blank=True
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Display order'),
        help_text=_('Order in which photos are displayed')
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Uploaded at')
    )

    class Meta:
        verbose_name = _('Location photo')
        verbose_name_plural = _('Location photos')
        ordering = ['order', '-uploaded_at']
        indexes = [
            models.Index(fields=['location', 'order']),
        ]

    def __str__(self):
        return f"Photo for {self.location.name}"
