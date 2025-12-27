"""
Core repository functions for Location model.

Pure functions that encapsulate database queries.
All functions return QuerySets or model instances.
"""

from typing import Optional, Dict, List, Any
from django.db.models import QuerySet, Count
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point

from apps.locations.models import Location


def get_approved_locations() -> QuerySet:
    """
    Get all approved locations.

    Used by: map_view, LocationListView (base), locations_api_view

    Returns:
        QuerySet of approved Location objects
    """
    return Location.objects.filter(is_approved=True)


def get_location_by_slug(slug: str, approved_only: bool = True) -> QuerySet:
    """
    Get location queryset filtered by slug.

    Used by: LocationDetailView

    Args:
        slug: Location slug
        approved_only: Whether to filter for approved locations only

    Returns:
        QuerySet filtered by slug and approval status
    """
    qs = Location.objects.all()
    if approved_only:
        qs = qs.filter(is_approved=True)
    return qs.filter(slug=slug)


def get_nearby_locations(
    reference_point: Point,
    radius_km: float = 50,
    exclude_pk: Optional[int] = None,
    limit: int = 5,
    approved_only: bool = True
) -> QuerySet:
    """
    Get locations within radius of a reference point.

    Used by: LocationDetailView (nearby locations)

    Args:
        reference_point: PostGIS Point to measure distance from
        radius_km: Maximum distance in kilometers (default: 50)
        exclude_pk: Optional primary key to exclude (e.g., current location)
        limit: Maximum number of results (default: 5)
        approved_only: Whether to filter for approved locations (default: True)

    Returns:
        QuerySet of nearby Location objects, ordered by distance

    Query optimizations:
        - Uses PostGIS distance_lte for efficient spatial filtering
        - Limits results in database, not Python
    """
    from django.contrib.gis.db.models.functions import Distance

    qs = Location.objects.filter(
        location__distance_lte=(reference_point, D(km=radius_km))
    ).annotate(
        distance=Distance('location', reference_point)
    ).order_by('distance')

    if approved_only:
        qs = qs.filter(is_approved=True)

    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)

    return qs[:limit]


def create_location(data: Dict[str, Any]) -> Location:
    """
    Create a new location.

    Used by: location_submit_view

    Args:
        data: Dictionary containing location data (already processed by service layer)

    Returns:
        Created Location instance
    """
    return Location.objects.create(**data)


def bulk_approve_locations(location_ids: List[int]) -> int:
    """
    Bulk approve locations by IDs.

    Used by: admin.py approve_locations action

    Args:
        location_ids: List of location primary keys

    Returns:
        Number of locations updated
    """
    return Location.objects.filter(pk__in=location_ids).update(is_approved=True)


def bulk_reject_locations(location_ids: List[int]) -> int:
    """
    Bulk reject (un-approve) locations by IDs.

    Used by: admin.py reject_locations action

    Args:
        location_ids: List of location primary keys

    Returns:
        Number of locations updated
    """
    return Location.objects.filter(pk__in=location_ids).update(is_approved=False)


def get_locations_for_sitemap() -> QuerySet:
    """
    Get locations for XML sitemap generation.

    Used by: sitemaps.py LocationSitemap

    Returns:
        QuerySet of approved locations ordered by update time

    Query optimizations:
        - Only fetches fields needed for sitemap (id, slug, updated_at)
        - Orders by updated_at for efficient pagination
    """
    return Location.objects.filter(
        is_approved=True
    ).only(
        'id', 'slug', 'updated_at'
    ).order_by('-updated_at')


def get_locations_grouped_by_type() -> Dict[str, List[Location]]:
    """
    Get all approved locations grouped by type.

    Used by: sitemap_page_view

    Returns:
        Dictionary mapping type display names to lists of Location objects

    Query optimizations:
        - Fetches all data in single query
        - Orders for efficient grouping
    """
    from collections import defaultdict

    # Get all approved locations ordered by name
    locations = Location.objects.filter(
        is_approved=True
    ).order_by('location_type', 'name')

    # Group by type
    grouped = defaultdict(list)
    for location in locations:
        type_display = location.get_location_type_display()
        grouped[type_display].append(location)

    return dict(grouped)


def get_locations_count_by_type() -> Dict[str, int]:
    """
    Get count of locations per type.

    Used by: sitemap_page_view (for statistics)

    Returns:
        Dictionary mapping location_type display name to count

    Query optimizations:
        - Database-level aggregation instead of Python counting
        - Single efficient query using values() + annotate()
    """
    counts = Location.objects.filter(
        is_approved=True
    ).values('location_type').annotate(
        count=Count('id')
    )

    # Convert to dict with display names
    result = {}
    for item in counts:
        type_value = item['location_type']
        # Get display name from choices
        type_display = dict(Location._meta.get_field('location_type').choices)[type_value]
        result[type_display] = item['count']

    return result


def filter_locations_by_type(
    queryset: Optional[QuerySet] = None,
    location_type: Optional[str] = None
) -> QuerySet:
    """
    Filter locations by type.

    Used by: LocationListView, locations_api_view

    Args:
        queryset: Base queryset to filter (defaults to all approved)
        location_type: Type to filter by (optional)

    Returns:
        Filtered QuerySet
    """
    if queryset is None:
        queryset = get_approved_locations()

    if location_type:
        queryset = queryset.filter(location_type=location_type)

    return queryset


def get_random_locations(limit: int = 20, approved_only: bool = True) -> QuerySet:
    """
    Get random approved locations.

    Used by: locations_api_view (landing page fallback when no user location)

    Args:
        limit: Maximum number of results (default: 20)
        approved_only: Whether to filter for approved locations (default: True)

    Returns:
        QuerySet of random Location objects

    Query optimizations:
        - Uses database-level random ordering
        - Limits results in database, not Python
    """
    qs = Location.objects.all()

    if approved_only:
        qs = qs.filter(is_approved=True)

    return qs.order_by('?')[:limit]
