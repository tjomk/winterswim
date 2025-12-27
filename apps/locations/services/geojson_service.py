"""
Business logic for GeoJSON serialization.

Pure functions for transforming location data to GeoJSON format.
"""

import json
from typing import Callable, Dict, Any


def enrich_geojson_with_urls(geojson_str: str, url_builder_fn: Callable[[str], str]) -> Dict[str, Any]:
    """
    Add detail URLs to GeoJSON features.

    Args:
        geojson_str: GeoJSON string
        url_builder_fn: Function to build URLs (slug) -> url

    Returns:
        GeoJSON dict with URLs added
    """
    data = json.loads(geojson_str)

    for feature in data['features']:
        slug = feature['properties']['slug']
        feature['properties']['detail_url'] = url_builder_fn(slug)

    return data
