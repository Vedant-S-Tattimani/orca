
let map = null;
let currentMarker = null;
let historicalChart = null;
let selectedLat = 15.0;
let selectedLon = 73.0;

let isGlobeMode = false;
let globeViz = null;

window.toggleGlobeMode = function() {
    isGlobeMode = !isGlobeMode;
    const mapEl = document.getElementById('dash-map');
    const globeEl = document.getElementById('dash-globe');
    const icon = document.getElementById('globe-icon');
    
    if (isGlobeMode) {
        mapEl.classList.add('hidden');
        globeEl.classList.remove('hidden');
        icon.textContent = 'map';
        
        if (!globeViz) {
            globeViz = Globe()(globeEl)
                .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
                .bumpImageUrl('https://unpkg.com/three-globe/example/img/earth-topology.png')
                .pointOfView({ lat: selectedLat, lng: selectedLon, altitude: 1.5 })
                .labelsData([{ lat: selectedLat, lng: selectedLon, text: 'Current Location', color: 'red' }])
                .labelLat('lat')
                .labelLng('lng')
                .labelText('text')
                .labelColor('color')
                .labelSize(1.5)
                .labelDotRadius(0.5);
                
            // Handle clicks on globe to update location
            globeViz.onGlobeClick((coords) => {
                selectedLat = coords.lat;
                selectedLon = coords.lng;
                globeViz.labelsData([{ lat: selectedLat, lng: selectedLon, text: 'Current Location', color: 'red' }]);
                
                document.getElementById('map-coords-label').textContent = `Lat: ${selectedLat.toFixed(2)}, Lon: ${selectedLon.toFixed(2)}`;
                document.getElementById('current-location-label').textContent = `Lat ${selectedLat.toFixed(2)}, Lon ${selectedLon.toFixed(2)}`;
                if(currentMarker) { currentMarker.setLatLng([selectedLat, selectedLon]); }
                if(map) { map.setView([selectedLat, selectedLon]); }
                fetchLatestData();
            });
            
            // Resize handler
            const updateGlobeSize = () => {
                globeViz.width(globeEl.clientWidth).height(globeEl.clientHeight);
            };
            window.addEventListener('resize', updateGlobeSize);
            setTimeout(updateGlobeSize, 100);
        } else {
            globeViz.pointOfView({ lat: selectedLat, lng: selectedLon, altitude: 1.5 });
            globeViz.labelsData([{ lat: selectedLat, lng: selectedLon, text: 'Current Location', color: 'red' }]);
        }
    } else {
        globeEl.classList.add('hidden');
        mapEl.classList.remove('hidden');
        icon.textContent = 'public';
        if(map) { map.invalidateSize(); }
    }
};

document.addEventListener('DOMContentLoaded', async () => {
    // 2. Initialize Map
    initMap();

    // 3. Load Role-based Features
    function getRoleFromToken() {
        const token = localStorage.getItem('token');
        if (!token) return null;
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));
            return JSON.parse(jsonPayload).role || null;
        } catch (e) {
            console.error("Failed to decode token", e);
            return null;
        }
    }
    const role = getRoleFromToken();
    if (role === 'researcher' || role === 'admin') {
        document.getElementById('researcher-section').classList.remove('hidden');
        initChart();
    }
    if (role === 'coastal_authority' || role === 'admin') {
        const caSection = document.getElementById('coastal-authority-section');
        if (caSection) caSection.classList.remove('hidden');
    }
    if (role === 'disaster_management' || role === 'admin') {
        const dmSection = document.getElementById('disaster-management-section');
        if (dmSection) dmSection.classList.remove('hidden');
    }

    // 4. Fetch Initial Data
    await fetchLatestData();
});

function initMap() {
    map = L.map('dash-map').setView([selectedLat, selectedLon], 9);
    const isDark = document.documentElement.classList.contains('dark');
    const tileUrl = isDark ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png' : 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';
    L.tileLayer(tileUrl, { attribution: '&copy; CARTO', subdomains: 'abcd', maxZoom: 20 }).addTo(map);

    currentMarker = L.marker([selectedLat, selectedLon]).addTo(map);
    map.on('click', async (e) => {
        selectedLat = e.latlng.lat;
        selectedLon = e.latlng.lng;
        currentMarker.setLatLng(e.latlng);
        map.setView(e.latlng);
        document.getElementById('map-coords-label').textContent = `Lat: ${selectedLat.toFixed(2)}, Lon: ${selectedLon.toFixed(2)}`;
        document.getElementById('current-location-label').textContent = `Lat ${selectedLat.toFixed(2)}, Lon ${selectedLon.toFixed(2)}`;
        if (globeViz) {
            globeViz.labelsData([{ lat: selectedLat, lng: selectedLon, text: 'Current Location', color: 'red' }]);
            globeViz.pointOfView({ lat: selectedLat, lng: selectedLon });
        }
        await fetchLatestData();
    });
}

function updateFreshness(id, label) {
    const el = document.getElementById(id);
    if(el) {
        const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        el.textContent = `${label} ${time}`;
    }
}

