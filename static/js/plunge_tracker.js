document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const swimForm = document.getElementById('swim-form');
    const getLocationBtn = document.getElementById('get-location-btn');
    const totalSessions = document.getElementById('total-sessions');
    const totalTime = document.getElementById('total-time');
    const plungeList = document.getElementById('plunge-list');
    const exportBtn = document.getElementById('export-plunges-btn');
    const importBtn = document.getElementById('import-plunges-btn');
    const importFileInput = document.getElementById('import-file-input');
    const translationsElem = document.getElementById('js-translations');

    // Translations
    const translations = translationsElem.dataset;
    
    // Weather loading indicator
    const weatherLoadingIndicator = document.createElement('div');
    weatherLoadingIndicator.className = 'weather-loading';
    weatherLoadingIndicator.textContent = translations.fetchingWeather || 'Fetching weather...';
    weatherLoadingIndicator.style.display = 'none';
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
            const formattedDate = plungeDateTime.toLocaleDateString();
            const formattedTime = plungeDateTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            plungeItem.innerHTML = `
                <div class="item-date">${formattedDate} ${formattedTime}</div>
                <div class="item-details">
                    <div>${plunge.durationMinutes || 0}m ${plunge.durationSeconds || 0}s</div>
                    <div>${plunge.waterTemp !== '' ? plunge.waterTemp + '°C' : notAvailable} / ${plunge.airTemp !== '' ? plunge.airTemp + '°C' : notAvailable}</div>
                    <div>${plunge.windSpeed ? (plunge.windSpeed + ' m/s' + (plunge.windDirection ? ' ' + plunge.windDirection : '')) : notAvailable}</div>
                </div>
                <button class="delete-btn" aria-label="Delete plunge">&times;</button>
            `;
            plungeList.appendChild(plungeItem);
        });
    }

    function renderStatistics() {
        const totalSessions = plunges.length;
        const totalTimeInSeconds = plunges.reduce((total, plunge) => {
            const minutes = parseInt(plunge.durationMinutes, 10) || 0;
            const seconds = parseInt(plunge.durationSeconds, 10) || 0;
            return total + (minutes * 60) + seconds;
        }, 0);

        const totalMinutes = Math.floor(totalTimeInSeconds / 60);
        const remainingSeconds = totalTimeInSeconds % 60;

        totalSessions.textContent = totalSessions;
        totalTime.textContent = `${totalMinutes}m ${remainingSeconds}s`;
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
            const url = `/plunge-tracker/api/weather/?latitude=${latitude}&longitude=${longitude}`;
            
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
        weatherLoadingIndicator.style.display = 'inline-block';
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
                    weatherLoadingIndicator.style.display = 'none';
                    getLocationBtn.disabled = false;
                }
            },
            (error) => {
                alert(translations.unableToRetrieveLocation);
                weatherLoadingIndicator.style.display = 'none';
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
        if (e.target.classList.contains('delete-btn')) {
            const plungeItem = e.target.closest('.plunge-item');
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

