from django import template

register = template.Library()


@register.filter
def is_multiple_checkbox(field):
    """Check if the field widget is CheckboxSelectMultiple or RadioSelect"""
    widget_name = field.field.widget.__class__.__name__
    return widget_name in ['CheckboxSelectMultiple', 'RadioSelect']
