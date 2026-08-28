/**
 * 3D Earth Globe Application
 * Supports MapTiler SDK JS & MapLibre GL 3D Globe with Deep Location Zooming
 */

// MapTiler API Key provided by user
let MAPTILER_API_KEY = '0YSu8AQQixtJloXET7Ro';

let map = null;
let isUserInteracting = false;
let isPointerDown = false;
let inactivityTimer = null;
let lastAnimationTimestamp = 0;
let resumeTimestamp = 0;

const INACTIVITY_DELAY_MS = 4000;
const SECONDS_PER_REVOLUTION = 200;
const MAX_ZOOM_FOR_ROTATION = 5.0;
const RAMP_IN_DURATION_MS = 1200;

// High-resolution Satellite + Vector Labels style (Zoomable up to zoom 20, 100% free)
const fallbackStyle = {
  version: 8,
  sources: {
    'esri-satellite': {
      type: 'raster',
      tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],
      tileSize: 256,
      maxzoom: 20
    },
    'carto-labels': {
      type: 'raster',
      tiles: ['https://basemaps.cartocdn.com/rastertiles/voyager_only_labels/{z}/{x}/{y}{r}.png'],
      tileSize: 256,
      maxzoom: 20
    }
  },
  layers: [
    { id: 'esri-satellite-layer', type: 'raster', source: 'esri-satellite', minzoom: 0, maxzoom: 20 },
    { id: 'carto-labels-layer', type: 'raster', source: 'carto-labels', minzoom: 0, maxzoom: 20 }
  ]
};

function initGlobe() {
  const container = document.getElementById('map');
  if (!container) return;

  // Try MapTiler SDK if key is configured, otherwise fallback to MapLibre GL JS
  let useMapTiler = typeof maptilersdk !== 'undefined' && MAPTILER_API_KEY && MAPTILER_API_KEY.trim() !== '';

  if (useMapTiler) {
    try {
      maptilersdk.config.apiKey = MAPTILER_API_KEY;
      map = new maptilersdk.Map({
        container: 'map',
        style: maptilersdk.MapStyle.HYBRID,
        projection: 'globe',
        center: [55, 15], // Positioned slightly to the right side
        zoom: 1.8,
        minZoom: 1,
        maxZoom: 20,
        pitch: 0,
        bearing: 0,
        terrain: true,
        navigationControl: false,
        geolocateControl: false,
        scaleControl: false
      });

      let hasErrored = false;
      map.on('error', (e) => {
        if (!hasErrored && e && e.error && (e.error.status === 403 || e.error.status === 401)) {
          hasErrored = true;
          console.warn('MapTiler key unauthorized (403). Falling back to free MapLibre 3D Globe...');
          try { map.remove(); } catch(err){}
          initMapLibreGlobe();
        }
      });

      map.on('style.load', () => {
        try {
          if (typeof map.setSpace === 'function') {
            map.setSpace({ color: '#010204', preset: 'milkyway' });
          }
        } catch (err) {}
      });

      map.on('load', () => {
        setupInteractionListeners();
        requestAnimationFrame(animateGlobe);
      });
      return;
    } catch (e) {
      console.warn('MapTiler init failed, falling back to MapLibre:', e);
    }
  }

  initMapLibreGlobe();
}

function initMapLibreGlobe() {
  if (typeof maplibregl === 'undefined') {
    console.error('MapLibre GL JS not loaded.');
    return;
  }

  try {
    map = new maplibregl.Map({
      container: 'map',
      style: fallbackStyle,
      projection: 'globe',
      center: [55, 15], // Positioned slightly to the right side
      zoom: 1.8,
      minZoom: 1,
      maxZoom: 20,
      pitch: 0,
      bearing: 0,
      attributionControl: false
    });

    map.on('load', () => {
      setupInteractionListeners();
      requestAnimationFrame(animateGlobe);
    });

    window.addEventListener('resize', () => {
      if (map) map.resize();
    });
  } catch (err) {
    console.error('Failed to initialize 3D Globe:', error);
  }
}

function animateGlobe(timestamp) {
  if (lastAnimationTimestamp === 0) {
    lastAnimationTimestamp = timestamp;
  }
  const deltaTime = timestamp - lastAnimationTimestamp;
  lastAnimationTimestamp = timestamp;

  if (map && !isUserInteracting && !isPointerDown) {
    const currentZoom = map.getZoom();
    if (currentZoom <= MAX_ZOOM_FOR_ROTATION) {
      let rampFactor = 1.0;
      if (resumeTimestamp > 0) {
        const timeSinceResume = timestamp - resumeTimestamp;
        rampFactor = Math.min(1.0, timeSinceResume / RAMP_IN_DURATION_MS);
      }

      const degreesPerMs = (360 / (SECONDS_PER_REVOLUTION * 1000)) * rampFactor;
      const degreesToRotate = degreesPerMs * deltaTime;

      const center = map.getCenter();
      center.lng = (center.lng - degreesToRotate + 360) % 360;
      if (center.lng > 180) center.lng -= 360;

      map.jumpTo({ center });
    }
  }

  requestAnimationFrame(animateGlobe);
}

function setupInteractionListeners() {
  const mapElement = document.getElementById('map');
  if (!mapElement || !map) return;

  function stopAutoRotation() {
    isUserInteracting = true;
    resumeTimestamp = 0;
    if (inactivityTimer) {
      clearTimeout(inactivityTimer);
      inactivityTimer = null;
    }
  }

  function scheduleAutoRotationResume() {
    if (inactivityTimer) clearTimeout(inactivityTimer);
    inactivityTimer = setTimeout(() => {
      if (!isPointerDown) {
        isUserInteracting = false;
        resumeTimestamp = performance.now();
      }
    }, INACTIVITY_DELAY_MS);
  }

  mapElement.addEventListener('pointerdown', () => {
    isPointerDown = true;
    stopAutoRotation();
  }, { passive: true });

  window.addEventListener('pointerup', () => {
    isPointerDown = false;
    scheduleAutoRotationResume();
  }, { passive: true });

  mapElement.addEventListener('wheel', () => {
    stopAutoRotation();
    scheduleAutoRotationResume();
  }, { passive: true });

  const mapStartEvents = ['dragstart', 'zoomstart', 'rotatestart', 'pitchstart'];
  mapStartEvents.forEach((evt) => {
    map.on(evt, () => stopAutoRotation());
  });

  const mapEndEvents = ['dragend', 'zoomend', 'rotateend', 'pitchend', 'moveend'];
  mapEndEvents.forEach((evt) => {
    map.on(evt, () => {
      if (!isPointerDown) scheduleAutoRotationResume();
    });
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initGlobe);
} else {
  initGlobe();
}
