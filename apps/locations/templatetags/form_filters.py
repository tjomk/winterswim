from django import template
from django.utils.translation import gettext_lazy as _

from apps.locations.models import Facility

register = template.Library()


@register.filter
def is_multiple_checkbox(field):
    """Check if the field widget is CheckboxSelectMultiple or RadioSelect"""
    widget_name = field.field.widget.__class__.__name__
    return widget_name in ['CheckboxSelectMultiple', 'RadioSelect']


@register.filter
def get_facility_label(value):
    """Convert a facility value to its translated label."""
    # Find the facility choice that matches the value
    for facility_value, facility_label in Facility.choices:
        if facility_value == value:
            return facility_label
    return value  # Return original value if not found
