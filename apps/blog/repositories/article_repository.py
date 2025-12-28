"""
Repository layer for Article and Category queries.

Pure functions that return QuerySets for use in views and services.
"""

from typing import Optional
from django.db.models import QuerySet, Q, F
from django.utils import timezone

from apps.blog.models import Article, Category, ArticleStatus


def get_published_articles(language: Optional[str] = None) -> QuerySet:
    """
    Get all published articles.

    Args:
        language: Filter by language code (optional)

    Returns:
        QuerySet of published Article objects

    Usage:
        Used by BlogListView to display all published articles.
    """
    qs = Article.objects.filter(
        status=ArticleStatus.PUBLISHED,
        published_at__lte=timezone.now()
    ).select_related('category')

    if language:
        qs = qs.filter(language=language)

    return qs


def get_articles_by_category(
    category_slug: str,
    language: str,
    published_only: bool = True
) -> QuerySet:
    """
    Get articles in a specific category.

    Args:
        category_slug: Category slug
        language: Language code
        published_only: Filter for published articles only

    Returns:
        QuerySet of Article objects

    Usage:
        Used by CategoryView to display articles in a category.
    """
    qs = Article.objects.filter(
        category__slug=category_slug,
        category__language=language
    ).select_related('category')

    if published_only:
        qs = qs.filter(
            status=ArticleStatus.PUBLISHED,
            published_at__lte=timezone.now()
        )

    return qs


def get_article_by_slug(
    article_slug: str,
    category_slug: str,
    language: str,
    published_only: bool = True
) -> QuerySet:
    """
    Get article by slug within a category.

    Args:
        article_slug: Article slug
        category_slug: Category slug
        language: Language code
        published_only: Filter for published only

    Returns:
        QuerySet filtered to single article

    Usage:
        Used by ArticleDetailView to display a single article.
    """
    qs = Article.objects.filter(
        slug=article_slug,
        category__slug=category_slug,
        language=language
    ).select_related('category')

    if published_only:
        qs = qs.filter(
            status=ArticleStatus.PUBLISHED,
            published_at__lte=timezone.now()
        )

    return qs


def get_related_articles(
    article: Article,
    limit: int = 3
) -> QuerySet:
    """
    Get related articles (same category, different article).

    Args:
        article: Reference article
        limit: Maximum number of results

    Returns:
        QuerySet of related Article objects

    Usage:
        Used by ArticleDetailView to show related articles.
    """
    return Article.objects.filter(
        category=article.category,
        language=article.language,
        status=ArticleStatus.PUBLISHED,
        published_at__lte=timezone.now()
    ).exclude(
        pk=article.pk
    ).order_by('-published_at')[:limit]


def get_recent_articles(language: str, limit: int = 5) -> QuerySet:
    """
    Get most recent published articles.

    Args:
        language: Language code
        limit: Maximum number of results

    Returns:
        QuerySet of recent Article objects

    Usage:
        Used for sidebar widgets or homepage recent articles.
    """
    return Article.objects.filter(
        language=language,
        status=ArticleStatus.PUBLISHED,
        published_at__lte=timezone.now()
    ).select_related('category').order_by('-published_at')[:limit]


def increment_view_count(article_id: int) -> int:
    """
    Increment article view count.

    Args:
        article_id: Article primary key

    Returns:
        Number of rows updated (1 if successful)

    Usage:
        Called by ArticleDetailView to track page views.
    """
    return Article.objects.filter(pk=article_id).update(
        view_count=F('view_count') + 1
    )


def get_categories_for_language(language: str) -> QuerySet:
    """
    Get all categories for a language.

    Args:
        language: Language code

    Returns:
        QuerySet of Category objects

    Usage:
        Used by views to display category navigation.
    """
    return Category.objects.filter(language=language).order_by('order', 'name')


def search_articles(
    query: str,
    language: str,
    published_only: bool = True
) -> QuerySet:
    """
    Search articles by title and content.

    Args:
        query: Search query string
        language: Language code
        published_only: Filter for published only

    Returns:
        QuerySet of matching Article objects

    Usage:
        Used by search view for full-text search.
    """
    qs = Article.objects.filter(
        language=language
    ).filter(
        Q(title__icontains=query) |
        Q(content__icontains=query) |
        Q(excerpt__icontains=query)
    ).select_related('category')

    if published_only:
        qs = qs.filter(
            status=ArticleStatus.PUBLISHED,
            published_at__lte=timezone.now()
        )

    return qs.order_by('-published_at')


def get_articles_for_sitemap() -> QuerySet:
    """
    Get articles for XML sitemap generation.

    Returns:
        QuerySet of published articles for sitemap

    Usage:
        Used by ArticleSitemap to generate sitemap.xml.
    """
    return Article.objects.filter(
        status=ArticleStatus.PUBLISHED,
        published_at__lte=timezone.now()
    ).select_related('category').only(
        'id', 'slug', 'updated_at', 'language', 'category__slug'
    ).order_by('-updated_at')
