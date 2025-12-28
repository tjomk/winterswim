"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap
from apps.locations.views.seo_views import robots_txt
from apps.locations.sitemaps import LocationSitemap, StaticViewSitemap, CountrySitemap, CitySitemap
from apps.blog.sitemaps import ArticleSitemap, CategorySitemap

# Sitemap configuration
sitemaps = {
    'locations': LocationSitemap,
    'countries': CountrySitemap,
    'cities': CitySitemap,
    'static': StaticViewSitemap,
    'articles': ArticleSitemap,
    'categories': CategorySitemap,
}

urlpatterns = [
    # SEO
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # Admin
    path('admin/', admin.site.urls),

    # i18n
    path('i18n/', include('django.conf.urls.i18n')),
]

# Add i18n patterns for translated URLs
urlpatterns += i18n_patterns(
    # Blog
    path('blog/', include('apps.blog.urls')),

    # Locations app (main site)
    path('', include('apps.locations.urls')),
)

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
