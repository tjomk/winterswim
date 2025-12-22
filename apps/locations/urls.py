"""
URL configuration for locations app.
"""

from django.urls import path
from . import views

app_name = 'locations'

urlpatterns = [
    # Main map view (home page)
    path('', views.map_view, name='map'),

    # Submission (must come before slug pattern)
    path('submit/', views.location_submit_view, name='submit'),
    path('submit/success/', views.submit_success_view, name='submit_success'),

    # Location views
    path('list/', views.LocationListView.as_view(), name='list'),

    # API
    path('api/locations/', views.locations_api_view, name='api_locations'),

    # Detail view (must be last - catches all remaining paths)
    path('<slug:slug>/', views.LocationDetailView.as_view(), name='detail'),
]
