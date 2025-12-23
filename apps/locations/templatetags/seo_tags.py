"""
Template tags for SEO structured data (Schema.org JSON-LD).
"""

import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def location_schema(context, location):
    """
    Generate Schema.org JSON-LD structured data for a location.

    Uses Place schema with LocalBusiness or SportsActivityLocation properties.
    """
    request = context['request']

    # Base schema structure
    schema = {
        "@context": "https://schema.org",
        "@type": "Place",
        "name": location.name,
        "description": location.description,
        "url": request.build_absolute_uri(),
    }

    # Add address if available
    if location.address:
        schema["address"] = {
            "@type": "PostalAddress",
            "streetAddress": location.address,
        }

    # Add geographic coordinates
    if location.location:
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": location.latitude,
            "longitude": location.longitude,
        }

    # Add image if available
    if location.photos.exists():
        first_photo = location.photos.first()
        schema["image"] = request.build_absolute_uri(first_photo.image.url)

    # Add contact information
    if location.website:
        schema["url"] = location.website

    if location.phone or location.email:
        schema["contactPoint"] = {
            "@type": "ContactPoint",
            "contactType": "customer service",
        }
        if location.phone:
            schema["contactPoint"]["telephone"] = location.phone
        if location.email:
            schema["contactPoint"]["email"] = location.email

    # Add pricing information
    if location.is_free:
        schema["isAccessibleForFree"] = True
    elif location.pricing_details:
        schema["isAccessibleForFree"] = False

    # Add amenity features (facilities)
    if location.facilities:
        amenities = []
        for facility in location.facilities:
            amenities.append({
                "@type": "LocationFeatureSpecification",
                "name": facility,
            })
        schema["amenityFeature"] = amenities

    # Convert to JSON and mark as safe for template rendering
    json_ld = json.dumps(schema, ensure_ascii=False, indent=2)
    return mark_safe(f'<script type="application/ld+json">\n{json_ld}\n</script>')


@register.simple_tag(takes_context=True)
def website_schema(context):
    """
    Generate Schema.org JSON-LD for the website.

    Used on the home page to provide site-wide structured data.
    """
    request = context['request']

    schema = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "Winter Swimming Locations",
        "url": f"{request.scheme}://{request.get_host()}/",
        "description": "Discover winter swimming locations around the world. Find wild spots, commercial facilities, swimming clubs, and public facilities for cold water swimming.",
        "inLanguage": ["en", "fi", "et"],
    }

    json_ld = json.dumps(schema, ensure_ascii=False, indent=2)
    return mark_safe(f'<script type="application/ld+json">\n{json_ld}\n</script>')


@register.simple_tag(takes_context=True)
def organization_schema(context):
    """
    Generate Schema.org JSON-LD for the organization.

    Used for branding and identity in search results.
    """
    request = context['request']

    schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Winter Swimming Locations",
        "url": f"{request.scheme}://{request.get_host()}/",
        "description": "A community-driven platform for discovering and sharing winter swimming locations worldwide.",
        "logo": f"{request.scheme}://{request.get_host()}/static/images/logo.png",
    }

    json_ld = json.dumps(schema, ensure_ascii=False, indent=2)
    return mark_safe(f'<script type="application/ld+json">\n{json_ld}\n</script>')


@register.simple_tag(takes_context=True)
def breadcrumb_schema(context, breadcrumbs):
    """
    Generate Schema.org BreadcrumbList JSON-LD markup.

    Args:
        breadcrumbs: List of tuples [(name, url), ...] representing the breadcrumb trail

    Returns:
        JSON-LD script tag with BreadcrumbList structured data
    """
    request = context['request']

    # Build the itemListElement array
    items = []
    for position, (name, url) in enumerate(breadcrumbs, start=1):
        # Build absolute URL
        if url:
            absolute_url = request.build_absolute_uri(url)
        else:
            # Current page (last item) - use current URL
            absolute_url = request.build_absolute_uri()

        items.append({
            "@type": "ListItem",
            "position": position,
            "name": name,
            "item": absolute_url if url else absolute_url  # Last item may not have link
        })

    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items
    }

    json_ld = json.dumps(schema, ensure_ascii=False, indent=2)
    return mark_safe(f'<script type="application/ld+json">\n{json_ld}\n</script>')
