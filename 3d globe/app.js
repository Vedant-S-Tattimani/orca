/**
 * 3D Earth Globe Application
 * Powered by MapTiler SDK JS & MapTiler Cloud
 */

// ============================================================================
// MAPTILER API KEY CONFIGURATION
// Place your MapTiler Cloud API key here.
// You can get a free key at: https://cloud.maptiler.com/
// ============================================================================
const MAPTILER_API_KEY = 'uPaD3QT5o1HpHQYgYGRX';

// Set global SDK API key
if (typeof maptilersdk !== 'undefined') {
  maptilersdk.config.apiKey = MAPTILER_API_KEY;
} else {
  console.error('MapTiler SDK JS failed to load. Please check your network connection.');
}

// Global Application State & Animation Flags
let map = null;
let isUserInteracting = false;
let isPointerDown = false;
let inactivityTimer = null;
let lastAnimationTimestamp = 0;
let resumeTimestamp = 0;

// Configuration Constants
const INACTIVITY_DELAY_MS = 4000;   // 4 seconds of inactivity before auto-rotation resumes
const SECONDS_PER_REVOLUTION = 200; // Speed of full rotation (200 seconds per 360 deg)
const MAX_ZOOM_FOR_ROTATION = 5.0;  // Auto-rotation active when zoomed out (globe view)
const RAMP_IN_DURATION_MS = 1200;   // Smooth acceleration duration (1.2s) when resuming

/**
 * Initialize 3D Globe Map
 */
function initGlobe() {
  try {
    // Create MapTiler Map instance with 3D Globe projection
    map = new maptilersdk.Map({
      container: 'map',
      style: maptilersdk.MapStyle.HYBRID, // Realistic satellite imagery with geography & place labels
      projection: 'globe',               // 3D Earth Globe projection
      center: [15, 20],                  // Initial center coordinates
      zoom: 1.6,                         // Show complete Earth on load
      minZoom: 1,
      maxZoom: 20,
      pitch: 0,
      bearing: 0,
      terrain: true,                     // 3D elevation terrain data
      navigationControl: false,          // Pure minimal globe, no extra buttons
      geolocateControl: false,
      scaleControl: false
    });

    // Configure background atmosphere & space starry sky when style is loaded
    map.on('style.load', () => {
      try {
        if (typeof map.setSpace === 'function') {
          map.setSpace({
            color: '#010204',
            preset: 'milkyway'
          });
        }
      } catch (err) {
        console.warn('Space background preset configuration fallback:', err);
      }
    });

    // Start auto-rotation animation loop after initial load
    map.on('load', () => {
      setupInteractionListeners();
      requestAnimationFrame(animateGlobe);
    });

    // Handle window resizing smoothly
    window.addEventListener('resize', () => {
      if (map) map.resize();
    });

    // Reset animation timestamp on visibility change to prevent jumps after tab switching
    document.addEventListener('visibilitychange', () => {
      lastAnimationTimestamp = 0;
    });

  } catch (error) {
    console.error('Failed to initialize 3D Earth Globe:', error);
    showErrorMessage();
  }
}

/**
 * Main Frame-Rate Independent Animation Loop
 * Performs smooth, continuous auto-rotation from current camera position
 */
function animateGlobe(timestamp) {
  if (lastAnimationTimestamp === 0) {
    lastAnimationTimestamp = timestamp;
  }
  const deltaTime = timestamp - lastAnimationTimestamp;
  lastAnimationTimestamp = timestamp;

  // Auto-rotate only when user is idle and pointer is released
  if (map && !isUserInteracting && !isPointerDown) {
    const currentZoom = map.getZoom();

    // Auto-rotate when zoomed out in globe view
    if (currentZoom <= MAX_ZOOM_FOR_ROTATION) {
      // Calculate smooth ramp-in acceleration factor (0.0 to 1.0 over RAMP_IN_DURATION_MS)
      let rampFactor = 1.0;
      if (resumeTimestamp > 0) {
        const timeSinceResume = timestamp - resumeTimestamp;
        rampFactor = Math.min(1.0, timeSinceResume / RAMP_IN_DURATION_MS);
      }

      // Continuous longitude adjustment based on delta time & ramp speed
      const degreesPerMs = (360 / (SECONDS_PER_REVOLUTION * 1000)) * rampFactor;
      const degreesToRotate = degreesPerMs * deltaTime;

      const center = map.getCenter();
      center.lng = (center.lng - degreesToRotate + 360) % 360;
      if (center.lng > 180) center.lng -= 360;

      // Update position seamlessly from current location without snapping
      map.jumpTo({ center });
    }
  }

  requestAnimationFrame(animateGlobe);
}

