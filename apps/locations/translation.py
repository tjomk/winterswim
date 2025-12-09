"""
Translation configuration for Location models.

Registers translatable fields for django-modeltranslation.
"""

from modeltranslation.translator import translator, TranslationOptions
from .models import Location


class LocationTranslationOptions(TranslationOptions):
    """
    Define which fields should be translatable for Location model.
    """
    fields = ('name', 'description', 'access_instructions', 'pricing_details')
    required_languages = ('en',)  # English is required


translator.register(Location, LocationTranslationOptions)