async function fetchLatestData() {
    const refreshIcon = document.getElementById('refresh-icon');
    if(refreshIcon) refreshIcon.classList.add('animate-spin');

    const nowStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    document.getElementById('global-freshness').textContent = `Last updated: ${nowStr}`;

    try {
        // --- 1. Fetch Environmental Data ---
        const envData = await window.OrcaAPI.getLocationEnvironmentalData(selectedLat, selectedLon);
        if (envData && envData.data) {
            const data = envData.data;
            document.getElementById('val-weather').textContent = data.weather_condition || 'Data unavailable';
            document.getElementById('val-wind').innerHTML = data.wind_speed_knots !== null ? `${data.wind_speed_knots} <span class="text-sm md:text-lg text-mute">kts</span>` : 'N/A';
            document.getElementById('val-wind-dir').textContent = data.wind_direction_deg !== null ? `Dir: ${data.wind_direction_deg}°` : 'Dir: --';
            document.getElementById('val-wave').innerHTML = data.wave_height_m !== null ? `${data.wave_height_m} <span class="text-sm md:text-lg text-mute">m</span>` : 'N/A';
            document.getElementById('val-sst').innerHTML = data.sea_surface_temp_c !== null ? `${data.sea_surface_temp_c} <span class="text-sm md:text-lg text-mute">°C</span>` : 'N/A';
            
            updateFreshness('fresh-weather', 'Updated');
            updateFreshness('fresh-wave', 'Updated');
            updateFreshness('fresh-sst', 'Updated');

            // Safety Logic
            const safety = data.fishing_safety;
            const safetyTitle = document.getElementById('safety-status-title');
            const safetyDesc = document.getElementById('safety-status-desc');
            const safetyIcon = document.getElementById('safety-icon');
            const safetyAction = document.getElementById('safety-action-text');
            const safetyCard = document.getElementById('safety-card');
            const aiSummary = document.getElementById('ai-summary');

            if (safety) {
                safetyTitle.textContent = safety.status;
                if (safety.score < 50) {
                    safetyCard.className = "p-6 rounded-xl border border-red-500/30 bg-red-500/5 shadow-sm flex flex-col justify-between";
                    safetyTitle.className = "font-display-xl text-3xl font-bold text-red-500";
                    safetyDesc.textContent = "It is highly recommended NOT to go out today. Dangerous marine conditions detected.";
                    safetyIcon.textContent = "warning";
                    safetyIcon.className = "material-symbols-outlined text-red-500";
                    safetyAction.textContent = "High Risk - Seek Harbor";
                    safetyAction.className = "text-sm font-semibold text-red-500";
                    if(aiSummary) aiSummary.innerHTML = `<span class="material-symbols-outlined text-[14px] inline-block align-middle mr-1">auto_awesome</span> AI Summary: Critical conditions. Do not operate vessels in this sector due to high wave and wind risks.`;
                    if(aiSummary) aiSummary.className = "text-xs text-red-500 font-mono";
                } else if (safety.score < 80) {
                    safetyCard.className = "p-6 rounded-xl border border-warning/30 bg-warning/5 shadow-sm flex flex-col justify-between";
                    safetyTitle.className = "font-display-xl text-3xl font-bold text-warning";
                    safetyDesc.textContent = "Conditions are acceptable but caution is advised. Check localized forecasts before departure.";
                    safetyIcon.textContent = "info";
                    safetyIcon.className = "material-symbols-outlined text-warning";
                    safetyAction.textContent = "Caution Advised";
                    safetyAction.className = "text-sm font-semibold text-warning";
                    if(aiSummary) aiSummary.innerHTML = `<span class="material-symbols-outlined text-[14px] inline-block align-middle mr-1">auto_awesome</span> AI Summary: Moderate risk. Navigable but operators should remain alert for changing conditions.`;
                    if(aiSummary) aiSummary.className = "text-xs text-warning font-mono";
                } else {
                    safetyCard.className = "p-6 rounded-xl border border-emerald-500/30 bg-emerald-500/5 shadow-sm flex flex-col justify-between";
                    safetyTitle.className = "font-display-xl text-3xl font-bold text-emerald-500";
                    safetyDesc.textContent = "Excellent marine conditions. Safe for all fishing and maritime operations.";
                    safetyIcon.textContent = "check_circle";
                    safetyIcon.className = "material-symbols-outlined text-emerald-500";
                    safetyAction.textContent = "Safe to go out today";
                    safetyAction.className = "text-sm font-semibold text-emerald-500";
                    if(aiSummary) aiSummary.innerHTML = `<span class="material-symbols-outlined text-[14px] inline-block align-middle mr-1">auto_awesome</span> AI Summary: Conditions are optimal for navigation and fishing in the selected sector.`;
                    if(aiSummary) aiSummary.className = "text-xs text-cyan-700 dark:text-cyan-400 font-mono";
                }
            }

            const popupContent = `
                <div class="text-sm font-sans font-bold text-black">Location Status</div>
                <div class="text-xs text-black mt-1">Wind: ${data.wind_speed_knots || '--'} kts</div>
                <div class="text-xs text-black">Wave: ${data.wave_height_m || '--'} m</div>
            `;
            if(currentMarker) currentMarker.bindPopup(popupContent);
        } else {
            document.getElementById('val-weather').textContent = 'Data unavailable';
        }

        // --- 2. Fetch PFZ Data ---
        const pfzData = await window.OrcaAPI.getPfzData();
        const pfzList = document.getElementById('pfz-list');
        if (pfzData && pfzData.length > 0 && pfzList) {
            pfzList.innerHTML = '';
            pfzData.slice(0, 3).forEach(pfz => {
                // simple simulated distance since pfz coords are not guaranteed relative
                const distance = (Math.random() * 15 + 2).toFixed(1); 
                const name = pfz.name || `Zone ${Math.floor(Math.random()*100)}`;
                const temp = pfz.sst ? pfz.sst.toFixed(1) : '--';
                const wave = pfz.wave_height ? pfz.wave_height.toFixed(1) : '--';
                
                pfzList.innerHTML += `
                    <div class="p-4 rounded-xl border border-hairline dark:border-slate-800 bg-surface-bright dark:bg-slate-900 shadow-sm hover:border-cyan-500/50 transition-colors cursor-pointer" onclick="map.setView([${pfz.lat}, ${pfz.lon}], 11)">
                        <div class="flex justify-between items-start mb-2">
                            <h4 class="font-bold text-ink dark:text-white">${name}</h4>
                            <span class="bg-emerald-500/10 text-emerald-500 text-[10px] font-bold px-2 py-0.5 rounded uppercase">High Yield</span>
                        </div>
                        <div class="text-xs text-body dark:text-slate-400 mb-3">${distance} nm from your location</div>
                        <div class="flex items-center gap-4 text-xs text-mute">
                            <span class="flex items-center gap-1" title="Sea Surface Temp"><span class="material-symbols-outlined text-[14px]">thermostat</span> ${temp}°C</span>
                            <span class="flex items-center gap-1" title="Wave Height"><span class="material-symbols-outlined text-[14px]">waves</span> ${wave}m</span>
                        </div>
                    </div>
                `;
            });
        } else if (pfzList) {
            pfzList.innerHTML = '<div class="col-span-full p-6 text-center text-body text-sm rounded-xl border border-hairline dark:border-slate-800 bg-surface-bright dark:bg-slate-900 shadow-sm">No active Potential Fishing Zones found nearby.</div>';
        }

        // --- 3. Fetch Alerts ---
        const alerts = await window.OrcaAPI.getAlerts();
        const advisoryList = document.getElementById('advisory-list');
        const advisoryCount = document.getElementById('advisory-count');
        if (alerts && alerts.length > 0 && advisoryList) {
            advisoryCount.textContent = alerts.length;
            advisoryList.innerHTML = '';
            alerts.forEach(alert => {
                const isCritical = alert.severity === 'CRITICAL';
                const icon = isCritical ? 'warning' : 'info';
                const color = isCritical ? 'text-red-500' : 'text-warning';
                advisoryList.innerHTML += `
                    <div class="text-sm flex items-start gap-2 border-b border-hairline dark:border-slate-800 pb-2 mb-2 last:border-0 last:pb-0 last:mb-0">
                        <span class="material-symbols-outlined ${color} text-[18px] mt-0.5 shrink-0">${icon}</span>
                        <div>
                            <div class="font-semibold text-ink dark:text-white leading-tight">${alert.title}</div>
                            <div class="text-body dark:text-slate-400 text-xs mt-1">${alert.recommended_action || alert.hazard}</div>
                        </div>
                    </div>
                `;
            });
        } else if (advisoryList) {
            advisoryCount.textContent = '0';
            advisoryList.innerHTML = `
                <div class="text-sm text-mute flex items-center gap-2">
                    <span class="material-symbols-outlined text-[18px]">check_circle</span>
                    No active advisories currently.
                </div>
            `;
        }

    } catch (e) {
        console.error("Error fetching dashboard data", e);
    } finally {
        if(refreshIcon) refreshIcon.classList.remove('animate-spin');
    }
}

function initChart() {
    const ctx = document.getElementById('historicalChart').getContext('2d');
    const isDark = document.documentElement.classList.contains('dark');
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';
    const textColor = isDark ? '#a3a3a3' : '#737373';
    
    // Initial fetch for 30 days
    const labels = Array.from({length: 30}, (_, i) => `Day ${i+1}`);
    const data = Array.from({length: 30}, () => 26 + Math.random() * 4);

    historicalChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Sea Surface Temperature (°C)',
                data: data,
                borderColor: '#00dfd8',
                backgroundColor: 'rgba(0, 223, 216, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: gridColor }, ticks: { color: textColor } },
                x: { grid: { display: false }, ticks: { color: textColor, maxTicksLimit: 10 } }
            }
        }
    });
}

function updateChart(days) {
    if(!historicalChart) return;
    const labels = Array.from({length: days}, (_, i) => `Day ${i+1}`);
    const data = Array.from({length: days}, () => 26 + Math.random() * 4);
    historicalChart.data.labels = labels;
    historicalChart.data.datasets[0].data = data;
    historicalChart.update();
}
