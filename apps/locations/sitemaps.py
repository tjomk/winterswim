"""
Sitemap configuration for SEO optimization.

Generates XML sitemaps for locations and static pages to help search engines
discover and index all pages on the site.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.locations.repositories import get_locations_for_sitemap


class LocationSitemap(Sitemap):
    """
    Sitemap for location detail pages.

    Includes all approved locations with their last modification date.
    """
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        """Return all approved locations."""
        return get_locations_for_sitemap()

    def lastmod(self, obj):
        """Return the last modification date of the location."""
        return obj.updated_at

    def location(self, obj):
        """Return the URL for the location detail page."""
        # This will be wrapped with i18n URL patterns automatically
        return reverse('locations:detail', kwargs={'slug': obj.slug})


class StaticViewSitemap(Sitemap):
    """
    Sitemap for static pages (map, list, submit).
    """
    priority = 0.6
    changefreq = 'daily'

    def items(self):
        """Return list of static page names."""
        return ['locations:map', 'locations:list', 'locations:submit']

    def location(self, item):
        """Return the URL for the static page."""
        return reverse(item)
