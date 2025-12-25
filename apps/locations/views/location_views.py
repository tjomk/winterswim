"""
Views for location management (Imperative Shell).

These views coordinate between the web layer and business logic,
following the "Functional Core, Imperative Shell" pattern.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import gettext as _, get_language
from django.views.generic import ListView, DetailView
from django.core.serializers import serialize
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F
import json

from apps.locations.models import Location
from apps.locations.forms import LocationSubmissionForm
from apps.locations.services import prepare_location_data_for_save
from infrastructure.notifications.telegram import telegram_service


def map_view(request):
    """
    Main map view showing all approved locations.

    This is the home page of the site.
    """
    # Get all approved locations
    locations = Location.objects.filter(is_approved=True)

    # Serialize locations for the map
    locations_geojson = serialize(
        'geojson',
        locations,
        geometry_field='location',
        fields=('name', 'location_type', 'description')
    )

    # Add breadcrumb navigation (home page - single item for Schema.org)
    from django.urls import reverse
    breadcrumb_list = [
        (_('Home'), None),  # Current page - no link
    ]

    context = {
        'locations_geojson': locations_geojson,
        'page_title': _('Winter Swimming Locations'),
        'breadcrumb_list': breadcrumb_list,
    }

    return render(request, 'locations/map.html', context)


class LocationListView(ListView):
    """
    List view of all approved locations.
    """
    model = Location
    template_name = 'locations/location_list.html'
    context_object_name = 'locations'
    paginate_by = 20

    def get_queryset(self):
        """Get approved locations with optional search and proximity filters."""
        queryset = Location.objects.filter(is_approved=True)

        # Get current language for search
        current_language = get_language() or 'en'

        # SEARCH FILTER
        search_query = self.request.GET.get('q', '').strip()
        if search_query and len(search_query) >= 3:
            # Use the appropriate search vector for current language
            search_vector_field = f'search_vector_{current_language}'

            # Create search query with language-specific config
            search_configs = {'en': 'english', 'fi': 'finnish', 'et': 'simple'}
            search_config = search_configs.get(current_language, 'simple')

            search_q = SearchQuery(search_query, config=search_config)

            # Search in language-specific search vector
            queryset = queryset.filter(
                **{f'{search_vector_field}__icontains': search_q}
            ).annotate(
                rank=SearchRank(F(search_vector_field), search_q)
            ).order_by('-rank', '-created_at')

        # PROXIMITY FILTER ("Near Me")
        lat = self.request.GET.get('lat')
        lon = self.request.GET.get('lon')
        radius_km = self.request.GET.get('radius', '50')  # Default 50km

        if lat and lon:
            try:
                lat_float = float(lat)
                lon_float = float(lon)
                radius_float = float(radius_km)

                # Validate coordinates (basic sanity check)
                if not (-90 <= lat_float <= 90 and -180 <= lon_float <= 180):
                    raise ValueError("Invalid coordinates")
                if not (1 <= radius_float <= 500):  # Max 500km to prevent abuse
                    radius_float = 50

                user_point = Point(lon_float, lat_float, srid=4326)

                # Filter locations within radius and annotate with distance
                queryset = queryset.filter(
                    location__distance_lte=(user_point, D(km=radius_float))
                ).annotate(
                    distance=Distance('location', user_point)
                ).order_by('distance')

            except (ValueError, TypeError):
                # Invalid coordinates - ignore proximity filter
                pass

        # LOCATION TYPE FILTER (existing)
        location_type = self.request.GET.get('type')
        if location_type:
            queryset = queryset.filter(location_type=location_type)

        # Default ordering if no proximity or search
        if not (search_query or (lat and lon)):
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('All Locations')

        # Pass search parameters to template for preservation
        context['search_query'] = self.request.GET.get('q', '')
        context['filter_lat'] = self.request.GET.get('lat', '')
        context['filter_lon'] = self.request.GET.get('lon', '')
        context['filter_radius'] = self.request.GET.get('radius', '50')
        context['is_proximity_filtered'] = bool(context['filter_lat'] and context['filter_lon'])

        # Add breadcrumb navigation
        from django.urls import reverse
        context['breadcrumb_list'] = [
            (_('Home'), reverse('locations:map')),
            (_('All Locations'), None),  # Current page - no link
        ]

        return context


class LocationDetailView(DetailView):
    """
    Detail view for a single location.
    """
    model = Location
    template_name = 'locations/location_detail.html'
    context_object_name = 'location'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        """Only show approved locations."""
        return Location.objects.filter(is_approved=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.object.name

        # Get nearby locations (within 50km)
        if self.object.location:
            from django.contrib.gis.measure import D
            nearby = Location.objects.filter(
                is_approved=True,
                location__distance_lte=(self.object.location, D(km=50))
            ).exclude(pk=self.object.pk)[:5]
            context['nearby_locations'] = nearby

        # Add breadcrumb navigation
        from django.urls import reverse
        context['breadcrumb_list'] = [
            (_('Home'), reverse('locations:map')),
            (_('All Locations'), reverse('locations:list')),
            (self.object.name, None),  # Current page - no link
        ]

        return context


def location_submit_view(request):
    """
    View for submitting a new location (no authentication required).
    """
    if request.method == 'POST':
        form = LocationSubmissionForm(request.POST)

        if form.is_valid():
            # Use service layer to prepare data
            location_data = prepare_location_data_for_save(form.cleaned_data)

            # Create location (imperative shell)
            location = Location.objects.create(**location_data)

            # Send Telegram notification to moderators
            telegram_service.notify_new_submission(location)

            messages.success(
                request,
                _('Thank you! Your location has been submitted and will be reviewed by our moderators.')
            )

            return redirect('locations:submit_success')

    else:
        form = LocationSubmissionForm()

    context = {
        'form': form,
        'page_title': _('Suggest a Location'),
    }

    return render(request, 'locations/location_submit.html', context)


def submit_success_view(request):
    """Success page after location submission."""
    context = {
        'page_title': _('Submission Successful'),
    }
    return render(request, 'locations/submit_success.html', context)


def sitemap_page_view(request):
    """
    HTML sitemap page for users.

    Shows all locations grouped by type with statistics.
    """
    from collections import defaultdict
    from django.urls import reverse

    # Get all approved locations
    locations = Location.objects.filter(is_approved=True).order_by('name')

    # Group locations by type
    locations_by_type = defaultdict(list)
    location_type_counts = {}

    for location in locations:
        type_display = location.get_location_type_display()
        locations_by_type[type_display].append(location)

    # Convert defaultdict to regular dict for template
    locations_by_type = dict(locations_by_type)

    # Calculate counts for statistics
    for type_name, type_locations in locations_by_type.items():
        location_type_counts[type_name] = len(type_locations)

    # Add breadcrumb navigation
    breadcrumb_list = [
        (_('Home'), reverse('locations:map')),
        (_('Site Map'), None),  # Current page - no link
    ]

    context = {
        'page_title': _('Site Map'),
        'locations_by_type': locations_by_type,
        'total_locations': locations.count(),
        'location_type_counts': location_type_counts,
        'breadcrumb_list': breadcrumb_list,
    }

    return render(request, 'locations/sitemap_page.html', context)


def locations_api_view(request):
    """
    API endpoint to get locations as GeoJSON.

    Used by the map interface.
    """
    locations = Location.objects.filter(is_approved=True)

    # Apply filters if provided
    location_type = request.GET.get('type')
    if location_type:
        locations = locations.filter(location_type=location_type)

    # Serialize to GeoJSON
    geojson = serialize(
        'geojson',
        locations,
        geometry_field='location',
        fields=(
            'pk',
            'name',
            'slug',
            'description',
            'location_type',
            'facilities',
            'is_free',
            'address',
        )
    )

    # Parse and enhance GeoJSON
    data = json.loads(geojson)

    # Add detail URL to each feature
    from django.urls import reverse
    for feature in data['features']:
        location_slug = feature['properties']['slug']
        feature['properties']['detail_url'] = reverse('locations:detail', kwargs={'slug': location_slug})

    from django.http import JsonResponse
    return JsonResponse(data)
