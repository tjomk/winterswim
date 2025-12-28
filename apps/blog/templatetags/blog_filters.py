"""
Custom template filters for blog app.
"""

from django import template

register = template.Library()


@register.filter(name='split')
def split(value, arg):
    """
    Split a string by a delimiter.

    Usage: {{ "a,b,c"|split:"," }}
    """
    if value:
        return value.split(arg)
    return []


@register.filter(name='strip')
def strip(value):
    """
    Remove leading and trailing whitespace from a string.

    Usage: {{ "  hello  "|strip }}
    """
    if value:
        return value.strip()
    return value
