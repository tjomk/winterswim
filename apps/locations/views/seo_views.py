"""
SEO-related views for robots.txt and other SEO functionality.
"""

from django.http import HttpResponse
from django.views.decorators.http import require_GET


@require_GET
def robots_txt(request):
    """
    Generate robots.txt file dynamically.

    Allows all user agents to crawl the site except admin areas.
    References the sitemap location for better indexing.
    """
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /i18n/",
        "",
        "# Sitemap location",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]

    return HttpResponse("\n".join(lines), content_type="text/plain")


@require_GET
def debug_headers(request):
    """Debug view to check request headers and scheme detection."""
    lines = [
        f"request.scheme: {request.scheme}",
        f"request.is_secure(): {request.is_secure()}",
        f"request.get_host(): {request.get_host()}",
        f"request.META.get('HTTP_X_FORWARDED_PROTO'): {request.META.get('HTTP_X_FORWARDED_PROTO')}",
        f"request.META.get('HTTP_X_FORWARDED_FOR'): {request.META.get('HTTP_X_FORWARDED_FOR')}",
        "",
        "All HTTP headers:",
        *[f"{k}: {v}" for k, v in request.META.items() if k.startswith('HTTP_')]
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
