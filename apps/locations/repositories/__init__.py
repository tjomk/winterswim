"""
Data access layer for locations (Repository Pattern).

Pure functions for database queries, following the Functional Core pattern.
"""

from .location_repository import (
    get_approved_locations,
    get_location_by_slug,
    get_nearby_locations,
    get_random_locations,
    create_location,
    bulk_approve_locations,
    bulk_reject_locations,
    get_locations_for_sitemap,
    get_locations_grouped_by_type,
    get_locations_count_by_type,
    filter_locations_by_type,
    get_locations_by_city,
    get_locations_by_country,
    get_cities_by_country,
    get_all_countries,
    get_city_bounds,
)

from .search_repository import (
    search_locations,
    get_locations_with_proximity,
    combine_search_and_proximity,
)

__all__ = [
    # Basic queries
    'get_approved_locations',
    'get_location_by_slug',
    'get_nearby_locations',
    'get_random_locations',
    'create_location',
    'bulk_approve_locations',
    'bulk_reject_locations',
    'get_locations_for_sitemap',
    'get_locations_grouped_by_type',
    'get_locations_count_by_type',
    'filter_locations_by_type',

    # City/Country queries
    'get_locations_by_city',
    'get_locations_by_country',
    'get_cities_by_country',
    'get_all_countries',
    'get_city_bounds',

    # Search queries
    'search_locations',
    'get_locations_with_proximity',
    'combine_search_and_proximity',
]
