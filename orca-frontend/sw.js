const CACHE_NAME = 'orca-marine-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/index.html',
  '/dashboard.html',
  '/fishing.html',
  '/assistant.html',
  '/map.html',
  '/researcher.html',
  '/api.js',
  '/i18n.js',
  '/tts.js',
  '/stt.js',
  '/manifest.json',
  '/logo.png',
  '/logo-white.png',
  '/favicon.png',
  '/favicon.ico'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(ASSETS_TO_CACHE);
      })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  if (url.pathname.startsWith('/api/') && event.request.method === 'GET') {
    // Stale-While-Revalidate for API GET calls
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        const fetchPromise = fetch(event.request).then((networkResponse) => {
          if (networkResponse.ok) {
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, networkResponse.clone()));
          }
          return networkResponse;
        }).catch(() => {
          // If network fails, just rely on cache
        });
        return cachedResponse || fetchPromise;
      })
    );
  } else if (event.request.method !== 'GET') {
    // Cannot cache POST/PUT/DELETE out of the box, just fetch
    // A full IndexedDB background sync could be added here
    event.respondWith(fetch(event.request).catch(err => {
      if(event.request.url.includes('/api/query')) {
        return new Response(JSON.stringify({
            risk_level: "offline", 
            recommendation: "CRITICAL: You are offline — no live data available. Do NOT rely on cached or generic responses for safety or navigation decisions. Data could not be verified.",
            reasoning: "The device is currently offline and unable to reach the ORCA servers to assess live marine conditions, PFZ, or weather data. Please restore connectivity for a live safety assessment."
        }), { headers: { 'Content-Type': 'application/json' }});
      }
      throw err;
    }));
  } else {
    // Cache first for static assets, fallback to network
    event.respondWith(
      caches.match(event.request).then((response) => {
        return response || fetch(event.request).then(networkResponse => {
            if (networkResponse && networkResponse.status === 200) {
                const responseToCache = networkResponse.clone();
                caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseToCache));
            }
            return networkResponse;
        });
      })
    );
  }
});
