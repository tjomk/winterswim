"""
Views for location management (Imperative Shell).
"""

from .location_views import (
    map_view,
    LocationListView,
    LocationDetailView,
    location_submit_view,
    submit_success_view,
    locations_api_view,
)

__all__ = [
    'map_view',
    'LocationListView',
    'LocationDetailView',
    'location_submit_view',
    'submit_success_view',
    'locations_api_view',
]
