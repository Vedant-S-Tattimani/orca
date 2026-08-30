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
     * GET /api/environmental-data?lat={lat}&lon={lon}
     * Falls back to direct Open-Meteo APIs if backend is unreachable.
     */
    async getLocationEnvironmentalData(lat, lon) {
        try {
            const response = await fetch(`${API_BASE}/api/environmental-data?lat=${lat}&lon=${lon}`);
            if (response.ok) {
                return await response.json();
            }
        } catch (e) {
            console.warn('Backend environmental endpoint unavailable, falling back to direct Open-Meteo APIs:', e);
        }

        // --- Client-Side Fallback: Fetch directly from Open-Meteo APIs ---
        try {
            const weatherUrl = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&hourly=wind_speed_10m,wind_direction_10m,precipitation,weather_code,visibility&forecast_days=1`;
            const marineUrl = `https://marine-api.open-meteo.com/v1/marine?latitude=${lat}&longitude=${lon}&hourly=wave_height,swell_wave_height,ocean_current_velocity,ocean_current_direction,sea_surface_temperature&forecast_days=1`;

            const [wRes, mRes] = await Promise.allSettled([
                fetch(weatherUrl).then(r => r.ok ? r.json() : null),
                fetch(marineUrl).then(r => r.ok ? r.json() : null)
            ]);

            const wData = (wRes.status === 'fulfilled' && wRes.value) ? wRes.value : null;
            const mData = (mRes.status === 'fulfilled' && mRes.value) ? mRes.value : null;

            let wind_speed_kmh = null;
            let wind_direction_deg = null;
            let rainfall_mm = null;
            let weather_code = null;
            let weather_condition = 'Unknown';
            let visibility_km = null;

            if (wData && wData.hourly) {
                if (wData.hourly.wind_speed_10m && wData.hourly.wind_speed_10m.length > 0) {
                    wind_speed_kmh = wData.hourly.wind_speed_10m[0];
                }
                if (wData.hourly.wind_direction_10m && wData.hourly.wind_direction_10m.length > 0) {
                    wind_direction_deg = wData.hourly.wind_direction_10m[0];
                }
                if (wData.hourly.precipitation && wData.hourly.precipitation.length > 0) {
                    rainfall_mm = wData.hourly.precipitation[0];
                }
                if (wData.hourly.weather_code && wData.hourly.weather_code.length > 0) {
                    weather_code = wData.hourly.weather_code[0];
                    const wCodes = {
                        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                        45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
                        55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
                        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
                        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
                    };
                    weather_condition = wCodes[weather_code] || "Unknown";
                }
                if (wData.hourly.visibility && wData.hourly.visibility.length > 0) {
                    const visM = wData.hourly.visibility[0];
                    if (visM !== null && visM !== undefined) {
                        visibility_km = visM / 1000.0;
                    }
                }
            }

            let wave_height_m = null;
            let swell_wave_height_m = null;
            let ocean_current_speed_knots = null;
            let ocean_current_direction_deg = null;
            let sea_surface_temp_c = null;

            if (mData && mData.hourly) {
                if (mData.hourly.wave_height && mData.hourly.wave_height.length > 0) {
                    wave_height_m = mData.hourly.wave_height[0];
                }
                if (mData.hourly.swell_wave_height && mData.hourly.swell_wave_height.length > 0) {
                    swell_wave_height_m = mData.hourly.swell_wave_height[0];
                }
                if (mData.hourly.ocean_current_velocity && mData.hourly.ocean_current_velocity.length > 0) {
                    const currVel = mData.hourly.ocean_current_velocity[0];
                    if (currVel !== null && currVel !== undefined) {
                        ocean_current_speed_knots = currVel * 1.94384;
                    }
                }
                if (mData.hourly.ocean_current_direction && mData.hourly.ocean_current_direction.length > 0) {
                    ocean_current_direction_deg = mData.hourly.ocean_current_direction[0];
                }
                if (mData.hourly.sea_surface_temperature && mData.hourly.sea_surface_temperature.length > 0) {
                    sea_surface_temp_c = mData.hourly.sea_surface_temperature[0];
                }
            }

            let storm_risk = null;
            if (weather_code !== null) {
                if ([95, 96, 99].includes(weather_code)) storm_risk = "High Risk (Thunderstorm)";
                else if ([80, 81, 82, 63, 65].includes(weather_code)) storm_risk = "Moderate Risk (Heavy Rain)";
                else if ([51, 53, 55, 61].includes(weather_code)) storm_risk = "Low Risk (Light Rain)";
                else storm_risk = "Low Risk";
            }

            let fishing_safety = null;
            if (wind_speed_kmh !== null || wave_height_m !== null || weather_code !== null) {
                let score = 100;
                if (wind_speed_kmh !== null) {
                    if (wind_speed_kmh > 55) score -= 50;
                    else if (wind_speed_kmh > 37) score -= 30;
                    else if (wind_speed_kmh > 22) score -= 15;
                }
                const effWave = wave_height_m !== null ? wave_height_m : swell_wave_height_m;
                if (effWave !== null) {
                    if (effWave > 3.0) score -= 50;
                    else if (effWave > 2.0) score -= 35;
                    else if (effWave > 1.0) score -= 15;
                }
                if (weather_code !== null) {
                    if ([95, 96, 99].includes(weather_code)) score -= 45;
                    else if ([80, 81, 82, 63, 65].includes(weather_code)) score -= 25;
                    else if ([51, 53, 55, 61].includes(weather_code)) score -= 10;
                }
                if (ocean_current_speed_knots !== null) {
                    if (ocean_current_speed_knots > 2.5) score -= 25;
                    else if (ocean_current_speed_knots > 1.0) score -= 10;
                }

                score = Math.max(0, Math.min(100, score));
                let status = "Safe for Fishing";
                if (score < 50) status = "Unsafe / High Risk";
                else if (score < 80) status = "Caution Required";

                fishing_safety = { score, status };
            }

            return {
                latitude: lat,
                longitude: lon,
                timestamp: new Date().toISOString(),
                data: {
                    wind_speed_kmh: wind_speed_kmh !== null ? Number(wind_speed_kmh.toFixed(1)) : null,
                    wind_speed_knots: wind_speed_kmh !== null ? Number((wind_speed_kmh / 1.852).toFixed(1)) : null,
                    wind_direction_deg: wind_direction_deg !== null ? Number(wind_direction_deg.toFixed(1)) : null,
                    wave_height_m: wave_height_m !== null ? Number(wave_height_m.toFixed(2)) : null,
                    swell_wave_height_m: swell_wave_height_m !== null ? Number(swell_wave_height_m.toFixed(2)) : null,
                    rainfall_mm: rainfall_mm !== null ? Number(rainfall_mm.toFixed(2)) : null,
                    ocean_current_speed_knots: ocean_current_speed_knots !== null ? Number(ocean_current_speed_knots.toFixed(2)) : null,
                    ocean_current_direction_deg: ocean_current_direction_deg !== null ? Number(ocean_current_direction_deg.toFixed(1)) : null,
                    sea_surface_temp_c: sea_surface_temp_c !== null ? Number(sea_surface_temp_c.toFixed(1)) : null,
                    visibility_km: visibility_km !== null ? Number(visibility_km.toFixed(1)) : null,
                    weather_code: weather_code,
                    weather_condition: weather_condition,
                    storm_risk: storm_risk,
                    fishing_safety: fishing_safety
                },
                source: "Open-Meteo Weather & Marine API (Direct)"
            };

        } catch (err) {
            console.error('Error fetching environmental data directly:', err);
            return null;
        }
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
