"""
Django app configuration for blog.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BlogConfig(AppConfig):
    """Configuration for blog app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.blog'
    verbose_name = _('Blog')
