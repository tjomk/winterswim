/**
 * Leaflet Gesture Handling
 *
 * Adds gesture handling to Leaflet maps to prevent accidental scrolling/zooming
 * and improve UX on both desktop and mobile devices.
 *
 * Usage:
 *   initGestureHandling(map, mapElementId, translations);
 */

function initGestureHandling(map, mapElementId, translations) {
    'use strict';

    // Detect if user is on Mac
    const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
    const scrollText = isMac ? translations.scrollMac : translations.scroll;

    // Get map element
    const mapElement = document.getElementById(mapElementId);

    if (!mapElement) {
        console.error('Map element not found:', mapElementId);
        return;
    }

    // Set data attributes for overlay content
    mapElement.setAttribute('data-gesture-handling-touch-content', translations.touch);
    mapElement.setAttribute('data-gesture-handling-scroll-content', scrollText);

    // Track interaction state
    let draggingMap = false;
    let scrollTimeout = null;
    let touchTimeout = null;

    // Disable map dragging on mobile by default
    const disableDragging = () => {
        map.dragging.disable();
        if (map.tap) map.tap.disable();
    };

    const enableDragging = () => {
        map.dragging.enable();
        if (map.tap) map.tap.enable();
    };

    // Touch event handling for mobile
    const handleTouchStart = (e) => {
        if (e.touches.length === 1) {
            // Single finger touch - show warning
            mapElement.classList.add('leaflet-gesture-handling-touch-warning');
            disableDragging();
        } else if (e.touches.length === 2) {
            // Two finger touch - enable dragging
            e.preventDefault();
            enableDragging();
            mapElement.classList.remove('leaflet-gesture-handling-touch-warning');
        }
    };

    const handleTouchMove = (e) => {
        if (e.touches.length === 1) {
            // Single finger - show warning
            mapElement.classList.add('leaflet-gesture-handling-touch-warning');
            disableDragging();
        } else if (e.touches.length === 2) {
            // Two fingers - allow interaction
            e.preventDefault();
            enableDragging();
            mapElement.classList.remove('leaflet-gesture-handling-touch-warning');
        }
    };

    const handleTouchEnd = (e) => {
        // Clear any existing timeout
        if (touchTimeout) clearTimeout(touchTimeout);

        // Hide warning after 2 seconds with fade-out animation
        touchTimeout = setTimeout(() => {
            mapElement.classList.add('fadeout');
            setTimeout(() => {
                mapElement.classList.remove('leaflet-gesture-handling-touch-warning', 'fadeout');
            }, 500); // Wait for fade-out animation to complete
        }, 2000);

        // Re-enable dragging for desktop mouse events
        if (e.touches.length === 0) {
            enableDragging();
        }
    };

    // Add touch event listeners
    mapElement.addEventListener('touchstart', handleTouchStart, { passive: false });
    mapElement.addEventListener('touchmove', handleTouchMove, { passive: false });
    mapElement.addEventListener('touchend', handleTouchEnd);
    mapElement.addEventListener('touchcancel', handleTouchEnd);

    // Scroll wheel handling for desktop
    mapElement.addEventListener('wheel', (e) => {
        if (e.ctrlKey || e.metaKey) {
            // Allow zooming with Ctrl/Cmd + scroll
            e.preventDefault();
            map.scrollWheelZoom.enable();
            mapElement.classList.remove('leaflet-gesture-handling-scroll-warning', 'fadeout');
        } else {
            // Show warning
            map.scrollWheelZoom.disable();
            mapElement.classList.remove('fadeout');
            mapElement.classList.add('leaflet-gesture-handling-scroll-warning');

            // Clear any existing timeout
            if (scrollTimeout) clearTimeout(scrollTimeout);

            // Hide warning after 2 seconds with fade-out animation
            scrollTimeout = setTimeout(() => {
                mapElement.classList.add('fadeout');
                setTimeout(() => {
                    mapElement.classList.remove('leaflet-gesture-handling-scroll-warning', 'fadeout');
                }, 500); // Wait for fade-out animation to complete
            }, 2000);
        }
    }, { passive: false });

    // Track dragging state
    map.on('movestart', () => { draggingMap = true; });
    map.on('moveend', () => { draggingMap = false; });

    // Mouse over/out handling for desktop
    map.on('mouseover', () => {
        enableDragging();
    });

    map.on('mouseout', () => {
        if (!draggingMap) {
            // Keep dragging enabled on desktop for better UX
            enableDragging();
        }
    });
}
