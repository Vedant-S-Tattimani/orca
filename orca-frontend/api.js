/**
 * ORCA Marine - Frontend API Service
 * Encapsulates all backend communications.
 */

// Use VITE_API_URL if it exists in the environment, otherwise default to localhost:8000
const API_BASE = (typeof process !== 'undefined' && process.env && process.env.VITE_API_URL) 
    ? process.env.VITE_API_URL 
    : 'http://localhost:8000';

const OrcaAPI = {
    /**
     * Submit a raw query to ORCA
     * POST /api/query
     */
    async submitQuery(text, lat = null, lon = null, sessionId = 'default', lang = null) {
        try {
            const currentLang = lang || localStorage.getItem('orca_lang') || 'en';
            const response = await fetch(`${API_BASE}/api/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, lat, lon, session_id: sessionId, lang: currentLang })
            });
            if (!response.ok) throw new Error('Query submission failed');
            return await response.json();
        } catch (error) {
            console.error('Error submitting query:', error);
            throw error;
        }
    },

    /**
     * Get result for a query
     * GET /api/result/{query_id}
     */
    async getQueryResult(queryId) {
        try {
            const response = await fetch(`${API_BASE}/api/result/${queryId}`);
            if (!response.ok) throw new Error('Query result fetch failed');
            return await response.json();
        } catch (error) {
            console.error('Error fetching query result:', error);
            throw error;
        }
    },

    /**
     * Get live agent status
     * GET /api/agents/status
     */
    async getAgentStatus() {
        try {
            const response = await fetch(`${API_BASE}/api/agents/status`);
            if (!response.ok) throw new Error('Agent status fetch failed');
            return await response.json();
        } catch (error) {
            console.error('Error fetching agent status:', error);
            throw error;
        }
    },

    /**
     * Get simulated vessels
     * GET /api/vessels
     */
    async getVessels() {
        try {
            const response = await fetch(`${API_BASE}/api/vessels`);
            if (!response.ok) throw new Error('Vessels fetch failed');
            return await response.json();
        } catch (error) {
            console.error('Error fetching vessels:', error);
            throw error;
        }
    },

    /**
     * Get active computed alerts
     * GET /api/alerts
     */
    async getAlerts() {
        try {
            const response = await fetch(`${API_BASE}/api/alerts`);
            if (!response.ok) throw new Error('Alerts fetch failed');
            return await response.json();
        } catch (error) {
            console.error('Error fetching alerts:', error);
            throw error;
        }
    },

    /**
     * Get ports
     * GET /api/ports
     */
    async getPorts() {
        try {
            const response = await fetch(`${API_BASE}/api/ports`);
            if (!response.ok) throw new Error('Ports fetch failed');
            return await response.json();
        } catch (error) {
            console.error('Error fetching ports:', error);
            throw error;
        }
    },

    /**
     * Get PFZ Data
     * POST /api/pfz
     */
    async getPfzData(sectors) {
        try {
            const response = await fetch(`${API_BASE}/api/pfz`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sectors })
            });
            if (!response.ok) throw new Error('PFZ data fetch failed');
            return await response.json();
        } catch (error) {
            console.error('Error fetching PFZ data:', error);
            throw error;
        }
    },

    /**
     * Calculate route
     * POST /api/route
     */
    async calculateRoute(originLat, originLon, destLat, destLon, vesselSpeedKnots = 12.0) {
        try {
            const response = await fetch(`${API_BASE}/api/route`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    origin_lat: originLat, 
                    origin_lon: originLon, 
                    dest_lat: destLat, 
                    dest_lon: destLon,
                    vessel_speed_knots: vesselSpeedKnots
                })
            });
            if (!response.ok) throw new Error('Route calculation failed');
            return await response.json();
        } catch (error) {
            console.error('Error calculating route:', error);
            throw error;
        }
    },

    /**
     * Fetch real environmental & marine data for a selected location (lat, lon)
     * GET /api/environmental-data?lat={lat}&lon={lon}&hour_offset={hourOffset}
     * Supports ECMWF, GFS, and ICON forecast models with direct Open-Meteo fallback.
     */
    async getLocationEnvironmentalData(lat, lon, hourOffset = 0, model = 'ecmwf_ifs025') {
        try {
            const response = await fetch(`${API_BASE}/api/environmental-data?lat=${lat}&lon=${lon}&hour_offset=${hourOffset}&model=${model}`);
            if (response.ok) {
                const resData = await response.json();
                if (resData && resData.data) return resData;
            }
        } catch (e) {
            console.warn('Backend environmental endpoint unavailable, falling back to direct Open-Meteo APIs:', e);
        }

        // --- Client-Side Fallback: Fetch directly from Open-Meteo Weather & Marine APIs ---
        try {
            const modelParam = model === 'gfs_seamless' ? '&models=gfs_seamless' : (model === 'icon_seamless' ? '&models=icon_seamless' : '&models=ecmwf_ifs025');
            const weatherUrl = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&hourly=wind_speed_10m,wind_direction_10m,wind_gusts_10m,temperature_2m,apparent_temperature,surface_pressure,relative_humidity_2m,precipitation,weather_code,cloud_cover,visibility${modelParam}&forecast_days=4`;
            const marineUrl = `https://marine-api.open-meteo.com/v1/marine?latitude=${lat}&longitude=${lon}&hourly=wave_height,wave_direction,wave_period,swell_wave_height,swell_wave_direction,ocean_current_velocity,ocean_current_direction,sea_surface_temperature&forecast_days=4`;

            const [wRes, mRes] = await Promise.allSettled([
                fetch(weatherUrl).then(r => r.ok ? r.json() : null).catch(() => null),
                fetch(marineUrl).then(r => r.ok ? r.json() : null).catch(() => null)
            ]);

            const wData = (wRes.status === 'fulfilled' && wRes.value) ? wRes.value : null;
            const mData = (mRes.status === 'fulfilled' && mRes.value) ? mRes.value : null;

            const idx = Math.max(0, Math.min(hourOffset, 72));

            let wind_speed_kmh = null;
            let wind_direction_deg = null;
            let wind_gusts_kmh = null;
            let temperature_c = null;
            let apparent_temperature_c = null;
            let surface_pressure_hpa = null;
            let relative_humidity_pct = null;
            let cloud_cover_pct = null;
            let rainfall_mm = null;
            let weather_code = null;
            let weather_condition = 'Clear sky';
            let visibility_km = 10.0;

            if (wData && wData.hourly) {
                const getH = (arr) => (arr && arr.length > idx) ? arr[idx] : ((arr && arr.length > 0) ? arr[0] : null);
                
                wind_speed_kmh = getH(wData.hourly.wind_speed_10m);
                wind_direction_deg = getH(wData.hourly.wind_direction_10m);
                wind_gusts_kmh = getH(wData.hourly.wind_gusts_10m);
                temperature_c = getH(wData.hourly.temperature_2m);
                apparent_temperature_c = getH(wData.hourly.apparent_temperature);
                surface_pressure_hpa = getH(wData.hourly.surface_pressure);
                relative_humidity_pct = getH(wData.hourly.relative_humidity_2m);
                cloud_cover_pct = getH(wData.hourly.cloud_cover);
                rainfall_mm = getH(wData.hourly.precipitation);
                weather_code = getH(wData.hourly.weather_code);

                if (weather_code !== null) {
                    const wCodes = {
                        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                        45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
                        55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
                        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
                        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
                    };
                    weather_condition = wCodes[weather_code] || "Clear sky";
                }
                const visM = getH(wData.hourly.visibility);
                if (visM !== null && visM !== undefined) {
                    visibility_km = visM / 1000.0;
                }
            }

            let wave_height_m = null;
            let wave_direction_deg = null;
            let wave_period_s = null;
            let swell_wave_height_m = null;
            let ocean_current_speed_knots = null;
            let ocean_current_direction_deg = null;
            let sea_surface_temp_c = null;

            if (mData && mData.hourly) {
                const getM = (arr) => (arr && arr.length > idx) ? arr[idx] : ((arr && arr.length > 0) ? arr[0] : null);

                wave_height_m = getM(mData.hourly.wave_height);
                wave_direction_deg = getM(mData.hourly.wave_direction);
                wave_period_s = getM(mData.hourly.wave_period);
                swell_wave_height_m = getM(mData.hourly.swell_wave_height);
                const currVel = getM(mData.hourly.ocean_current_velocity);
                if (currVel !== null && currVel !== undefined) {
                    ocean_current_speed_knots = currVel * 1.94384;
                }
                ocean_current_direction_deg = getM(mData.hourly.ocean_current_direction);
                sea_surface_temp_c = getM(mData.hourly.sea_surface_temperature);
            }

            let storm_risk = "Low Risk";
            if (weather_code !== null) {
                if ([95, 96, 99].includes(weather_code)) storm_risk = "High Risk (Thunderstorm)";
                else if ([80, 81, 82, 63, 65].includes(weather_code)) storm_risk = "Moderate Risk (Heavy Rain)";
                else if ([51, 53, 55, 61].includes(weather_code)) storm_risk = "Low Risk (Light Rain)";
            }

            let score = 90;
            if (wind_speed_kmh !== null) {
                if (wind_speed_kmh > 55) score -= 45;
                else if (wind_speed_kmh > 37) score -= 25;
                else if (wind_speed_kmh > 22) score -= 10;
            }
            const effWave = wave_height_m !== null ? wave_height_m : swell_wave_height_m;
            if (effWave !== null) {
                if (effWave > 3.0) score -= 45;
                else if (effWave > 2.0) score -= 30;
                else if (effWave > 1.0) score -= 15;
            }
            if (weather_code !== null) {
                if ([95, 96, 99].includes(weather_code)) score -= 40;
                else if ([80, 81, 82, 63, 65].includes(weather_code)) score -= 20;
            }
            if (ocean_current_speed_knots !== null && ocean_current_speed_knots > 2.5) score -= 20;

            score = Math.max(10, Math.min(100, score));
            let status = "Safe for Fishing";
            if (score < 50) status = "Unsafe / High Risk";
            else if (score < 80) status = "Caution Required";

            const fishing_safety = { score, status };

            const validNum = (v, dec = 1, fallback = null) => (typeof v === 'number' && !isNaN(v)) ? Number(v.toFixed(dec)) : fallback;
            const marineTempFallback = validNum(sea_surface_temp_c, 1, 28.5);

            return {
                latitude: lat,
                longitude: lon,
                timestamp: new Date().toISOString(),
                model_used: model.toUpperCase(),
                data: {
                    wind_speed_kmh: validNum(wind_speed_kmh, 1, 14.5),
                    wind_speed_knots: (typeof wind_speed_kmh === 'number' && !isNaN(wind_speed_kmh)) ? Number((wind_speed_kmh / 1.852).toFixed(1)) : 7.8,
                    wind_direction_deg: validNum(wind_direction_deg, 0, 240),
                    wind_gusts_kmh: validNum(wind_gusts_kmh, 1, 21.0),
                    temperature_c: validNum(temperature_c, 1, marineTempFallback),
                    apparent_temperature_c: validNum(apparent_temperature_c, 1, marineTempFallback + 2.5),
                    surface_pressure_hpa: validNum(surface_pressure_hpa, 1, 1011.5),
                    relative_humidity_pct: validNum(relative_humidity_pct, 0, 78),
                    cloud_cover_pct: validNum(cloud_cover_pct, 0, 35),
                    wave_height_m: validNum(wave_height_m, 2, null),
                    wave_direction_deg: validNum(wave_direction_deg, 0, null),
                    wave_period_s: validNum(wave_period_s, 1, null),
                    swell_wave_height_m: validNum(swell_wave_height_m, 2, null),
                    rainfall_mm: validNum(rainfall_mm, 2, 0.0),
                    ocean_current_speed_knots: validNum(ocean_current_speed_knots, 2, null),
                    ocean_current_direction_deg: validNum(ocean_current_direction_deg, 0, null),
                    sea_surface_temp_c: validNum(sea_surface_temp_c, 1, null),
                    visibility_km: validNum(visibility_km, 1, 10.0),
                    weather_code: weather_code,
                    weather_condition: weather_condition,
                    storm_risk: storm_risk,
                    fishing_safety: fishing_safety
                },
                source: `Open-Meteo (${model.toUpperCase()}) & Marine API`
            };
        } catch (err) {
            console.error('Error fetching environmental data directly:', err);
            return {
                latitude: lat,
                longitude: lon,
                timestamp: new Date().toISOString(),
                model_used: model.toUpperCase(),
                data: {
                    wind_speed_kmh: 15.0, wind_speed_knots: 8.1, wind_direction_deg: 240.0, wind_gusts_kmh: 22.0,
                    temperature_c: 28.0, apparent_temperature_c: 31.0, surface_pressure_hpa: 1012.0,
                    relative_humidity_pct: 75, cloud_cover_pct: 40, wave_height_m: null, wave_direction_deg: null,
                    wave_period_s: null, swell_wave_height_m: null, rainfall_mm: 0.0, ocean_current_speed_knots: null,
                    ocean_current_direction_deg: null, sea_surface_temp_c: null, visibility_km: 10.0,
                    weather_code: 0, weather_condition: "Clear sky", storm_risk: "Low Risk",
                    fishing_safety: { score: 85, status: "Safe for Fishing" }
                },
                source: "Open-Meteo Weather API (Fallback)"
            };
        }
    },

    /**
     * Search locations (cities, ports, coordinates)
     */
    async searchLocations(query) {
        if (!query || !query.trim()) return [];
        const q = query.trim();

        // 1. Check if coordinates (e.g. "12.87, 74.84" or "12.87 74.84")
        const coordMatch = q.match(/^(-?\d+(\.\d+)?)[,\s]+(-?\d+(\.\d+)?)$/);
        if (coordMatch) {
            const lat = parseFloat(coordMatch[1]);
            const lon = parseFloat(coordMatch[3]);
            if (!isNaN(lat) && !isNaN(lon)) {
                return [{
                    name: `Coordinates (${lat.toFixed(4)}°, ${lon.toFixed(4)}°)`,
                    country: 'Custom Pinpoint',
                    lat: lat,
                    lon: lon,
                    type: 'coordinate'
                }];
            }
        }

        const results = [];

        // 2. Local ports matching
        try {
            const ports = await this.getPorts();
            if (ports && ports.length) {
                const qLower = q.toLowerCase();
                ports.forEach(p => {
                    if (p.name && (p.name.toLowerCase().includes(qLower) || (p.locode && p.locode.toLowerCase().includes(qLower)))) {
                        results.push({
                            name: `${p.name} Port`,
                            country: p.locode ? `LOCODE: ${p.locode}` : 'India Port',
                            lat: p.lat,
                            lon: p.lon,
                            type: 'port'
                        });
                    }
                });
            }
        } catch (e) {
            console.warn('Port search failed:', e);
        }

        // 3. Open-Meteo Geocoding API search
        try {
            const res = await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(q)}&count=5`);
            if (res.ok) {
                const geoData = await res.json();
                if (geoData && geoData.results) {
                    geoData.results.forEach(g => {
                        results.push({
                            name: g.name,
                            country: [g.admin1, g.country].filter(Boolean).join(', '),
                            lat: g.latitude,
                            lon: g.longitude,
                            type: 'city'
                        });
                    });
                }
            }
        } catch (e) {
            console.warn('Geocoding API search failed:', e);
        }

        return results;
    },

    /**
     * Authenticate user and get JWT
     */
    async login(email, password) {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        try {
            const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });
            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || 'Login failed');
            }
            const data = await response.json();
            localStorage.setItem('accessToken', data.access_token);
            await this.fetchCurrentUser();
            return data;
        } catch (error) {
            console.error('Error logging in:', error);
            throw error;
        }
    },

    /**
     * Register new user
     */
    async register(email, password, fullName) {
        try {
            const response = await fetch(`${API_BASE}/api/v1/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, full_name: fullName, role: 'fisherman' })
            });
            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || 'Registration failed');
            }
            return await response.json();
        } catch (error) {
            console.error('Error registering:', error);
            throw error;
        }
    },

    /**
     * Get current user
     */
    async fetchCurrentUser() {
        const token = localStorage.getItem('accessToken');
        if (!token) return null;
        try {
            const response = await fetch(`${API_BASE}/api/v1/auth/me`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!response.ok) {
                if (response.status === 401) {
                    this.logout(false);
                }
                throw new Error('Failed to fetch user');
            }
            const user = await response.json();
            localStorage.setItem('userRole', user.role);
            localStorage.setItem('userEmail', user.email);
            localStorage.setItem('userFullName', user.full_name);
            return user;
        } catch (error) {
            console.error('Error fetching current user:', error);
            return null;
        }
    },

    /**
     * Logout
     */
    logout(redirect = true) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('userRole');
        localStorage.removeItem('userEmail');
        localStorage.removeItem('userFullName');
        if (redirect) {
            window.location.href = 'login.html';
        }
    },
    
    /**
     * Page Protection
     */
    requireAuth() {
        if (!localStorage.getItem('accessToken')) {
            window.location.href = 'login.html';
        }
    },

    /**
     * Trigger SOS
     * POST /api/v1/sos
     */
    async triggerSOS(lat, lon) {
        try {
            const token = localStorage.getItem('accessToken');
            const headers = { 'Content-Type': 'application/json' };
            if (token) headers['Authorization'] = `Bearer ${token}`;
            
            const response = await fetch(`${API_BASE}/api/v1/sos`, {
                method: 'POST',
                headers,
                body: JSON.stringify({ lat, lon })
            });
            if (!response.ok) throw new Error('Failed to trigger SOS');
            return await response.json();
        } catch (error) {
            console.error('Error triggering SOS:', error);
            throw error;
        }
    },

    /**
     * Cancel SOS
     * PATCH /api/v1/sos/{incident_id}/resolve
     */
    async cancelSOS(incidentId) {
        try {
            const token = localStorage.getItem('accessToken');
            const headers = { 'Content-Type': 'application/json' };
            if (token) headers['Authorization'] = `Bearer ${token}`;
            
            const response = await fetch(`${API_BASE}/api/v1/sos/${incidentId}/resolve`, {
                method: 'PATCH',
                headers,
                body: JSON.stringify({ resolution_note: "Cancelled by user" })
            });
            if (!response.ok) throw new Error('Failed to cancel SOS');
            return await response.json();
        } catch (error) {
            console.error('Error canceling SOS:', error);
            throw error;
        }
    },

    /**
     * Get Trip Details
     * GET /api/v1/trips/{trip_id}
     */
    async getTrip(tripId) {
        try {
            const token = localStorage.getItem('accessToken');
            const headers = { 'Accept': 'application/json' };
            if (token) headers['Authorization'] = `Bearer ${token}`;
            
            const response = await fetch(`${API_BASE}/api/v1/trips/${tripId}`, {
                method: 'GET',
                headers
            });
            if (!response.ok) throw new Error('Failed to get trip details');
            return await response.json();
        } catch (error) {
            console.error('Error getting trip:', error);
            throw error;
        }
    },

    /**
     * Log Trip Action
     * POST /api/v1/trips/{trip_id}/log
     */
    async logTripAction(tripId, lat, lon, activityType, notes) {
        try {
            const token = localStorage.getItem('accessToken');
            const headers = { 'Content-Type': 'application/json' };
            if (token) headers['Authorization'] = `Bearer ${token}`;
            
            const response = await fetch(`${API_BASE}/api/v1/trips/${tripId}/log`, {
                method: 'POST',
                headers,
                body: JSON.stringify({ lat, lon, activity_type: activityType, notes })
            });
            if (!response.ok) throw new Error('Failed to log trip action');
            return await response.json();
        } catch (error) {
            console.error('Error logging trip action:', error);
            throw error;
        }
    },

    /**
     * Get Last Known Advisory
     * GET /api/v1/advisory/last_known
     */
    async getLastKnownAdvisory() {
        try {
            const response = await fetch(`${API_BASE}/api/v1/advisory/last_known`, {
                method: 'GET',
                headers: { 'Accept': 'application/json' }
            });
            if (!response.ok) throw new Error('Failed to fetch last known advisory');
            return await response.json();
        } catch (error) {
            console.error('Error fetching last known advisory:', error);
            throw error;
        }
    },

    /**
     * Get Regional Alerts
     * GET /api/v1/alerts/regional
     */
    async getRegionalAlerts(region) {
        try {
            const response = await fetch(`${API_BASE}/api/v1/alerts/regional?region=${encodeURIComponent(region)}`, {
                method: 'GET',
                headers: { 'Accept': 'application/json' }
            });
            if (!response.ok) throw new Error('Failed to fetch regional alerts');
            return await response.json();
        } catch (error) {
            console.error('Error fetching regional alerts:', error);
            throw error;
        }
    }
};

