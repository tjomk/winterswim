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
        "Disallow: /i18n/",
        "",
        "# Sitemap location",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]

    return HttpResponse("\n".join(lines), content_type="text/plain")
