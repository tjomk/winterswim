"""
SEO template tags for blog articles.

Provides Schema.org structured data for articles.
"""

from django import template
import json
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def article_schema(context, article):
    """
    Generate Schema.org Article JSON-LD.

    Args:
        context: Template context
        article: Article instance

    Returns:
        Safe HTML script tag with JSON-LD

    Usage:
        {% load blog_seo_tags %}
        {% article_schema article %}
    """
    request = context['request']

    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article.title,
        "description": article.excerpt or article.meta_description,
        "author": {
            "@type": "Person",
            "name": article.author_name
        },
        "datePublished": article.published_at.isoformat() if article.published_at else None,
        "dateModified": article.updated_at.isoformat(),
        "publisher": {
            "@type": "Organization",
            "name": "Winter Swimming Locations",
            "logo": {
                "@type": "ImageObject",
                "url": f"{request.scheme}://{request.get_host()}/static/images/logo.png"
            }
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": request.build_absolute_uri()
        }
    }

    # Add featured image
    if article.featured_image:
        schema["image"] = {
            "@type": "ImageObject",
            "url": request.build_absolute_uri(article.featured_image.url),
            "caption": article.featured_image_alt or article.title
        }

    # Add reading time
    if article.reading_time_minutes:
        schema["timeRequired"] = f"PT{article.reading_time_minutes}M"

    json_ld = json.dumps(schema, ensure_ascii=False, indent=2)
    return mark_safe(f'<script type="application/ld+json">\n{json_ld}\n</script>')
