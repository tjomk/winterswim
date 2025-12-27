"""
Business logic for search functionality.

Pure functions for search-related validation and transformation.
"""

from typing import Optional, Dict


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate geographic coordinates.

    Args:
        latitude: Latitude value
        longitude: Longitude value

    Returns:
        True if valid, False otherwise
    """
    return -90 <= latitude <= 90 and -180 <= longitude <= 180


def normalize_search_query(query: str) -> Optional[str]:
    """
    Normalize search query string.

    Args:
        query: Raw search query

    Returns:
        Normalized query string or None if too short
    """
    normalized = query.strip()
    return normalized if len(normalized) >= 3 else None


def clamp_radius(radius_km: float, min_km: float = 1, max_km: float = 500) -> float:
    """
    Clamp radius to valid range.

    Args:
        radius_km: Requested radius
        min_km: Minimum allowed radius
        max_km: Maximum allowed radius

    Returns:
        Clamped radius value
    """
    return max(min_km, min(radius_km, max_km))


def parse_proximity_params(
    lat_str: Optional[str],
    lon_str: Optional[str],
    radius_str: Optional[str] = '50'
) -> Optional[Dict[str, float]]:
    """
    Parse and validate proximity filter parameters from request.

    Args:
        lat_str: Latitude string
        lon_str: Longitude string
        radius_str: Radius string (default: '50')

    Returns:
        Dictionary with float values or None if invalid
    """
    if not (lat_str and lon_str):
        return None

    try:
        lat = float(lat_str)
        lon = float(lon_str)
        radius = float(radius_str)

        if not validate_coordinates(lat, lon):
            return None

        radius = clamp_radius(radius)

        return {
            'latitude': lat,
            'longitude': lon,
            'radius_km': radius,
        }
    except (ValueError, TypeError):
        return None
