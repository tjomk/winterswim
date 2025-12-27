"""
Views for location management (Imperative Shell).

These views coordinate between the web layer and business logic,
following the "Functional Core, Imperative Shell" pattern.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext as _, get_language
from django.views.generic import ListView, DetailView
from django.core.serializers import serialize

from apps.locations.models import Location
from apps.locations.forms import LocationSubmissionForm
from apps.locations.services import (
    prepare_location_data_for_save,
    normalize_search_query,
    parse_proximity_params,
    enrich_geojson_with_urls,
)
from apps.locations.repositories import (
    get_approved_locations,
    create_location,
    get_location_by_slug,
    get_nearby_locations,
    get_random_locations,
    combine_search_and_proximity,
    get_locations_grouped_by_type,
    get_locations_count_by_type,
    filter_locations_by_type,
)
from infrastructure.notifications.telegram import telegram_service


def map_view(request):
    """
    Main map view showing all approved locations.

    This is the home page of the site.
    """
    # Get all approved locations
    locations = get_approved_locations()

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
        # Get current language
        current_language = get_language() or 'en'

        # Get filter parameters
        search_query = normalize_search_query(
            self.request.GET.get('q', '')
        )
        location_type = self.request.GET.get('type')

        # Parse proximity parameters
        proximity = parse_proximity_params(
            self.request.GET.get('lat'),
            self.request.GET.get('lon'),
            self.request.GET.get('radius', '50')
        )

        # Get filtered queryset from repository
        queryset = combine_search_and_proximity(
            search_query=search_query,
            language=current_language,
            latitude=proximity['latitude'] if proximity else None,
            longitude=proximity['longitude'] if proximity else None,
            radius_km=proximity['radius_km'] if proximity else 50,
            location_type=location_type
        )

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
        # Return queryset filtered by slug from repository
        return get_location_by_slug(self.kwargs['slug'], approved_only=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.object.name

        # Get nearby locations (within 50km)
        if self.object.location:
            context['nearby_locations'] = get_nearby_locations(
                reference_point=self.object.location,
                radius_km=50,
                exclude_pk=self.object.pk,
                limit=5
            )

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

            # Create location via repository
            location = create_location(location_data)

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
    from django.urls import reverse

    # Get locations grouped by type (efficient DB query)
    locations_by_type = get_locations_grouped_by_type()
    location_type_counts = get_locations_count_by_type()

    # Calculate total
    total_locations = sum(location_type_counts.values())

    # Add breadcrumb navigation
    breadcrumb_list = [
        (_('Home'), reverse('locations:map')),
        (_('Site Map'), None),  # Current page - no link
    ]

    context = {
        'page_title': _('Site Map'),
        'locations_by_type': locations_by_type,
        'total_locations': total_locations,
        'location_type_counts': location_type_counts,
        'breadcrumb_list': breadcrumb_list,
    }

    return render(request, 'locations/sitemap_page.html', context)


def locations_api_view(request):
    """
    API endpoint to get locations as GeoJSON.

    Used by the map interface.
    Returns nearby locations if user location provided,
    otherwise returns 20 random locations.
    """
    from django.urls import reverse
    from django.http import JsonResponse
    from django.contrib.gis.geos import Point

    # Parse proximity parameters
    proximity = parse_proximity_params(
        request.GET.get('lat'),
        request.GET.get('lon'),
        request.GET.get('radius', '50')
    )

    # Get locations based on user location availability
    if proximity and proximity['latitude'] and proximity['longitude']:
        # User location available - get nearby locations
        reference_point = Point(
            proximity['longitude'],
            proximity['latitude'],
            srid=4326
        )
        locations = get_nearby_locations(
            reference_point=reference_point,
            radius_km=proximity.get('radius_km', 50),
            limit=100  # Show up to 100 nearby locations
        )
    else:
        # No user location - get 20 random locations
        location_type = request.GET.get('type')
        if location_type:
            locations = filter_locations_by_type(location_type=location_type)[:20]
        else:
            locations = get_random_locations(limit=20)

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

    # Add detail URLs
    data = enrich_geojson_with_urls(
        geojson,
        url_builder_fn=lambda slug: reverse('locations:detail', kwargs={'slug': slug})
    )

    return JsonResponse(data)
