document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const swimForm = document.getElementById('swim-form');
    const getLocationBtn = document.getElementById('get-location-btn');
    const totalSessions = document.getElementById('total-sessions');
    const totalTime = document.getElementById('total-time');
    const avgDuration = document.getElementById('avg-duration');
    const plungeList = document.getElementById('plunge-list');
    const exportBtn = document.getElementById('export-plunges-btn');
    const importBtn = document.getElementById('import-plunges-btn');
    const importFileInput = document.getElementById('import-file-input');
    const translationsElem = document.getElementById('js-translations');

    // Translations
    const translations = translationsElem.dataset;

    getLocationBtn.parentNode.insertBefore(weatherLoadingIndicator, getLocationBtn.nextSibling);

    // Form Inputs
    const dateTimeInput = document.getElementById('date-time');
    const durationMinutesInput = document.getElementById('duration-minutes');
    const durationSecondsInput = document.getElementById('duration-seconds');
    const waterTempInput = document.getElementById('water-temp');
    const airTempInput = document.getElementById('air-temp');
    const windSpeedInput = document.getElementById('wind-speed');
    const windDirectionInput = document.getElementById('wind-direction');
    const latitudeInput = document.getElementById('latitude');
    const longitudeInput = document.getElementById('longitude');

    // App State
    let plunges = JSON.parse(localStorage.getItem('plunges')) || [];

    // --- Functions ---

    function savePlunges() {
        localStorage.setItem('plunges', JSON.stringify(plunges));
    }

    function getWindDirectionClass(windDirection) {
        if (!windDirection) return '';

        const direction = windDirection.toLowerCase();
        const directionMap = {
            'n': 'direction-n',
            'ne': 'direction-ne',
            'e': 'direction-e',
            'se': 'direction-se',
            's': 'direction-s',
            'sw': 'direction-sw',
            'w': 'direction-w',
            'nw': 'direction-nw'
        };

        return directionMap[direction] || '';
    }

    function formatDuration(minutes, seconds) {
        const min = parseInt(minutes, 10) || 0;
        const sec = parseInt(seconds, 10) || 0;
        return `${min}m ${sec}s`;
    }

    function formatTemperature(temp) {
        return temp !== '' && temp !== undefined && temp !== null ? temp + '°C' : 'N/A';
    }

    function formatWind(windSpeed, windDirection) {
        if (!windSpeed) return 'N/A';
        return windSpeed + ' m/s';
    }

    function formatCoordinates(latitude, longitude) {
        if (!latitude || !longitude) return 'N/A';
        return `${latitude}, ${longitude}`;
    }

    function renderPlunges() {
        plungeList.innerHTML = '';

        if (plunges.length === 0) {
            plungeList.innerHTML = `<div class="empty-state">${translations.noPlungesRecorded}</div>`;
            return;
        }

        plunges.sort((a, b) => new Date(b.date) - new Date(a.date));
        plunges.forEach(plunge => {
            const plungeItem = document.createElement('div');
            plungeItem.className = 'plunge-item';
            plungeItem.setAttribute('data-id', plunge.id);
            const notAvailable = translations.notAvailable || 'N/A';

            // Format date for display
            const plungeDateTime = new Date(plunge.date);
            const formattedDate = plungeDateTime.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            const formattedTime = plungeDateTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            // Format data
            const duration = formatDuration(plunge.durationMinutes, plunge.durationSeconds);
            const waterTemp = formatTemperature(plunge.waterTemp);
            const airTemp = formatTemperature(plunge.airTemp);
            const windSpeed = formatWind(plunge.windSpeed, plunge.windDirection);
            const coordinates = formatCoordinates(plunge.latitude, plunge.longitude);
            const windDirectionClass = getWindDirectionClass(plunge.windDirection);

            plungeItem.innerHTML = `
                <div class="item-header">
                    <span class="item-date">${formattedDate} • ${formattedTime}</span>
                    <button class="delete-btn" title="Delete session">
                        <i data-lucide="trash-2"></i>
                    </button>
                </div>

                <div class="item-data-grid">
                    <div class="data-chip" title="Duration">
                        <i data-lucide="timer"></i>
                        <span class="value">${duration}</span>
                    </div>

                    <div class="data-chip" title="Water / Air Temp">
                        <i data-lucide="thermometer"></i>
                        <span class="value">${waterTemp} <span class="divider">/</span> ${airTemp}</span>
                    </div>

                    <div class="data-chip" title="Wind speed and direction">
                        <i data-lucide="wind"></i>
                        <span class="value">
                            ${windSpeed}
                            ${plunge.windDirection ? `<i data-lucide="arrow-up" class="wind-arrow ${windDirectionClass}"></i>` : ''}
                        </span>
                    </div>

                    <div class="data-chip" title="Coordinates">
                        <i data-lucide="map-pin"></i>
                        <span class="value">${coordinates}</span>
                    </div>
                </div>
            `;
            plungeList.appendChild(plungeItem);
        });

        // Re-initialize Lucide icons after rendering plunges
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    function renderStatistics() {
        const sessionCount = plunges.length;
        const totalTimeInSeconds = plunges.reduce((total, plunge) => {
            const minutes = parseInt(plunge.durationMinutes, 10) || 0;
            const seconds = parseInt(plunge.durationSeconds, 10) || 0;
            return total + (minutes * 60) + seconds;
        }, 0);

        const totalMinutes = Math.floor(totalTimeInSeconds / 60);
        const remainingSeconds = totalTimeInSeconds % 60;

        // Calculate average duration
        let avgDurationText = '0m 0s';
        if (sessionCount > 0) {
            const avgTimeInSeconds = totalTimeInSeconds / sessionCount;
            const avgMinutes = Math.floor(avgTimeInSeconds / 60);
            const avgSeconds = Math.round(avgTimeInSeconds % 60);
            avgDurationText = `${avgMinutes}m ${avgSeconds}s`;
        }

        totalSessions.textContent = sessionCount;
        totalTime.textContent = `${totalMinutes}m ${remainingSeconds}s`;
        avgDuration.textContent = avgDurationText;
    }

    function render() {
        renderStatistics();
        renderPlunges();
    }

    function handleDeletePlunge(plungeId) {
        if (confirm(translations.confirmDeletePlunge)) {
            plunges = plunges.filter(plunge => plunge.id !== plungeId);
            savePlunges();
            render();
        }
    }

    function handleAddPlunge(e) {
        e.preventDefault();
        const newPlunge = {
            id: Date.now(),
            date: dateTimeInput.value,
            durationMinutes: durationMinutesInput.value,
            durationSeconds: durationSecondsInput.value,
            waterTemp: waterTempInput.value,
            airTemp: airTempInput.value,
            windSpeed: windSpeedInput.value,
            windDirection: windDirectionInput.value,
            latitude: latitudeInput.value,
            longitude: longitudeInput.value,
        };
        plunges.push(newPlunge);
        savePlunges();
        render();
        swimForm.reset();

        // Reset date to now - datetime-local format is always YYYY-MM-DDThh:mm
        const now = new Date();
        // Adjust for timezone to get correct local time
        const timeZoneOffset = now.getTimezoneOffset() * 60000; // offset in milliseconds
        const localTime = new Date(now - timeZoneOffset);

        const year = localTime.getUTCFullYear();
        const month = (localTime.getUTCMonth() + 1).toString().padStart(2, '0');
        const day = localTime.getUTCDate().toString().padStart(2, '0');
        const hours = localTime.getUTCHours().toString().padStart(2, '0');
        const minutes = localTime.getUTCMinutes().toString().padStart(2, '0');

        dateTimeInput.value = `${year}-${month}-${day}T${hours}:${minutes}`;
    }

    function fetchWeatherData(latitude, longitude) {
        return new Promise((resolve, reject) => {
            const url = `/tracker/api/weather/?latitude=${latitude}&longitude=${longitude}`;

            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success && data.data) {
                        resolve(data.data);
                    } else {
                        reject(new Error(data.error || translations.unableToFetchWeather));
                    }
                })
                .catch(error => {
                    console.error('Error fetching weather data:', error);
                    reject(error);
                });
        });
    }

    function handleGetLocation() {
        if (!navigator.geolocation) {
            alert(translations.geolocationNotSupported);
            return;
        }

        // Show loading indicator
        getLocationBtn.disabled = true;

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                try {
                    latitudeInput.value = position.coords.latitude.toFixed(6);
                    longitudeInput.value = position.coords.longitude.toFixed(6);

                    // Fetch weather data for this location
                    const weatherData = await fetchWeatherData(
                        position.coords.latitude,
                        position.coords.longitude
                    );

                    // Fill in weather data
                    if (weatherData.temperature !== undefined) {
                        airTempInput.value = weatherData.temperature;
                    }
                    if (weatherData.windspeed !== undefined) {
                        windSpeedInput.value = weatherData.windspeed;
                    }
                    if (weatherData.winddirection) {
                        windDirectionInput.value = weatherData.winddirection;
                    }

                } catch (error) {
                    console.error('Weather fetch failed:', error);
                    // Don't show error to user as it's not critical
                } finally {
                    // Hide loading indicator
                    getLocationBtn.disabled = false;
                }
            },
            (error) => {
                alert(translations.unableToRetrieveLocation);
                getLocationBtn.disabled = false;
            }
        );
    }

    function handleExportPlunges() {
        if (plunges.length === 0) {
            alert(translations.noPlungesToExport);
            return;
        }
        const dataStr = JSON.stringify(plunges, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `winter_swims_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    function handleImportPlunges(event) {
        const file = event.target.files[0];
        if (!file) {
            return;
        }
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const importedPlunges = JSON.parse(e.target.result);
                if (!Array.isArray(importedPlunges)) {
                    throw new Error(translations.invalidImportFormatArray);
                }
                // Basic validation of the first item
                if (importedPlunges.length > 0 && !importedPlunges[0].hasOwnProperty('id')) {
                     throw new Error(translations.invalidImportFormatId);
                }
                if (confirm(translations.confirmOverrideData)) {
                    plunges = importedPlunges;
                    savePlunges();
                    render();
                }
            } catch (error) {
                alert(`${translations.errorImportingFile}${error.message}`);
            } finally {
                // Reset file input to allow importing the same file again
                importFileInput.value = '';
            }
        };
        reader.readAsText(file);
    }


    // --- Event Listeners ---
    swimForm.addEventListener('submit', handleAddPlunge);

    getLocationBtn.addEventListener('click', handleGetLocation);

    exportBtn.addEventListener('click', handleExportPlunges);

    importBtn.addEventListener('click', () => importFileInput.click());

    importFileInput.addEventListener('change', handleImportPlunges);

    plungeList.addEventListener('click', (e) => {
        const deleteButton = e.target.closest('.delete-btn');
        if (deleteButton) {
            const plungeItem = deleteButton.closest('.plunge-item');
            const plungeId = parseInt(plungeItem.dataset.id, 10);
            handleDeletePlunge(plungeId);
        }
    });


    // --- Initialisation ---

    // Set default date to now - datetime-local format is always YYYY-MM-DDThh:mm
    const now = new Date();
    // Adjust for timezone to get correct local time
    const timeZoneOffset = now.getTimezoneOffset() * 60000; // offset in milliseconds
    const localTime = new Date(now - timeZoneOffset);

    const year = localTime.getUTCFullYear();
    const month = (localTime.getUTCMonth() + 1).toString().padStart(2, '0');
    const day = localTime.getUTCDate().toString().padStart(2, '0');
    const hours = localTime.getUTCHours().toString().padStart(2, '0');
    const minutes = localTime.getUTCMinutes().toString().padStart(2, '0');

    dateTimeInput.value = `${year}-${month}-${day}T${hours}:${minutes}`;
    render();
});

