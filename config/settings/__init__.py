"""
Settings package initialization.
Loads appropriate settings based on DJANGO_SETTINGS_MODULE environment variable.
"""

import os

# Default to development settings
env = os.environ.get('DJANGO_ENV', 'development')

if env == 'production':
    from .production import *
else:
    from .development import *
