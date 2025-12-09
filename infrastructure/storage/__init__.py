"""
Infrastructure layer for storage backends.
"""

from .backends import get_photo_storage

__all__ = ['get_photo_storage']
