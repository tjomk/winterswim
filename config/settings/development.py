"""
Development settings for winterswim project.
"""

from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '192.168.8.10']

# Development-specific installed apps
INSTALLED_APPS += [
    # Add django-debug-toolbar or other dev tools here when needed
]

# Email backend for development (console output)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
