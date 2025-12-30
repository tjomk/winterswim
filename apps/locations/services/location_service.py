"""
Business logic for location management (Functional Core).

This module contains pure business logic for locations,
following the "Functional Core, Imperative Shell" pattern.
"""

from typing import Dict, List
from django.contrib.gis.geos import Point


def validate_location_data(data: Dict) -> Dict[str, List[str]]:
    """
    Validate location submission data.

    Args:
        data: Dictionary containing location data

    Returns:
        Dictionary of validation errors (empty if valid)
    """
    errors = {}

    # Required fields
    if not data.get('name', '').strip():
        errors['name'] = ['Name is required']

    if not data.get('description', '').strip():
        errors['description'] = ['Description is required']

    # Validate coordinates
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if latitude is None or longitude is None:
        errors['location'] = ['Location coordinates are required']
    else:
        try:
            lat = float(latitude)
            lon = float(longitude)

            if not (-90 <= lat <= 90):
                errors['latitude'] = ['Latitude must be between -90 and 90']

            if not (-180 <= lon <= 180):
                errors['longitude'] = ['Longitude must be between -180 and 180']
        except (ValueError, TypeError):
            errors['location'] = ['Invalid coordinates']

    # Validate email if provided
    submitted_by_email = data.get('submitted_by_email', '').strip()
    if submitted_by_email and '@' not in submitted_by_email:
        errors['submitted_by_email'] = ['Invalid email address']

    return errors


def create_point_from_coordinates(latitude: float, longitude: float) -> Point:
    """
    Create a PostGIS Point from latitude and longitude.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Returns:
        PostGIS Point object
    """
    return Point(float(longitude), float(latitude), srid=4326)


def parse_facilities(facilities_list: List[str]) -> List[str]:
    """
    Parse and validate facilities list.

    Args:
        facilities_list: List of facility identifiers

    Returns:
        Validated list of facilities
    """
    from apps.locations.models import Facility

    valid_facilities = [f.value for f in Facility]
    return [f for f in facilities_list if f in valid_facilities]


def prepare_location_data_for_save(data: Dict) -> Dict:
    """
    Prepare location data for database save.

    Transforms user input into database-ready format.
    Pure function - no side effects.

    Args:
        data: Raw form data

    Returns:
        Processed data ready for database
    """
    processed = {
        'name': data['name'].strip(),
        'description': data.get('description', '').strip(),
        'location': create_point_from_coordinates(
            float(data['latitude']),
            float(data['longitude'])
        ),
        'address': data.get('address', '').strip(),
        'location_type': data.get('location_type', 'wild'),
        'facilities': parse_facilities(data.get('facilities', [])),
        'access_instructions': data.get('access_instructions', '').strip(),
        'website': data.get('website', '').strip(),
        'email': data.get('email', '').strip(),
        'phone': data.get('phone', '').strip(),
        'is_free': data.get('is_free', True),
        'pricing_details': data.get('pricing_details', '').strip(),
        'submitted_by_name': data.get('submitted_by_name', '').strip(),
        'submitted_by_email': data.get('submitted_by_email', '').strip(),
        'is_approved': False,  # All submissions start as not approved
    }

    return processed
