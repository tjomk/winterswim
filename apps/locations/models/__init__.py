"""
Domain models for winter swimming locations.
"""

from .location import Location, LocationType, Facility
from .photo import LocationPhoto

__all__ = [
    'Location',
    'LocationType',
    'Facility',
    'LocationPhoto',
]
