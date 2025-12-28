"""
Translation configuration for Blog models.

Note: Articles are independent per language (not translations),
so we don't register Article model with modeltranslation.
The 'language' field on the model determines which language each article is in.
"""

# No translation registration needed for independent language articles
# This file exists for future extensibility if needed
