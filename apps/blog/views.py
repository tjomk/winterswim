"""
Views for blog application.

Implements blog listing, category filtering, and article detail views.
"""

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.utils.translation import get_language, gettext as _
from django.urls import reverse

from apps.blog.models import Article, Category
from apps.blog.repositories import (
    get_published_articles,
    get_articles_by_category,
    get_article_by_slug,
    get_related_articles,
    increment_view_count,
    get_categories_for_language,
)
from apps.blog.services import render_markdown


class BlogListView(ListView):
    """
    Blog listing page showing all articles.
    """
    model = Article
    template_name = 'blog/blog_list.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get_queryset(self):
        """Get published articles for current language."""
        language = get_language() or 'en'
        return get_published_articles(language=language)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language() or 'en'

        context['page_title'] = _('Blog')
        context['categories'] = get_categories_for_language(language)

        # Breadcrumbs
        context['breadcrumb_list'] = [
            (_('Home'), reverse('locations:map')),
            (_('Blog'), None),
        ]

        return context


class CategoryView(ListView):
    """
    Category page showing articles in a category.
    """
    model = Article
    template_name = 'blog/category_list.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get_queryset(self):
        """Get articles in category for current language."""
        language = get_language() or 'en'
        category_slug = self.kwargs['category_slug']
        return get_articles_by_category(
            category_slug=category_slug,
            language=language
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language() or 'en'
        category_slug = self.kwargs['category_slug']

        # Get category object
        category = get_object_or_404(
            Category,
            slug=category_slug,
            language=language
        )
        context['category'] = category
        context['page_title'] = category.name

        # All categories for navigation
        context['categories'] = get_categories_for_language(language)

        # Breadcrumbs
        context['breadcrumb_list'] = [
            (_('Home'), reverse('locations:map')),
            (_('Blog'), reverse('blog:list')),
            (category.name, None),
        ]

        return context


class ArticleDetailView(DetailView):
    """
    Article detail page.
    """
    model = Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'
    slug_url_kwarg = 'article_slug'

    def get_queryset(self):
        """Get article by slug within category."""
        language = get_language() or 'en'
        return get_article_by_slug(
            article_slug=self.kwargs['article_slug'],
            category_slug=self.kwargs['category_slug'],
            language=language
        )

    def get_object(self, queryset=None):
        """Get article and increment view count."""
        obj = super().get_object(queryset)

        # Increment view count (async in production)
        increment_view_count(obj.pk)

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language() or 'en'

        article = self.object

        # Render Markdown content
        context['rendered_content'] = render_markdown(article.content)

        # Related articles
        context['related_articles'] = get_related_articles(article, limit=3)

        # Categories for navigation
        context['categories'] = get_categories_for_language(language)

        # SEO
        context['page_title'] = article.title

        # Breadcrumbs
        context['breadcrumb_list'] = [
            (_('Home'), reverse('locations:map')),
            (_('Blog'), reverse('blog:list')),
            (article.category.name, reverse('blog:category', kwargs={
                'category_slug': article.category.slug
            })),
            (article.title, None),
        ]

        return context
