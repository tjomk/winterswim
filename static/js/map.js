/**
 * Map Initialization and Location Loading
 *
 * Handles the interactive map on the home page, including:
 * - Initial map setup with gesture handling
 * - Loading and displaying location markers
 * - Geolocation support for nearby locations
 * - Marker clustering for better performance
 */

(function() {
    'use strict';

    // Check if map element exists and is visible
    const mapElement = document.getElementById('map');
    if (!mapElement || mapElement.style.display === 'none') {
        console.log('Map element not ready, skipping initialization');
        return;
    }

    // Get initial locations data from template
    const initialLocationsData = window.INITIAL_LOCATIONS_DATA || null;
    const translations = window.MAP_TRANSLATIONS || {};
    const apiUrl = window.LOCATIONS_API_URL || '/api/locations/';

    // Initialize map centered on Estonia with scroll wheel zoom disabled by default
    const map = L.map('map', {
        scrollWheelZoom: false,
        dragging: true,
        tap: true
    }).setView([59.0, 25.0], 7);

    // Initialize gesture handling
    if (typeof initGestureHandling === 'function') {
        initGestureHandling(map, 'map', translations);
    }

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
    }).addTo(map);

    // Custom marker icon using self-hosted image
    const locationIcon = L.icon({
        iconUrl: '/static/vendor/leaflet/images/marker-icon-blue-2x.png',
        shadowUrl: '/static/vendor/leaflet/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    // Track marker cluster group
    let markerClusterGroup = null;

    // Initialize marker cluster group if available
    if (typeof L.markerClusterGroup === 'function') {
        markerClusterGroup = L.markerClusterGroup({
            maxClusterRadius: 50,
            spiderfyOnMaxZoom: true,
            showCoverageOnHover: false,
            zoomToBoundsOnClick: true
        });
        map.addLayer(markerClusterGroup);
    }

    // Helper functions
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function truncate(text, length) {
        if (text.length <= length) return text;
        return text.substring(0, length) + '...';
    }

    function getLocationTypeLabel(type) {
        const labels = translations.locationTypes || {
            'wild': 'Wild spot',
            'commercial': 'Commercial facility',
            'club': 'Swimming club',
            'public': 'Public facility'
        };
        return labels[type] || type;
    }

    // Function to clear existing markers
    function clearMarkers() {
        if (markerClusterGroup) {
            markerClusterGroup.clearLayers();
        }
    }

    // Function to display locations on the map
    function displayLocations(data) {
        if (!data.features || data.features.length === 0) {
            console.log('No locations found');
            return;
        }

        // Clear existing markers
        clearMarkers();

        // Create bounds to fit all markers
        const bounds = [];

        // Add markers for each location
        data.features.forEach(feature => {
            const coords = feature.geometry.coordinates;
            const props = feature.properties;

            // Leaflet uses [lat, lon], GeoJSON uses [lon, lat]
            const latLng = [coords[1], coords[0]];
            bounds.push(latLng);

            // Create popup content
            const popupContent = `
                <div class="location-marker-popup">
                    <h3>${escapeHtml(props.name)}</h3>
                    <p><strong>${escapeHtml(getLocationTypeLabel(props.location_type))}</strong></p>
                    ${props.description ? `<p>${escapeHtml(truncate(props.description, 100))}</p>` : ''}
                    ${props.is_free ? '<p>✓ ' + (translations.freeAccess || 'Free access') + '</p>' : '<p>💰 ' + (translations.paid || 'Paid') + '</p>'}
                    <a href="${props.detail_url}" class="btn btn-primary btn-sm">${translations.viewDetails || 'View Details'}</a>
                </div>
            `;

            // Add marker
            const marker = L.marker(latLng, { icon: locationIcon })
                .bindPopup(popupContent);

            // Add to cluster group if available, otherwise add directly to map
            if (markerClusterGroup) {
                markerClusterGroup.addLayer(marker);
            } else {
                marker.addTo(map);
            }
        });

        // Fit map to show all markers
        if (bounds.length > 0) {
            map.fitBounds(bounds, { padding: [50, 50] });
        }
    }

    // Function to load locations from API
    function loadLocations(latitude, longitude) {
        // Build API URL with optional location parameters
        let url = apiUrl;
        if (latitude && longitude) {
            url += `?lat=${latitude}&lon=${longitude}&radius=50`;
        }

        fetch(url)
            .then(response => response.json())
            .then(data => {
                displayLocations(data);
            })
            .catch(error => {
                console.error('Error loading locations:', error);
            });
    }

    // Display initial locations immediately (no waiting for geolocation)
    if (initialLocationsData) {
        console.log('Displaying initial locations');
        displayLocations(initialLocationsData);
    }

    // Try to get user's location and load nearby locations
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            // Success callback
            function(position) {
                const latitude = position.coords.latitude;
                const longitude = position.coords.longitude;
                console.log('User location obtained:', latitude, longitude);
                // Load nearby locations to replace initial ones
                loadLocations(latitude, longitude);
            },
            // Error callback
            function(error) {
                console.log('Geolocation error or denied:', error.message);
                // Keep initial locations - don't reload
            },
            // Options
            {
                timeout: 5000,
                maximumAge: 300000  // Accept cached position up to 5 minutes old
            }
        );
    }

    // Mobile: adjust map on window resize
    window.addEventListener('resize', function() {
        map.invalidateSize();
    });
})();
