"""
Article model for blog posts, guides, and quick reads.
"""

import uuid
import re
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class ArticleType(models.TextChoices):
    """Types of blog content."""
    GUIDE = 'guide', _('Ultimate Guide')
    POST = 'post', _('Blog Post')
    QUICK_READ = 'quick', _('Quick Read')


class ArticleStatus(models.TextChoices):
    """Publication status."""
    DRAFT = 'draft', _('Draft')
    SCHEDULED = 'scheduled', _('Scheduled')
    PUBLISHED = 'published', _('Published')
    ARCHIVED = 'archived', _('Archived')


class Article(models.Model):
    """
    Blog article - independent per language (not translations).

    Each language gets its own article instance for maximum flexibility.
    """

    # Basic information
    title = models.CharField(
        max_length=200,
        verbose_name=_('Title'),
        help_text=_('Article title')
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name=_('Slug'),
        help_text=_('SEO-friendly URL slug (auto-generated)'),
        blank=True
    )

    excerpt = models.TextField(
        max_length=300,
        verbose_name=_('Excerpt'),
        help_text=_('Short summary for listings (max 300 chars)'),
        blank=True
    )

    content = models.TextField(
        verbose_name=_('Content'),
        help_text=_('Article content in Markdown format')
    )

    # Categorization
    category = models.ForeignKey(
        'blog.Category',
        on_delete=models.PROTECT,  # Don't allow deleting categories with articles
        related_name='articles',
        verbose_name=_('Category')
    )

    article_type = models.CharField(
        max_length=20,
        choices=ArticleType.choices,
        default=ArticleType.POST,
        verbose_name=_('Article type'),
        help_text=_('Type of content')
    )

    # Language
    language = models.CharField(
        max_length=2,
        choices=[('en', 'English'), ('fi', 'Finnish'), ('et', 'Estonian')],
        default='en',
        verbose_name=_('Language'),
        db_index=True
    )

    # Featured image
    featured_image = models.ImageField(
        upload_to='blog/featured/%Y/%m/',
        verbose_name=_('Featured image'),
        help_text=_('Main article image (1200x630px recommended)'),
        blank=True
    )

    featured_image_alt = models.CharField(
        max_length=200,
        verbose_name=_('Image alt text'),
        help_text=_('Descriptive alt text for accessibility'),
        blank=True
    )

    # Publishing
    status = models.CharField(
        max_length=20,
        choices=ArticleStatus.choices,
        default=ArticleStatus.DRAFT,
        verbose_name=_('Status'),
        db_index=True
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Publish date'),
        help_text=_('Schedule publication (leave blank for immediate)'),
        db_index=True
    )

    # SEO
    meta_description = models.CharField(
        max_length=160,
        verbose_name=_('Meta description'),
        help_text=_('SEO description (max 160 chars, auto-generated from excerpt if blank)'),
        blank=True
    )

    meta_keywords = models.CharField(
        max_length=255,
        verbose_name=_('Meta keywords'),
        help_text=_('Comma-separated keywords'),
        blank=True
    )

    # Author information
    author_name = models.CharField(
        max_length=100,
        verbose_name=_('Author name'),
        default='Winter Swim Team'
    )

    # Reading time (auto-calculated)
    reading_time_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Reading time (minutes)'),
        help_text=_('Auto-calculated from content length')
    )

    # Engagement
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('View count'),
        help_text=_('Number of page views')
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', '-published_at']),
            models.Index(fields=['language', 'status', '-published_at']),
            models.Index(fields=['category', 'status', '-published_at']),
            models.Index(fields=['article_type', 'status']),
            models.Index(fields=['slug']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['language', 'slug'],
                name='unique_article_slug_per_language'
            )
        ]

    def __str__(self):
        return f"{self.title} ({self.language})"

    def save(self, *args, **kwargs):
        """Generate slug and calculate reading time if not exists."""
        if not self.slug:
            base_slug = slugify(self.title)
            uuid_part = str(uuid.uuid4()).split('-')[0]
            self.slug = f"{base_slug}-{uuid_part}"

        # Auto-calculate reading time (avg 200 words/min)
        if self.content:
            # Strip Markdown syntax for accurate word count
            text = re.sub(r'[#*`\[\]()]', '', self.content)
            word_count = len(text.split())
            self.reading_time_minutes = max(1, word_count // 200)

        # Auto-generate meta description from excerpt
        if not self.meta_description and self.excerpt:
            self.meta_description = self.excerpt[:160]

        super().save(*args, **kwargs)

    @property
    def is_published(self):
        """Check if article is currently published."""
        from django.utils import timezone
        return (
            self.status == ArticleStatus.PUBLISHED and
            self.published_at and
            self.published_at <= timezone.now()
        )
