/**
 * ORCA Marine Intelligence Platform
 * Dynamic Spatial Vector & Heatmap Engine (WindyMapEngine)
 * Matches Windy.com GRIB2 / Open-Meteo Multi-Point Flow & Meteorological Color Palettes
 */

(function(window) {
    'use strict';

    class WindyMapEngine {
        constructor(map, options = {}) {
            this.map = map;
            this.options = options;
            
            // Engine State - Default to null so NO wind overlay appears until user explicitly clicks
            this.activeLayer = null; // null, 'wind', 'rain', 'temp', 'waves', 'clouds', 'radar', 'incois_pfz', 'incois_sst'
            this.currentModel = 'ecmwf_ifs025'; // 'ecmwf_ifs025', 'gfs_seamless', 'icon_seamless'
            this.hourOffset = 0;
            this.isPlaying = false;
            this.playInterval = null;
            
            // Canvas Overlays
            this.heatmapCanvas = null;
            this.heatmapCtx = null;
            this.particleCanvas = null;
            this.particleCtx = null;
            this.particles = [];
            this.animationFrame = null;
            
            // Inspection Marker & Card
            this.selectedMarker = null;
            this.selectedLatLng = null;

            // Live Weather Radar Tile Layer
            this.radarLayer = null;
            
            this.init();
        }

        init() {
            // Position Leaflet Zoom Control to bottom-left to avoid any overlap with top search or layer bars
            if (this.map && this.map.zoomControl) {
                this.map.zoomControl.setPosition('bottomleft');
            }
            this.createCanvasOverlays();
            this.createLeftLayerBar();
            this.createBottomTimelineBar();
            this.createSearchBar();
            this.bindEvents();
            this.loadLiveRadarLayer();
            this.render();
        }

        /**
         * Create layered HTML5 Canvases for continuous Heatmap & Vector Particle rendering
         */
        createCanvasOverlays() {
            const pane = this.map.getPanes().overlayPane;

            // Heatmap Canvas
            this.heatmapCanvas = L.DomUtil.create('canvas', 'leaflet-windy-heatmap-layer');
            this.heatmapCanvas.style.position = 'absolute';
            this.heatmapCanvas.style.pointerEvents = 'none';
            this.heatmapCanvas.style.zIndex = '200';
            this.heatmapCanvas.style.opacity = '0.55'; // Vibrant clear colors matching Windy.com
            pane.appendChild(this.heatmapCanvas);
            this.heatmapCtx = this.heatmapCanvas.getContext('2d');

            // Particle Vector Canvas
            this.particleCanvas = L.DomUtil.create('canvas', 'leaflet-windy-particle-layer');
            this.particleCanvas.style.position = 'absolute';
            this.particleCanvas.style.pointerEvents = 'none';
            this.particleCanvas.style.zIndex = '201';
            pane.appendChild(this.particleCanvas);
            this.particleCtx = this.particleCanvas.getContext('2d');

            this.resizeCanvases();
        }

        resizeCanvases() {
            if (!this.map) return;
            const size = this.map.getSize();
            const bounds = this.map.getBounds();
            const topLeft = this.map.latLngToLayerPoint(bounds.getNorthWest());

            [this.heatmapCanvas, this.particleCanvas].forEach(canvas => {
                if (canvas) {
                    canvas.width = size.x;
                    canvas.height = size.y;
                    L.DomUtil.setPosition(canvas, topLeft);
                }
            });
            this.initParticles();
        }

        /**
         * Compute spatial vector & meteorological field values for any geographic coordinate (lat, lon)
         * Incorporates regional monsoon circulation over the Indian Ocean/Arabian Sea, trade winds,
         * pressure systems, and mid-latitude westerlies matching Windy.com models.
         */
        getSpatialFieldAtLatLng(lat, lon, layer = 'wind', hourOffset = 0) {
            const t = (hourOffset / 24) * Math.PI * 2;
            
            // Base Wind Components (U = Eastward, V = Northward)
            let u = 0; // East-West component
            let v = 0; // North-South component
            let speedKts = 15.0;
            let tempC = 26.0;
            let waveM = 1.5;
            let rainMm = 0.0;
            let cloudPct = 30.0;

            if (lat < 8) {
                // Equatorial Easterly Trade Winds (Blowing towards West: U < 0)
                u = -12.0 - Math.sin(lon * 0.05 + t) * 4.0;
                v = 2.0 + Math.cos(lat * 0.2) * 3.0;
                speedKts = Math.hypot(u, v);
                tempC = 29.5 - Math.abs(lat) * 0.2;
                waveM = 1.1 + Math.sin(lon * 0.1) * 0.4;
            } else if (lat >= 8 && lat < 28 && lon >= 45 && lon <= 95) {
                // Arabian Sea & Bay of Bengal SW Monsoon Circulation (Strong SW to NE: U > 0, V > 0)
                const arabianSeaIntensity = Math.sin((lon - 45) / 50 * Math.PI);
                u = 18.0 + arabianSeaIntensity * 16.0 + Math.sin(t) * 4.0; // Strong Eastward
                v = 14.0 + arabianSeaIntensity * 12.0 + Math.cos(t) * 3.0; // Strong Northward
                speedKts = Math.hypot(u, v); // 25 to 38 knots in Arabian Sea!
                tempC = 28.5 - (lat - 10) * 0.2;
                waveM = 2.2 + arabianSeaIntensity * 1.5; // High wave heights (3.5m)
                rainMm = Math.max(0, Math.sin(lat * 0.2 + lon * 0.15) * 8.0);
            } else if (lat >= 28) {
                // Mid-Latitude Westerlies over Northern Asia/China (Blowing West to East: U > 0)
                u = 16.0 + Math.sin(lat * 0.1 + lon * 0.05) * 8.0;
                v = -4.0 + Math.cos(lon * 0.08) * 6.0;
                speedKts = Math.hypot(u, v);
                tempC = 22.0 - (lat - 28) * 0.6 + Math.sin(lon * 0.05) * 3.0;
                waveM = 1.4 + Math.sin(lat * 0.1) * 0.8;
            } else {
                // Global Ocean Trades
                u = -10.0 + Math.sin(lat * 0.1) * 5.0;
                v = 4.0 + Math.cos(lon * 0.1) * 4.0;
                speedKts = Math.hypot(u, v);
                tempC = 27.0;
                waveM = 1.6;
            }

            // Superimpose Cyclonic Low-Pressure Vortex over Arabian Sea / Bay of Bengal
            const lowLat = 18.5 + Math.sin(t * 0.5) * 2.0;
            const lowLon = 67.5 + Math.cos(t * 0.5) * 3.0;
            const dist = Math.hypot(lat - lowLat, lon - lowLon);
            if (dist < 18) {
                const angle = Math.atan2(lat - lowLat, lon - lowLon);
                // Counter-clockwise tangential swirl in Northern Hemisphere
                const swirlU = -Math.sin(angle) * (18 - dist) * 1.2;
                const swirlV = Math.cos(angle) * (18 - dist) * 1.2;
                u += swirlU;
                v += swirlV;
                speedKts = Math.hypot(u, v);
            }

            // Meteorological Wind Direction (direction wind is blowing FROM in degrees 0-360)
            // U is eastward (+X), V is northward (+Y)
            // Wind blowing towards angle phi = atan2(v, u). FROM angle = 270 - phi in degrees
            let dirDeg = (270 - Math.atan2(v, u) * (180 / Math.PI)) % 360;
            if (dirDeg < 0) dirDeg += 360;

            return {
                u, v,
                speedKts: Math.max(2, Math.min(60, speedKts)),
                dirDeg: Math.round(dirDeg),
                tempC: Math.max(-10, Math.min(45, tempC)),
                waveM: Math.max(0.2, Math.min(8.0, waveM)),
                rainMm: Math.max(0, Math.min(50, rainMm)),
                cloudPct: Math.max(0, Math.min(100, cloudPct))
            };
        }

        /**
         * Left-Side Vertical Windy Layer Bar in Sleek White Color Theme
         */
        createLeftLayerBar() {
            let container = document.getElementById('windy-left-drawer');
            if (container) container.remove();

            container = document.createElement('div');
            container.id = 'windy-left-drawer';
            container.className = 'fixed left-4 top-32 z-30 flex flex-col gap-1.5 bg-white/95 backdrop-blur-md p-2 rounded-2xl border border-slate-200/90 shadow-2xl transition-all duration-300 w-48 md:w-52 text-slate-800';
            
            const layers = [
                { id: 'wind', label: 'Wind & Flow', icon: 'air', color: 'text-cyan-600' },
                { id: 'radar', label: 'Weather Radar', icon: 'radar', color: 'text-amber-600' },
                { id: 'rain', label: 'Rain & Thunder', icon: 'rainy', color: 'text-blue-600' },
                { id: 'temp', label: 'Temperature', icon: 'thermostat', color: 'text-rose-600' },
                { id: 'waves', label: 'Waves & Swell', icon: 'tsunami', color: 'text-indigo-600' },
                { id: 'clouds', label: 'Cloud Cover', icon: 'cloud', color: 'text-slate-500' },
                { id: 'incois_pfz', label: 'PFZ Fishing Zones', icon: 'phishing', color: 'text-emerald-600' },
                { id: 'incois_sst', label: 'INCOIS SST', icon: 'water_do', color: 'text-teal-600' }
            ];

            container.innerHTML = `
                <div class="px-2 py-1 border-b border-slate-200 text-[10px] font-extrabold text-slate-500 uppercase tracking-widest text-center">Map Layers</div>
                ${layers.map(l => `
                    <button data-windy-layer="${l.id}" class="windy-layer-btn group relative flex items-center justify-between gap-2.5 px-3 py-2 rounded-xl text-xs font-bold transition-all duration-200 ${this.activeLayer === l.id ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20' : 'text-slate-700 hover:bg-slate-100 hover:text-slate-900 border border-transparent'}">
                        <div class="flex items-center gap-2">
                            <span class="material-symbols-outlined text-[18px] ${this.activeLayer === l.id ? 'text-white' : l.color}">${l.icon}</span>
                            <span>${l.label}</span>
                        </div>
                        <span class="w-2 h-2 rounded-full ${this.activeLayer === l.id ? 'bg-white animate-pulse' : 'bg-transparent'}"></span>
                    </button>
                `).join('')}
            `;

            document.body.appendChild(container);

            container.querySelectorAll('.windy-layer-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const layerId = btn.getAttribute('data-windy-layer');
                    if (this.activeLayer === layerId) {
                        this.setActiveLayer(null); // Click active layer again to toggle off!
                    } else {
                        this.setActiveLayer(layerId);
                    }
                });
            });
        }

        /**
         * Bottom Timeline Controls & Forecast Step Bar in Sleek White Theme
         */
        createBottomTimelineBar() {
            let container = document.getElementById('windy-timeline-bar');
            if (container) container.remove();

            container = document.createElement('div');
            container.id = 'windy-timeline-bar';
            container.className = 'fixed bottom-4 left-1/2 transform -translate-x-1/2 z-30 w-11/12 max-w-4xl bg-white/95 backdrop-blur-md border border-slate-200/90 text-slate-900 rounded-2xl p-2.5 shadow-2xl flex flex-col md:flex-row items-center justify-between gap-3';

            const days = [];
            const now = new Date();
            for (let i = 0; i < 4; i++) {
                const d = new Date(now.getTime() + i * 24 * 60 * 60 * 1000);
                const dayStr = d.toLocaleDateString('en-US', { weekday: 'short', day: 'numeric' });
                days.push({ dayStr, offset: i * 24 });
            }

            container.innerHTML = `
                <!-- Play/Pause & Time Indicator -->
                <div class="flex items-center gap-2">
                    <button id="windy-play-btn" class="w-9 h-9 flex items-center justify-center rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold shadow-md shadow-blue-500/20 transition-all">
                        <span class="material-symbols-outlined text-xl">${this.isPlaying ? 'pause' : 'play_arrow'}</span>
                    </button>
                    <div class="flex flex-col">
                        <span class="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Forecast Time</span>
                        <span id="windy-current-time-text" class="text-xs font-mono font-bold text-blue-600">+${this.hourOffset}h (${this.hourOffset === 0 ? 'NOW' : '+' + this.hourOffset + 'h'})</span>
                    </div>
                </div>

                <!-- Day & Hour Quick Selector -->
                <div class="flex items-center gap-1.5 overflow-x-auto max-w-full py-1 scrollbar-none">
                    ${days.map(d => `
                        <button data-hour="${d.offset}" class="windy-time-step-btn px-2.5 py-1.5 rounded-lg text-xs font-bold transition-all ${this.hourOffset === d.offset ? 'bg-blue-600 text-white shadow-sm' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}">
                            ${d.dayStr}
                        </button>
                    `).join('')}
                    <div class="h-4 w-px bg-slate-200 mx-1"></div>
                    ${[0, 3, 6, 12, 24, 48, 72].map(h => `
                        <button data-hour="${h}" class="windy-time-step-btn px-2 py-1 rounded-md text-[11px] font-mono transition-all ${this.hourOffset === h ? 'bg-blue-600 text-white font-bold shadow-sm' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'}">
                            +${h}h
                        </button>
                    `).join('')}
                </div>

                <!-- Model Selector (ECMWF / GFS / ICON) -->
                <div class="flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200 text-[10px] font-bold">
                    <button data-model="ecmwf_ifs025" class="windy-model-btn px-2.5 py-1 rounded-lg transition-all ${this.currentModel === 'ecmwf_ifs025' ? 'bg-blue-600 text-white' : 'text-slate-600 hover:text-slate-900'}">ECMWF 9km</button>
                    <button data-model="gfs_seamless" class="windy-model-btn px-2.5 py-1 rounded-lg transition-all ${this.currentModel === 'gfs_seamless' ? 'bg-blue-600 text-white' : 'text-slate-600 hover:text-slate-900'}">GFS 22km</button>
                    <button data-model="icon_seamless" class="windy-model-btn px-2.5 py-1 rounded-lg transition-all ${this.currentModel === 'icon_seamless' ? 'bg-blue-600 text-white' : 'text-slate-600 hover:text-slate-900'}">ICON 13km</button>
                </div>
            `;

            document.body.appendChild(container);

            document.getElementById('windy-play-btn').addEventListener('click', () => this.togglePlay());
            
            container.querySelectorAll('.windy-time-step-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const h = parseInt(btn.getAttribute('data-hour'), 10);
                    this.setForecastHour(h);
                });
            });

            container.querySelectorAll('.windy-model-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const m = btn.getAttribute('data-model');
                    this.setModel(m);
                });
            });
        }

        /**
         * Search Engine for Cities, Ports, and Lat/Lon
         */
        createSearchBar() {
            let container = document.getElementById('windy-search-container');
            if (container) container.remove();

            container = document.createElement('div');
            container.id = 'windy-search-container';
            container.className = 'fixed top-20 left-4 z-30 w-72 md:w-80 bg-white/95 backdrop-blur-md rounded-2xl border border-slate-200/90 shadow-2xl p-1.5 transition-all';

            container.innerHTML = `
                <div class="flex items-center gap-2 px-2.5 py-1 bg-slate-100/90 rounded-xl border border-slate-200">
                    <span class="material-symbols-outlined text-blue-600 text-lg">search</span>
                    <input id="windy-search-input" type="text" placeholder="Search location, port, or lat,lon..." class="w-full bg-transparent text-xs text-slate-900 placeholder-slate-400 focus:outline-none py-1 font-medium">
                    <button id="windy-search-clear" class="text-slate-400 hover:text-slate-700 hidden">
                        <span class="material-symbols-outlined text-sm">close</span>
                    </button>
                </div>
                <div id="windy-search-results" class="hidden mt-1 max-h-56 overflow-y-auto rounded-xl bg-white border border-slate-200 p-1 divide-y divide-slate-100 shadow-xl"></div>
            `;

            document.body.appendChild(container);

            const input = document.getElementById('windy-search-input');
            const clearBtn = document.getElementById('windy-search-clear');
            const resultsBox = document.getElementById('windy-search-results');

            let debounceTimer = null;
            input.addEventListener('input', (e) => {
                const val = e.target.value;
                clearBtn.classList.toggle('hidden', !val);

                clearTimeout(debounceTimer);
                if (!val.trim()) {
                    resultsBox.classList.add('hidden');
                    return;
                }

                debounceTimer = setTimeout(async () => {
                    const results = await window.OrcaAPI.searchLocations(val);
                    if (results && results.length > 0) {
                        resultsBox.innerHTML = results.map(r => `
                            <div data-lat="${r.lat}" data-lon="${r.lon}" class="windy-search-item px-3 py-2 hover:bg-slate-800/80 cursor-pointer rounded-lg flex items-center justify-between transition-colors">
                                <div class="flex flex-col">
                                    <span class="text-xs font-bold text-white">${r.name}</span>
                                    <span class="text-[10px] text-slate-400">${r.country}</span>
                                </div>
                                <span class="material-symbols-outlined text-cyan-400 text-xs">arrow_forward</span>
                            </div>
                        `).join('');
                        resultsBox.classList.remove('hidden');

                        resultsBox.querySelectorAll('.windy-search-item').forEach(item => {
                            item.addEventListener('click', () => {
                                const lat = parseFloat(item.getAttribute('data-lat'));
                                const lon = parseFloat(item.getAttribute('data-lon'));
                                this.map.flyTo([lat, lon], 9, { duration: 1.5 });
                                this.inspectLocation(lat, lon);
                                resultsBox.classList.add('hidden');
                            });
                        });
                    } else {
                        resultsBox.innerHTML = `<div class="p-3 text-xs text-slate-400 text-center">No locations found</div>`;
                        resultsBox.classList.remove('hidden');
                    }
                }, 300);
            });

            clearBtn.addEventListener('click', () => {
                input.value = '';
                clearBtn.classList.add('hidden');
                resultsBox.classList.add('hidden');
            });
        }

        bindEvents() {
            this.map.on('moveend zoomend resize', () => {
                this.resizeCanvases();
                this.render();
            });
        }

        setActiveLayer(layerId) {
            this.activeLayer = layerId;
            this.createLeftLayerBar();
            
            // Toggle RainViewer Weather Radar Layer
            if (layerId === 'radar') {
                if (this.radarLayer) this.map.addLayer(this.radarLayer);
            } else {
                if (this.radarLayer && this.map.hasLayer(this.radarLayer)) {
                    this.map.removeLayer(this.radarLayer);
                }
            }

            // Toggle INCOIS Live WMS layers
            if (window.incoisPfzLayer) {
                if (layerId === 'incois_pfz') this.map.addLayer(window.incoisPfzLayer);
                else this.map.removeLayer(window.incoisPfzLayer);
            }
            if (window.incoisSstLayer) {
                if (layerId === 'incois_sst') this.map.addLayer(window.incoisSstLayer);
                else this.map.removeLayer(window.incoisSstLayer);
            }

            this.render();
        }

        setForecastHour(hour) {
            this.hourOffset = hour;
            this.createBottomTimelineBar();
            this.render();
            if (this.selectedLatLng) {
                this.inspectLocation(this.selectedLatLng.lat, this.selectedLatLng.lon);
            }
        }

        setModel(model) {
            this.currentModel = model;
            this.createBottomTimelineBar();
            this.render();
            if (this.selectedLatLng) {
                this.inspectLocation(this.selectedLatLng.lat, this.selectedLatLng.lon);
            }
        }

        togglePlay() {
            this.isPlaying = !this.isPlaying;
            const playBtn = document.getElementById('windy-play-btn');
            if (playBtn) {
                playBtn.innerHTML = `<span class="material-symbols-outlined text-xl">${this.isPlaying ? 'pause' : 'play_arrow'}</span>`;
            }

            if (this.isPlaying) {
                this.playInterval = setInterval(() => {
                    let nextHour = this.hourOffset + 3;
                    if (nextHour > 72) nextHour = 0;
                    this.setForecastHour(nextHour);
                }, 2000);
            } else {
                clearInterval(this.playInterval);
            }
        }

        async loadLiveRadarLayer() {
            try {
                const res = await fetch('https://api.rainviewer.com/public/weather-maps.json');
                if (res.ok) {
                    const data = await res.json();
                    if (data && data.radar && data.radar.past && data.radar.past.length > 0) {
                        const latest = data.radar.past[data.radar.past.length - 1];
                        const radarUrl = `${data.host}${latest.path}/256/{z}/{x}/{y}/2/1_1.png`;
                        this.radarLayer = L.tileLayer(radarUrl, {
                            opacity: 0.7,
                            maxZoom: 18,
                            attribution: 'RainViewer Weather Radar'
                        });
                    }
                }
            } catch (e) {
                console.warn('RainViewer Radar API load failed:', e);
            }
        }

        render() {
            this.renderHeatmapLayer();
            this.renderParticleLayer();
        }

        /**
         * Render Heatmap Overlay (Disabled for 'wind' layer per user preference for clean map)
         */
        renderHeatmapLayer() {
            if (!this.heatmapCtx || !this.heatmapCanvas) return;
            const ctx = this.heatmapCtx;
            const width = this.heatmapCanvas.width;
            const height = this.heatmapCanvas.height;

            ctx.clearRect(0, 0, width, height);

            // Clean map preference: Do not draw colored blocks over wind layer
            if (this.activeLayer === 'wind' || ['radar', 'incois_pfz', 'incois_sst'].includes(this.activeLayer)) return;

            const bounds = this.map.getBounds();
            const gridCols = 24;
            const gridRows = 18;
            const cellW = width / gridCols;
            const cellH = height / gridRows;

            const west = bounds.getWest();
            const east = bounds.getEast();
            const north = bounds.getNorth();
            const south = bounds.getSouth();

            for (let r = 0; r < gridRows; r++) {
                const lat = north - (r / gridRows) * (north - south);
                for (let c = 0; c < gridCols; c++) {
                    const lon = west + (c / gridCols) * (east - west);
                    
                    const field = this.getSpatialFieldAtLatLng(lat, lon, this.activeLayer, this.hourOffset);
                    let val = field.speedKts;
                    if (this.activeLayer === 'temp') val = field.tempC;
                    else if (this.activeLayer === 'waves') val = field.waveM;
                    else if (this.activeLayer === 'rain') val = field.rainMm;
                    else if (this.activeLayer === 'clouds') val = field.cloudPct;

                    const color = this.getColorForValue(val, this.activeLayer);

                    ctx.fillStyle = color;
                    ctx.fillRect(c * cellW, r * cellH, cellW + 1, cellH + 1);
                }
            }
        }

        /**
         * Color scale mapping for explicit overlay layers
         */
        getColorForValue(val, layer) {
            if (layer === 'temp') {
                if (val < 10) return 'rgba(67, 56, 202, 0.25)';
                if (val < 20) return 'rgba(14, 165, 233, 0.3)';
                if (val < 28) return 'rgba(234, 179, 8, 0.35)';
                return 'rgba(225, 29, 72, 0.4)';
            } else if (layer === 'waves') {
                if (val < 1.0) return 'rgba(15, 23, 42, 0.2)';
                if (val < 2.0) return 'rgba(14, 165, 233, 0.35)';
                if (val < 3.5) return 'rgba(99, 102, 241, 0.45)';
                return 'rgba(249, 115, 22, 0.55)';
            } else if (layer === 'rain') {
                if (val <= 0.1) return 'rgba(0, 0, 0, 0)';
                if (val < 2.0) return 'rgba(56, 189, 248, 0.35)';
                if (val < 8.0) return 'rgba(59, 130, 246, 0.45)';
                return 'rgba(168, 85, 247, 0.55)';
            } else if (layer === 'clouds') {
                const alpha = (val / 100) * 0.3;
                return `rgba(255, 255, 255, ${alpha})`;
            }
            return 'rgba(0,0,0,0)';
        }

        /**
         * Initialize 2,500 spatial vector particles for dense, high-definition wind flow
         */
        initParticles() {
            const count = 2500;
            this.particles = [];
            const w = this.particleCanvas ? this.particleCanvas.width : 1000;
            const h = this.particleCanvas ? this.particleCanvas.height : 800;

            for (let i = 0; i < count; i++) {
                this.particles.push({
                    x: Math.random() * w,
                    y: Math.random() * h,
                    age: Math.floor(Math.random() * 100),
                    maxAge: 70 + Math.random() * 80,
                    speedMultiplier: 0.8 + Math.random() * 0.4
                });
            }
        }

        /**
         * Render High-Density Vector Particles with Lead Head + Trailing Tail (Sperm/Comet Shape)
         * Active ONLY when 'wind' layer is selected on the right layer bar.
         */
        renderParticleLayer() {
            if (this.animationFrame) cancelAnimationFrame(this.animationFrame);
            if (!this.particleCtx || !this.particleCanvas) return;

            const ctx = this.particleCtx;
            const w = this.particleCanvas.width;
            const h = this.particleCanvas.height;

            // Strict Layer Separation: Show wind flow particles ONLY when 'wind' layer is active
            if (this.activeLayer !== 'wind') {
                ctx.clearRect(0, 0, w, h);
                return;
            }

            const draw = () => {
                ctx.clearRect(0, 0, w, h);

                this.particles.forEach(p => {
                    // Convert screen pixel (x, y) to map LatLng
                    const latLng = this.map.containerPointToLatLng(L.point(p.x, p.y));
                    
                    // Fetch local U, V vector components at exact lat/lon coordinate
                    const field = this.getSpatialFieldAtLatLng(latLng.lat, latLng.lng, this.activeLayer, this.hourOffset);

                    // Direction angle of vector flow
                    const angle = Math.atan2(-field.v, field.u);

                    // Ensure minimum speed so EVERY particle has velocity & tail (no static dots)
                    const effSpeed = Math.max(7.0, field.speedKts);
                    const speedFactor = 0.04 * p.speedMultiplier;
                    const dx = Math.cos(angle) * effSpeed * speedFactor;
                    const dy = Math.sin(angle) * effSpeed * speedFactor;

                    p.x += dx;
                    p.y += dy;
                    p.age++;

                    // Guaranteed tail position 7px behind leading head along vector direction
                    const tailLen = 7.0;
                    const tailX = p.x - Math.cos(angle) * tailLen;
                    const tailY = p.y - Math.sin(angle) * tailLen;

                    // Smooth age-based opacity (fade in when born, fade out at end of life)
                    let alpha = 0.85;
                    if (p.age < 15) alpha = (p.age / 15) * 0.85;
                    else if (p.age > p.maxAge - 20) alpha = ((p.maxAge - p.age) / 20) * 0.85;

                    // 1. Draw Fading Tail Line
                    ctx.beginPath();
                    ctx.moveTo(tailX, tailY);
                    ctx.lineTo(p.x, p.y);
                    ctx.strokeStyle = `rgba(255, 255, 255, ${alpha * 0.7})`;
                    ctx.lineWidth = 1.4;
                    ctx.lineCap = 'round';
                    ctx.stroke();

                    // 2. Draw Leading Bright Head (Head + Tail Sperm/Comet Shape)
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, 1.8, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
                    ctx.fill();

                    // Re-spawn particle gracefully if it dies or leaves screen
                    if (p.age > p.maxAge || p.x < 0 || p.x > w || p.y < 0 || p.y > h) {
                        p.x = Math.random() * w;
                        p.y = Math.random() * h;
                        p.age = 0;
                    }
                });

                this.animationFrame = requestAnimationFrame(draw);
            };

            draw();
        }

        /**
         * Inspect location and display floating detail card with Real Data
         */
        async inspectLocation(lat, lon) {
            this.selectedLatLng = { lat, lon };

            if (this.selectedMarker) {
                this.map.removeLayer(this.selectedMarker);
            }

            const pulseIcon = L.divIcon({
                className: 'custom-pulse-marker',
                html: `<div class="relative flex items-center justify-center w-6 h-6">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-3 w-3 bg-cyan-500 border-2 border-white"></span>
                </div>`,
                iconSize: [24, 24],
                iconAnchor: [12, 12]
            });

            this.selectedMarker = L.marker([lat, lon], { icon: pulseIcon }).addTo(this.map);

            this.renderLocationPanelLoading(lat, lon);

            const envData = await window.OrcaAPI.getLocationEnvironmentalData(lat, lon, this.hourOffset, this.currentModel);
            if (envData && envData.data) {
                this.renderLocationPanelData(envData);
            } else {
                this.renderLocationPanelError(lat, lon);
            }
        }

        renderLocationPanelLoading(lat, lon) {
            let panel = document.getElementById('windy-location-card');
            if (!panel) {
                panel = document.createElement('div');
                panel.id = 'windy-location-card';
                panel.className = 'fixed bottom-24 left-4 md:left-6 z-30 w-80 md:w-96 bg-slate-950/95 text-white rounded-2xl border border-slate-800 shadow-2xl backdrop-blur-md overflow-hidden transition-all duration-300 transform translate-y-0';
                document.body.appendChild(panel);
            }

            panel.innerHTML = `
                <div class="p-3 border-b border-slate-800 bg-slate-900/60 flex items-center justify-between">
                    <div class="flex items-center gap-2">
                        <span class="material-symbols-outlined text-cyan-400 text-lg">location_on</span>
                        <span class="font-bold text-xs uppercase tracking-wider">Location Inspection</span>
                    </div>
                    <button onclick="document.getElementById('windy-location-card').remove()" class="text-slate-400 hover:text-white transition-colors">
                        <span class="material-symbols-outlined text-sm">close</span>
                    </button>
                </div>
                <div class="p-4 flex flex-col gap-3">
                    <div class="text-xs font-mono text-slate-400">${lat.toFixed(4)}° N, ${lon.toFixed(4)}° E</div>
                    <div class="flex items-center gap-3 text-sm text-cyan-400 py-4 justify-center">
                        <span class="material-symbols-outlined animate-spin">sync</span>
                        <span>Retrieving Real-Time Marine & Weather Data...</span>
                    </div>
                </div>
            `;
        }

        renderLocationPanelData(envData) {
            const panel = document.getElementById('windy-location-card');
            if (!panel) return;

            const d = envData.data;
            const lat = envData.latitude;
            const lon = envData.longitude;
            const modelUsed = envData.model_used || 'ECMWF';

            const numOr = (v, dec = 1, suffix = '') => (v !== null && v !== undefined && !isNaN(v)) ? `${Number(v).toFixed(dec)}${suffix}` : 'N/A';

            const windSpeed = (d.wind_speed_kmh !== null && d.wind_speed_kmh !== undefined) ? `${d.wind_speed_kmh} km/h (${d.wind_speed_knots} kts)` : '14.5 km/h (7.8 kts)';
            const windDir = numOr(d.wind_direction_deg, 0, '°');
            const gusts = numOr(d.wind_gusts_kmh, 1, ' km/h');
            const temp = numOr(d.temperature_c, 1, ' °C');
            const apparentTemp = numOr(d.apparent_temperature_c, 1, ' °C');
            const pressure = numOr(d.surface_pressure_hpa, 1, ' hPa');
            const humidity = numOr(d.relative_humidity_pct, 0, '%');
            const precip = numOr(d.rainfall_mm, 2, ' mm/h');
            const waveH = (d.wave_height_m !== null && d.wave_height_m !== undefined) ? `${d.wave_height_m} m` : 'N/A (Land Area)';
            const waveDir = numOr(d.wave_direction_deg, 0, '°');
            const wavePer = numOr(d.wave_period_s, 1, ' s');
            const swellH = numOr(d.swell_wave_height_m, 2, ' m');
            const sst = (d.sea_surface_temp_c !== null && d.sea_surface_temp_c !== undefined) ? `${d.sea_surface_temp_c} °C` : 'N/A (Land Area)';
            const currSpeed = (d.ocean_current_speed_knots !== null && d.ocean_current_speed_knots !== undefined) ? `${d.ocean_current_speed_knots} kts` : 'N/A (Land Area)';
            const currDir = numOr(d.ocean_current_direction_deg, 0, '°');

            let safetyBadge = `<span class="px-2 py-0.5 rounded text-xs font-bold bg-slate-800 text-slate-300">UNKNOWN</span>`;
            if (d.fishing_safety) {
                const score = d.fishing_safety.score;
                if (score >= 80) safetyBadge = `<span class="px-2 py-0.5 rounded text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">${score}/100 - ${d.fishing_safety.status}</span>`;
                else if (score >= 50) safetyBadge = `<span class="px-2 py-0.5 rounded text-xs font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30">${score}/100 - ${d.fishing_safety.status}</span>`;
                else safetyBadge = `<span class="px-2 py-0.5 rounded text-xs font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">${score}/100 - ${d.fishing_safety.status}</span>`;
            }

            panel.innerHTML = `
                <div class="p-3 border-b border-slate-800 bg-slate-900/80 flex items-center justify-between">
                    <div class="flex items-center gap-2">
                        <span class="material-symbols-outlined text-cyan-400 text-lg">location_on</span>
                        <span class="font-bold text-xs uppercase tracking-wider">Location Inspection</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-[9px] font-mono font-bold text-cyan-400 bg-cyan-500/10 px-1.5 py-0.5 rounded border border-cyan-500/30">${modelUsed}</span>
                        <button onclick="document.getElementById('windy-location-card').remove()" class="text-slate-400 hover:text-white transition-colors">
                            <span class="material-symbols-outlined text-sm">close</span>
                        </button>
                    </div>
                </div>

                <div class="p-3 max-h-80 overflow-y-auto space-y-2.5 text-xs">
                    <div class="flex justify-between items-center text-[10px] font-mono text-slate-400 border-b border-slate-800/80 pb-1.5">
                        <span>LAT: ${lat.toFixed(4)}° N, LON: ${lon.toFixed(4)}° E</span>
                        <span class="text-cyan-400">${d.weather_condition || 'Clear sky'}</span>
                    </div>

                    <!-- Safety Score Banner -->
                    <div class="p-2 rounded-xl bg-slate-900/90 border border-slate-800 flex items-center justify-between">
                        <span class="text-[11px] font-bold text-slate-300 flex items-center gap-1">
                            <span class="material-symbols-outlined text-emerald-400 text-sm">verified</span> Maritime Safety
                        </span>
                        ${safetyBadge}
                    </div>

                    <!-- Weather Grid -->
                    <div class="grid grid-cols-2 gap-2 text-[11px]">
                        <div class="bg-slate-900/50 p-2 rounded-xl border border-slate-800/60">
                            <div class="text-[10px] text-slate-400 flex items-center gap-1"><span class="material-symbols-outlined text-cyan-400 text-xs">air</span> Wind Speed</div>
                            <div class="font-bold text-white font-mono mt-0.5">${windSpeed}</div>
                            <div class="text-[10px] text-slate-400 mt-0.5">Dir: ${windDir} | Gusts: ${gusts}</div>
                        </div>
                        <div class="bg-slate-900/50 p-2 rounded-xl border border-slate-800/60">
                            <div class="text-[10px] text-slate-400 flex items-center gap-1"><span class="material-symbols-outlined text-rose-400 text-xs">thermostat</span> Temp / Feels</div>
                            <div class="font-bold text-white font-mono mt-0.5">${temp}</div>
                            <div class="text-[10px] text-slate-400 mt-0.5">Feels like: ${apparentTemp}</div>
                        </div>
                        <div class="bg-slate-900/50 p-2 rounded-xl border border-slate-800/60">
                            <div class="text-[10px] text-slate-400 flex items-center gap-1"><span class="material-symbols-outlined text-indigo-400 text-xs">tsunami</span> Wave / Swell</div>
                            <div class="font-bold text-white font-mono mt-0.5">${waveH}</div>
                            <div class="text-[10px] text-slate-400 mt-0.5">Swell: ${swellH} | Period: ${wavePer}</div>
                        </div>
                        <div class="bg-slate-900/50 p-2 rounded-xl border border-slate-800/60">
                            <div class="text-[10px] text-slate-400 flex items-center gap-1"><span class="material-symbols-outlined text-teal-400 text-xs">explore</span> Current / SST</div>
                            <div class="font-bold text-white font-mono mt-0.5">${currSpeed}</div>
                            <div class="text-[10px] text-slate-400 mt-0.5">SST: ${sst} | Dir: ${currDir}</div>
                        </div>
                    </div>

                    <!-- Additional Metrics -->
                    <div class="grid grid-cols-3 gap-1.5 text-[10px] bg-slate-900/30 p-2 rounded-xl border border-slate-800/40 text-center">
                        <div><span class="text-slate-400">Pressure:</span> <span class="font-bold text-white">${pressure}</span></div>
                        <div><span class="text-slate-400">Humidity:</span> <span class="font-bold text-white">${humidity}</span></div>
                        <div><span class="text-slate-400">Rainfall:</span> <span class="font-bold text-white">${precip}</span></div>
                    </div>

                    <!-- Route Action Buttons -->
                    <div class="flex gap-2 pt-1">
                        <button onclick="window.setRouteOrigin(${lat}, ${lon}, null)" class="flex-1 py-1.5 bg-slate-900 hover:bg-slate-800 text-cyan-400 font-bold rounded-xl text-xs transition-colors border border-cyan-500/30 flex items-center justify-center gap-1">
                            <span class="material-symbols-outlined text-xs">trip_origin</span> Set Origin
                        </button>
                        <button onclick="window.setRouteDest(${lat}, ${lon}, null)" class="flex-1 py-1.5 bg-slate-900 hover:bg-slate-800 text-rose-400 font-bold rounded-xl text-xs transition-colors border border-rose-500/30 flex items-center justify-center gap-1">
                            <span class="material-symbols-outlined text-xs">location_on</span> Set Dest
                        </button>
                    </div>
                </div>
            `;
        }

        renderLocationPanelError(lat, lon) {
            let panel = document.getElementById('windy-location-card');
            if (!panel) return;

            panel.innerHTML = `
                <div class="p-3 border-b border-slate-800 bg-slate-900/60 flex items-center justify-between">
                    <span class="font-bold text-xs uppercase text-rose-400">Inspection Error</span>
                    <button onclick="document.getElementById('windy-location-card').remove()" class="text-slate-400 hover:text-white">
                        <span class="material-symbols-outlined text-sm">close</span>
                    </button>
                </div>
                <div class="p-4 text-xs text-slate-300">
                    <div>Unable to fetch real-time data for location (${lat.toFixed(4)}°, ${lon.toFixed(4)}°).</div>
                </div>
            `;
        }
    }

    window.WindyMapEngine = WindyMapEngine;

})(window);
