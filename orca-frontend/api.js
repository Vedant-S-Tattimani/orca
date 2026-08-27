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
    }
};

window.OrcaAPI = OrcaAPI;