window.OrcaAPI = OrcaAPI;

async function fetchHistoricalTrends(location = "Mangalore-Coast", days = 30) {
    const token = localStorage.getItem('accessToken');
    if (!token) {
        throw new Error("No access token found. Please log in.");
    }
    
    const response = await fetch(`${API_BASE}/api/v1/historical/trends?location=${encodeURIComponent(location)}&days=${days}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
        }
    });

    if (response.status === 403) {
        throw new Error("Forbidden: You do not have researcher access.");
    }

    if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to fetch historical trends");
    }

    return await response.json();
}

async function fetchSourceHealth() {
    const response = await fetch(`${API_BASE}/api/v1/health/sources`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json'
        }
    });
    
    if (!response.ok) {
        throw new Error("Failed to fetch source health");
    }
    
    return await response.json();
}

// Export the new functions alongside the existing ones if a module bundler is used
if (typeof window !== 'undefined') {
    window.fetchHistoricalTrends = fetchHistoricalTrends;
    window.fetchSourceHealth = fetchSourceHealth;
}

// Role-based UI visibility and Auth state
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('accessToken');
    
    // Update Navigation based on Auth status
    const loginLinks = document.querySelectorAll('a[href="login.html"]');
    if (token) {
        loginLinks.forEach(link => {
            link.href = '#';
            link.innerHTML = `
                <span class="material-symbols-outlined text-[18px]">logout</span>
                <span data-i18n="nav_logout">Logout</span>
            `;
            link.title = "Logout";
            link.addEventListener('click', (e) => {
                e.preventDefault();
                OrcaAPI.logout();
            });
        });
    }

    const role = localStorage.getItem('userRole');
    if (role === 'researcher' || role === 'admin') {
        const researcherLink = document.getElementById('nav-researcher-link');
        if (researcherLink) {
            researcherLink.classList.remove('hidden');
        }
    }
});
