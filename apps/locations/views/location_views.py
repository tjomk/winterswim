"""
Views for location management (Imperative Shell).

These views coordinate between the web layer and business logic,
following the "Functional Core, Imperative Shell" pattern.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from django.views.generic import ListView, DetailView
from django.core.serializers import serialize
import json

from apps.locations.models import Location
from apps.locations.forms import LocationSubmissionForm
from apps.locations.services import prepare_location_data_for_save


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

    context = {
        'locations_geojson': locations_geojson,
        'page_title': _('Winter Swimming Locations'),
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
        """Get only approved locations."""
        queryset = Location.objects.filter(is_approved=True)

        # Filter by location type if provided
        location_type = self.request.GET.get('type')
        if location_type:
            queryset = queryset.filter(location_type=location_type)

        # Filter by facilities if provided
        # TODO: Implement facility filtering

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('All Locations')
        return context


class LocationDetailView(DetailView):
    """
    Detail view for a single location.
    """
    model = Location
    template_name = 'locations/location_detail.html'
    context_object_name = 'location'

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

            # TODO: Send Telegram notification to moderators

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
    for feature in data['features']:
        location_id = feature['properties']['pk']
        feature['properties']['detail_url'] = f'/locations/{location_id}/'

    from django.http import JsonResponse
    return JsonResponse(data)
