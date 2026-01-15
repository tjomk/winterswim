document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const addPlungeToggleBtn = document.getElementById('add-plunge-toggle-btn');
    const addPlungeForm = document.getElementById('add-plunge-form');
    const getLocationBtn = document.getElementById('get-location-btn');
    const statsSessions = document.getElementById('stats-sessions');
    const statsTotalTime = document.getElementById('stats-total-time');
    const plungeList = document.getElementById('plunge-list');
    const exportBtn = document.getElementById('export-plunges-btn');
    const importBtn = document.getElementById('import-plunges-btn');
    const importFileInput = document.getElementById('import-file-input');
    const translationsElem = document.getElementById('js-translations');

    // Translations
    const translations = translationsElem.dataset;

    // Form Inputs
    const plungeDateInput = document.getElementById('plunge-date');
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
            plungeList.innerHTML = `<p>${translations.noPlungesRecorded}</p>`;
            return;
        }

        plunges.sort((a, b) => new Date(b.date) - new Date(a.date));

        plunges.forEach(plunge => {
            const plungeItem = document.createElement('div');
            plungeItem.className = 'plunge-card';
            plungeItem.setAttribute('data-id', plunge.id);
            const notAvailable = translations.notAvailable || 'N/A';
            plungeItem.innerHTML = `
                <div class="plunge-card-header">
                    <h3>${new Date(plunge.date).toLocaleString()}</h3>
                    <button class="delete-plunge-btn">&times;</button>
                </div>
                <p><strong>${translations.duration}:</strong> ${plunge.durationMinutes || 0}m ${plunge.durationSeconds || 0}s</p>
                <p><strong>${translations.location}:</strong> ${plunge.latitude || notAvailable}, ${plunge.longitude || notAvailable}</p>
                <p><strong>${translations.waterTemp}:</strong> ${plunge.waterTemp !== '' ? plunge.waterTemp + '°C' : notAvailable}</p>
                <p><strong>${translations.airTemp}:</strong> ${plunge.airTemp !== '' ? plunge.airTemp + '°C' : notAvailable}</p>
                <p><strong>${translations.wind}:</strong> ${plunge.windSpeed ? plunge.windSpeed + ' m/s' : notAvailable}, ${plunge.windDirection || notAvailable}</p>
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

        statsSessions.textContent = totalSessions;
        statsTotalTime.textContent = `${totalMinutes}m ${remainingSeconds}s`;
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
            date: plungeDateInput.value,
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
        addPlungeForm.reset();
        addPlungeForm.style.display = 'none';
        plungeDateInput.valueAsNumber = new Date().getTime() - new Date().getTimezoneOffset() * 60000;
    }

    function handleGetLocation() {
        if (!navigator.geolocation) {
            alert(translations.geolocationNotSupported);
            return;
        }
        navigator.geolocation.getCurrentPosition(
            (position) => {
                latitudeInput.value = position.coords.latitude.toFixed(6);
                longitudeInput.value = position.coords.longitude.toFixed(6);
            },
            () => {
                alert(translations.unableToRetrieveLocation);
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

    addPlungeToggleBtn.addEventListener('click', () => {
        const isVisible = addPlungeForm.style.display === 'block';
        addPlungeForm.style.display = isVisible ? 'none' : 'block';
    });

    addPlungeForm.addEventListener('submit', handleAddPlunge);

    getLocationBtn.addEventListener('click', handleGetLocation);

    exportBtn.addEventListener('click', handleExportPlunges);

    importBtn.addEventListener('click', () => importFileInput.click());

    importFileInput.addEventListener('change', handleImportPlunges);

    plungeList.addEventListener('click', (e) => {
        if (e.target.classList.contains('delete-plunge-btn')) {
            const card = e.target.closest('.plunge-card');
            const plungeId = parseInt(card.dataset.id, 10);
            handleDeletePlunge(plungeId);
        }
    });


    // --- Initialisation ---

    // Set default date to now
    plungeDateInput.valueAsNumber = new Date().getTime() - new Date().getTimezoneOffset() * 60000;
    render();
});

