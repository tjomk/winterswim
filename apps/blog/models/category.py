"""
Category model for blog articles.
"""

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """
    Blog article category - independent per language.

    NOT using modeltranslation - categories are created separately
    per language for maximum flexibility.
    """

    # Basic information
    name = models.CharField(
        max_length=100,
        verbose_name=_('Name'),
        help_text=_('Category name')
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        verbose_name=_('Slug'),
        help_text=_('URL slug (auto-generated)'),
        blank=True
    )

    description = models.TextField(
        verbose_name=_('Description'),
        help_text=_('Category description for SEO'),
        blank=True
    )

    # Language association
    language = models.CharField(
        max_length=2,
        choices=[('en', 'English'), ('fi', 'Finnish'), ('et', 'Estonian')],
        default='en',
        verbose_name=_('Language'),
        help_text=_('Language for this category')
    )

    # Display order
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Display order'),
        help_text=_('Lower numbers appear first')
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['language', 'order', 'name']
        indexes = [
            models.Index(fields=['language', 'slug']),
            models.Index(fields=['language', 'order']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['language', 'slug'],
                name='unique_category_slug_per_language'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.language})"

    def save(self, *args, **kwargs):
        """Generate slug if not exists."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
