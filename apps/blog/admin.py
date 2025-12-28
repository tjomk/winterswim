"""
Django admin configuration for Blog models.

Provides admin interface for managing categories and articles.
"""

from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from django.urls import reverse

from .models import Article, Category
from .services import render_markdown


class ArticleAdminForm(forms.ModelForm):
    """Custom form with Markdown preview support."""

    class Meta:
        model = Article
        fields = '__all__'
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 30,
                'class': 'markdown-editor',
                'style': 'font-family: monospace;'
            }),
            'excerpt': forms.Textarea(attrs={'rows': 3}),
        }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for blog categories."""

    list_display = ('name', 'language', 'order', 'article_count', 'created_at')
    list_filter = ('language', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('language', 'order', 'name')

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'language', 'description', 'order')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def article_count(self, obj):
        """Display number of published articles in this category."""
        return obj.articles.filter(status='published').count()
    article_count.short_description = _('Published Articles')

    def get_queryset(self, request):
        """Optimize queries with article count."""
        qs = super().get_queryset(request)
        return qs.annotate(_article_count=Count('articles'))


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Admin interface for blog articles with Markdown support."""

    form = ArticleAdminForm

    list_display = (
        'title',
        'category',
        'article_type',
        'language',
        'status_badge',
        'published_at',
        'view_count',
        'reading_time_minutes',
    )

    list_filter = (
        'status',
        'language',
        'article_type',
        'category',
        'published_at',
        'created_at',
    )

    search_fields = (
        'title',
        'content',
        'excerpt',
        'meta_keywords',
    )

    readonly_fields = (
        'view_on_site_link',
        'created_at',
        'updated_at',
        'view_count',
        'reading_time_minutes',
        'content_preview',
    )

    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'view_on_site_link',
                'title',
                'slug',
                'category',
                'language',
                'article_type',
                'author_name',
            )
        }),
        (_('Content'), {
            'fields': (
                'excerpt',
                'content',
                'content_preview',
            ),
            'description': _('Content is written in Markdown format. Preview will be rendered below.')
        }),
        (_('Featured Image'), {
            'fields': (
                'featured_image',
                'featured_image_alt',
            ),
            'classes': ('collapse',)
        }),
        (_('Publishing'), {
            'fields': (
                'status',
                'published_at',
            )
        }),
        (_('SEO'), {
            'fields': (
                'meta_description',
                'meta_keywords',
            ),
            'classes': ('collapse',)
        }),
        (_('Statistics'), {
            'fields': (
                'reading_time_minutes',
                'view_count',
            ),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    actions = ['publish_articles', 'draft_articles', 'archive_articles']

    date_hierarchy = 'published_at'

    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'draft': 'gray',
            'scheduled': 'orange',
            'published': 'green',
            'archived': 'red',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_badge.short_description = _('Status')

    def content_preview(self, obj):
        """Render Markdown preview."""
        if obj.content:
            html_content = render_markdown(obj.content)
            return format_html(
                '<div class="markdown-preview" style="border: 1px solid #ccc; padding: 1rem; background: #f9f9f9; max-height: 400px; overflow-y: auto;">{}</div>',
                html_content
            )
        return '-'
    content_preview.short_description = _('Content Preview')

    def view_on_site_link(self, obj):
        """Display a clickable link to view the article on the site."""
        if obj.pk and obj.category:
            url = reverse('blog:detail', kwargs={
                'category_slug': obj.category.slug,
                'article_slug': obj.slug
            })
            return format_html(
                '<a href="{}" target="_blank" style="font-size: 14px; font-weight: bold; color: #417690;">🔗 View article on site</a>',
                url
            )
        return mark_safe('<span style="color: #999;">Save the article first to view it on the site</span>')
    view_on_site_link.short_description = _('View on Site')

    def publish_articles(self, request, queryset):
        """Bulk action to publish articles."""
        from django.utils import timezone
        updated = queryset.update(
            status='published',
            published_at=timezone.now()
        )
        self.message_user(
            request,
            _('{count} article(s) published.').format(count=updated)
        )
    publish_articles.short_description = _('Publish selected articles')

    def draft_articles(self, request, queryset):
        """Bulk action to set articles to draft."""
        updated = queryset.update(status='draft')
        self.message_user(
            request,
            _('{count} article(s) set to draft.').format(count=updated)
        )
    draft_articles.short_description = _('Set as draft')

    def archive_articles(self, request, queryset):
        """Bulk action to archive articles."""
        updated = queryset.update(status='archived')
        self.message_user(
            request,
            _('{count} article(s) archived.').format(count=updated)
        )
    archive_articles.short_description = _('Archive selected articles')
