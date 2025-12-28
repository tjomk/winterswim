"""
Sitemaps for blog articles and categories.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.blog.repositories import get_articles_for_sitemap
from apps.blog.models import Category


class ArticleSitemap(Sitemap):
    """Sitemap for blog articles."""

    changefreq = "monthly"
    priority = 0.7

    def items(self):
        """Return all published articles."""
        return get_articles_for_sitemap()

    def lastmod(self, obj):
        """Return last modification date."""
        return obj.updated_at

    def location(self, obj):
        """Return article URL."""
        return reverse('blog:detail', kwargs={
            'category_slug': obj.category.slug,
            'article_slug': obj.slug
        })


class CategorySitemap(Sitemap):
    """Sitemap for blog categories."""

    changefreq = "weekly"
    priority = 0.6

    def items(self):
        """Return all categories for all languages."""
        return Category.objects.all()

    def location(self, obj):
        """Return category URL."""
        return reverse('blog:category', kwargs={
            'category_slug': obj.slug
        })