/**
 * Comprehensive User Interaction Handling
 * Pauses rotation immediately when user clicks, drags, or zooms.
 * Resumes smooth auto-rotation from current position after 4 seconds of inactivity.
 */
function setupInteractionListeners() {
  const mapElement = document.getElementById('map');

  // Immediately stop auto-rotation on user gesture
  function stopAutoRotation() {
    isUserInteracting = true;
    resumeTimestamp = 0; // Reset ramp-in calculation

    if (inactivityTimer) {
      clearTimeout(inactivityTimer);
      inactivityTimer = null;
    }
  }

  // Schedule auto-rotation resumption after inactivity delay
  function scheduleAutoRotationResume() {
    if (inactivityTimer) {
      clearTimeout(inactivityTimer);
    }

    inactivityTimer = setTimeout(() => {
      // Only resume if user is no longer active or pressing down
      if (!isPointerDown) {
        isUserInteracting = false;
        resumeTimestamp = performance.now(); // Trigger smooth acceleration ramp
      }
    }, INACTIVITY_DELAY_MS);
  }

  // Pointer & Drag Events
  mapElement.addEventListener('pointerdown', () => {
    isPointerDown = true;
    stopAutoRotation();
  }, { passive: true });

  window.addEventListener('pointerup', () => {
    isPointerDown = false;
    scheduleAutoRotationResume();
  }, { passive: true });

  window.addEventListener('pointercancel', () => {
    isPointerDown = false;
    scheduleAutoRotationResume();
  }, { passive: true });

  // Touch interaction fallbacks
  mapElement.addEventListener('touchstart', () => {
    isPointerDown = true;
    stopAutoRotation();
  }, { passive: true });

  window.addEventListener('touchend', () => {
    isPointerDown = false;
    scheduleAutoRotationResume();
  }, { passive: true });

  // Mouse wheel / Trackpad zooming and panning
  mapElement.addEventListener('wheel', () => {
    stopAutoRotation();
    scheduleAutoRotationResume();
  }, { passive: true });

  // Keyboard controls
  window.addEventListener('keydown', () => {
    stopAutoRotation();
  }, { passive: true });

  window.addEventListener('keyup', () => {
    scheduleAutoRotationResume();
  }, { passive: true });

  // Map camera movement state events
  const mapStartEvents = ['dragstart', 'zoomstart', 'rotatestart', 'pitchstart', 'boxzoomstart'];
  mapStartEvents.forEach((evt) => {
    map.on(evt, () => {
      stopAutoRotation();
    });
  });

  const mapEndEvents = ['dragend', 'zoomend', 'rotateend', 'pitchend', 'moveend', 'boxzoomend'];
  mapEndEvents.forEach((evt) => {
    map.on(evt, () => {
      if (!isPointerDown) {
        scheduleAutoRotationResume();
      }
    });
  });
}

/**
 * Fallback error message display if MapTiler SDK fails to initialize
 */
function showErrorMessage() {
  const container = document.getElementById('map');
  if (container) {
    container.innerHTML = `
      <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh; color:#e2e8f0; font-family:sans-serif; text-align:center; padding:20px;">
        <h2 style="margin-bottom:12px; color:#f87171;">Globe Loading Error</h2>
        <p style="max-width:500px; color:#94a3b8; line-height:1.5;">
          Unable to render 3D Earth. Please check your network connection and MapTiler Cloud API Key.
        </p>
      </div>
    `;
  }
}

// Initialize application on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initGlobe);
} else {
  initGlobe();
}
