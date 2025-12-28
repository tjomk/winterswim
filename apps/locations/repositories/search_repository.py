"""
Search repository functions for Location model.

Handles complex search logic including full-text search and proximity filtering.
"""

from typing import Optional, Tuple
from django.db.models import QuerySet
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from apps.locations.models import Location


def search_locations(
    query: str,
    language: str = 'en',
    base_queryset: Optional[QuerySet] = None
) -> QuerySet:
    """
    Search locations using icontains on translated fields.

    Used by: LocationListView

    Args:
        query: Search query string
        language: Language code ('en', 'fi', 'et')
        base_queryset: Optional base queryset to search within

    Returns:
        QuerySet of matching locations ordered by created_at

    Query optimizations:
        - Searches across name, description, address, city, and country fields
        - Uses language-specific translated fields
        - Case-insensitive search
    """
    from django.db.models import Q

    if base_queryset is None:
        base_queryset = Location.objects.filter(is_approved=True)

    # Build language-specific field names
    name_field = f'name_{language}' if language != 'en' else 'name'
    description_field = f'description_{language}' if language != 'en' else 'description'
    city_field = f'city_{language}' if language != 'en' else 'city'
    country_field = f'country_{language}' if language != 'en' else 'country'

    # Search across all relevant fields
    search_filter = (
        Q(**{f'{name_field}__icontains': query}) |
        Q(**{f'description_{language}__icontains': query}) |
        Q(address__icontains=query) |
        Q(**{f'{city_field}__icontains': query}) |
        Q(**{f'{country_field}__icontains': query})
    )

    return base_queryset.filter(search_filter).order_by('-created_at')


def get_locations_with_proximity(
    latitude: float,
    longitude: float,
    radius_km: float = 50,
    base_queryset: Optional[QuerySet] = None
) -> Tuple[QuerySet, Point]:
    """
    Get locations within radius of coordinates, ordered by distance.

    Used by: LocationListView (proximity filter)

    Args:
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)
        radius_km: Maximum distance in kilometers (1-500)
        base_queryset: Optional base queryset to filter

    Returns:
        Tuple of (QuerySet with distance annotation, user_point)

    Query optimizations:
        - PostGIS distance_lte for spatial filtering
        - Distance annotation for sorting
        - Index-backed spatial queries

    Raises:
        ValueError: If coordinates are invalid
    """
    # Validate coordinates
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise ValueError("Invalid coordinates")

    # Clamp radius to prevent abuse
    radius_km = max(1, min(radius_km, 500))

    # Create point (PostGIS uses lon, lat order)
    user_point = Point(longitude, latitude, srid=4326)

    if base_queryset is None:
        base_queryset = Location.objects.filter(is_approved=True)

    # Filter by distance and annotate
    queryset = base_queryset.filter(
        location__distance_lte=(user_point, D(km=radius_km))
    ).annotate(
        distance=Distance('location', user_point)
    ).order_by('distance')

    return queryset, user_point


def combine_search_and_proximity(
    search_query: Optional[str] = None,
    language: str = 'en',
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: float = 50,
    location_type: Optional[str] = None
) -> QuerySet:
    """
    Combine search, proximity, and type filters.

    Used by: LocationListView (when multiple filters are active)

    Args:
        search_query: Optional search query string
        language: Language code for search
        latitude: Optional latitude for proximity filter
        longitude: Optional longitude for proximity filter
        radius_km: Radius in kilometers
        location_type: Optional type filter

    Returns:
        QuerySet with all filters applied and appropriate ordering

    Query optimizations:
        - Chains filters efficiently
        - Applies ordering based on active filters
    """
    from apps.locations.repositories.location_repository import filter_locations_by_type

    # Start with approved locations
    queryset = Location.objects.filter(is_approved=True)

    # Apply type filter
    if location_type:
        queryset = filter_locations_by_type(queryset, location_type)

    # Apply search filter
    if search_query and len(search_query) >= 3:
        queryset = search_locations(search_query, language, queryset)
        # Search applies its own ordering
        return queryset

    # Apply proximity filter
    if latitude is not None and longitude is not None:
        try:
            queryset, _ = get_locations_with_proximity(
                latitude, longitude, radius_km, queryset
            )
            # Proximity applies its own ordering
            return queryset
        except ValueError:
            # Invalid coordinates - continue with default ordering
            pass

    # Default ordering
    return queryset.order_by('-created_at')
