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


def get_locations_by_city(country_slug: str, city_slug: str, approved_only: bool = True) -> QuerySet:
    """
    Get all locations in a specific city.

    Used by: CityDetailView

    Args:
        country_slug: Country slug
        city_slug: City slug
        approved_only: Whether to filter for approved locations (default: True)

    Returns:
        QuerySet of Location objects in the specified city
    """
    qs = Location.objects.filter(
        country_slug=country_slug,
        city_slug=city_slug
    ).exclude(
        city_slug=''
    ).order_by('name')

    if approved_only:
        qs = qs.filter(is_approved=True)

    return qs


def get_locations_by_country(country_slug: str, approved_only: bool = True) -> QuerySet:
    """
    Get all locations in a specific country.

    Used by: CountryDetailView

    Args:
        country_slug: Country slug
        approved_only: Whether to filter for approved locations (default: True)

    Returns:
        QuerySet of Location objects in the specified country
    """
    qs = Location.objects.filter(
        country_slug=country_slug
    ).exclude(
        country_slug=''
    ).order_by('city', 'name')

    if approved_only:
        qs = qs.filter(is_approved=True)

    return qs


def get_cities_by_country(country_slug: str) -> List[Dict[str, Any]]:
    """
    Get list of cities in a country with location counts.

    Used by: CountryDetailView

    Args:
        country_slug: Country slug

    Returns:
        List of dictionaries with city info:
        [{'city': 'Tallinn', 'city_slug': 'tallinn', 'country': 'Estonia', 'country_slug': 'estonia', 'count': 15}, ...]

    Query optimizations:
        - Database-level aggregation using values() + annotate()
        - Excludes locations without city data
    """
    cities = Location.objects.filter(
        country_slug=country_slug,
        is_approved=True
    ).exclude(
        city_slug=''
    ).values(
        'city', 'city_slug', 'country', 'country_slug'
    ).annotate(
        count=Count('id')
    ).order_by('city')

    return list(cities)


def get_all_countries() -> List[Dict[str, Any]]:
    """
    Get list of all countries with city and location counts.

    Used by: CountryListView (optional)

    Returns:
        List of dictionaries with country info:
        [{'country': 'Estonia', 'country_slug': 'estonia', 'city_count': 5, 'location_count': 25}, ...]

    Query optimizations:
        - Uses database-level aggregation
        - Efficient counting via subqueries
    """
    from django.db.models import Count, Q

    countries = Location.objects.filter(
        is_approved=True
    ).exclude(
        country_slug=''
    ).values(
        'country', 'country_slug'
    ).annotate(
        location_count=Count('id'),
        city_count=Count('city_slug', distinct=True, filter=Q(city_slug__gt=''))
    ).order_by('country')

    return list(countries)


def get_city_bounds(country_slug: str, city_slug: str) -> Optional[tuple]:
    """
    Get geographic bounds (bbox) for all locations in a city.

    Used by: CityDetailView (for centering the map)

    Args:
        country_slug: Country slug
        city_slug: City slug

    Returns:
        Tuple of (min_lon, min_lat, max_lon, max_lat) or None if no locations

    Query optimizations:
        - Uses PostGIS Extent aggregation for efficient bounds calculation
    """
    from django.contrib.gis.db.models import Extent

    extent = Location.objects.filter(
        country_slug=country_slug,
        city_slug=city_slug,
        is_approved=True
    ).exclude(
        city_slug=''
    ).aggregate(
        extent=Extent('location')
    )

    return extent['extent']  # Returns (min_lon, min_lat, max_lon, max_lat) or None
