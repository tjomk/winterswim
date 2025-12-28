"""
URL configuration for locations app.
"""

from django.urls import path
from django.views.generic import RedirectView
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
    path('sitemap/', views.sitemap_page_view, name='sitemap_page'),

    # API
    path('api/locations/', views.locations_api_view, name='api_locations'),

    # Location detail (moved to avoid conflicts with country/city pages)
    path('locations/<slug:slug>/', views.LocationDetailView.as_view(), name='detail'),

    # Country and city pages
    path('countries/', views.CountryListView.as_view(), name='country_list'),
    path('<slug:country_slug>/', views.CountryDetailView.as_view(), name='country_detail'),
    path('<slug:country_slug>/<slug:city_slug>/', views.CityDetailView.as_view(), name='city_detail'),
]
