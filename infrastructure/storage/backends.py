"""
Abstract storage backend for flexible image storage.

This module provides an abstraction layer for image storage,
making it easy to switch between local storage and cloud storage (S3, etc.)
or add image processing middleware in the future.
"""

from django.core.files.storage import FileSystemStorage
from django.conf import settings


class AbstractPhotoStorage:
    """
    Abstract base for photo storage.

    Future extensions:
    - Add image processing (resize, compress, format conversion)
    - Switch to cloud storage (S3, Cloudinary, etc.)
    - Add CDN integration
    - Implement lazy loading strategies
    """

    def __init__(self):
        self._storage = self._get_storage_backend()

    def _get_storage_backend(self):
        """
        Get the configured storage backend.

        Override this method to switch to different storage backends.
        """
        # For now, use Django's default FileSystemStorage
        # Later, this can be switched to S3Storage, CloudinaryStorage, etc.
        return FileSystemStorage(
            location=settings.MEDIA_ROOT,
            base_url=settings.MEDIA_URL
        )

    def save(self, name, content, max_length=None):
        """Save a file."""
        return self._storage.save(name, content, max_length=max_length)

    def delete(self, name):
        """Delete a file."""
        return self._storage.delete(name)

    def exists(self, name):
        """Check if file exists."""
        return self._storage.exists(name)

    def url(self, name):
        """Get URL for a file."""
        return self._storage.url(name)

    def size(self, name):
        """Get file size."""
        return self._storage.size(name)


# Factory function to get photo storage instance
def get_photo_storage():
    """
    Factory function to get photo storage instance.

    This allows easy switching of storage backends via settings.
    """
    # In the future, this can check settings to determine which storage to use
    # storage_type = getattr(settings, 'PHOTO_STORAGE_TYPE', 'local')
    # if storage_type == 's3':
    #     return S3PhotoStorage()
    # elif storage_type == 'cloudinary':
    #     return CloudinaryPhotoStorage()
    # else:
    #     return LocalPhotoStorage()

    return AbstractPhotoStorage()._storage
