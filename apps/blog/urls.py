"""
URL configuration for blog app.
"""

from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Blog home (listing)
    path('', views.BlogListView.as_view(), name='list'),

    # Category listing
    path('<slug:category_slug>/', views.CategoryView.as_view(), name='category'),

    # Article detail
    path('<slug:category_slug>/<slug:article_slug>/', views.ArticleDetailView.as_view(), name='detail'),
]
