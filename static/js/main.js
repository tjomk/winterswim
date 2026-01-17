/**
 * Main JavaScript
 *
 * Core functionality for the site.
 */

(function() {
    'use strict';

    // Mobile menu toggle
    function initMobileMenu() {
        const toggle = document.getElementById('mobile-menu-toggle');
        const nav = document.getElementById('site-nav');

        if (!toggle || !nav) return;

        toggle.addEventListener('click', function() {
            nav.classList.toggle('is-open');
            nav.classList.toggle('mobile-menu-open');
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!toggle.contains(event.target) && !nav.contains(event.target)) {
                nav.classList.remove('is-open');
                nav.classList.remove('mobile-menu-open');
            }
        });

        // Close menu when pressing Escape
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                nav.classList.remove('is-open');
                nav.classList.remove('mobile-menu-open');
            }
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMobileMenu);
    } else {
        initMobileMenu();
    }
})();
