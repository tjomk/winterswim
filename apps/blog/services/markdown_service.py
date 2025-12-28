"""
Markdown rendering service with security.

Renders Markdown content to sanitized HTML using bleach for XSS prevention.
"""

import re
import markdown
from bleach import clean, linkify
from django.utils.safestring import mark_safe


# Allowed HTML tags after Markdown rendering
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'code', 'pre',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'img', 'hr', 'div', 'span'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
    'img': ['src', 'alt', 'title'],
    'code': ['class'],
    'div': ['class'],
    'span': ['class'],
    'pre': ['class'],
}


def render_markdown(content: str) -> str:
    """
    Render Markdown content to sanitized HTML.

    Args:
        content: Markdown text

    Returns:
        Safe HTML string

    Security:
        - Sanitizes HTML with bleach
        - Allows only safe tags and attributes
        - Auto-linkifies URLs

    Usage:
        html = render_markdown(article.content)
    """
    if not content:
        return ''

    # Render Markdown to HTML
    md = markdown.Markdown(extensions=[
        'fenced_code',      # ```code blocks```
        'tables',           # Tables support
        'nl2br',            # Newline to <br>
        'toc',              # Table of contents
        'codehilite',       # Code syntax highlighting
    ])
    html = md.convert(content)

    # Sanitize HTML (prevent XSS)
    clean_html = clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )

    # Auto-linkify URLs
    linkified_html = linkify(clean_html)

    return mark_safe(linkified_html)


def extract_reading_time(content: str) -> int:
    """
    Calculate reading time from content.

    Args:
        content: Article content (Markdown or plain text)

    Returns:
        Estimated reading time in minutes (minimum 1)

    Usage:
        reading_time = extract_reading_time(article.content)
    """
    if not content:
        return 1

    # Strip Markdown syntax for accurate word count
    text = re.sub(r'[#*`\[\]()]', '', content)
    words = text.split()
    word_count = len(words)

    # Average reading speed: 200 words per minute
    reading_time = max(1, word_count // 200)

    return reading_time
