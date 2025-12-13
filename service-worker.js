// ==========================================
// Service Worker for Clearance Genie PWA
// ==========================================
//
// MANUAL CACHE BUSTER INSTRUCTIONS:
// ==================================
// To force all users to update to the latest version:
//
// 1. Increment the CACHE_VERSION number below (e.g., '2.0.0' → '2.0.1')
// 2. Update the same version in index.html:
//    - Line ~11: manifest.json?v=X.X.X
//    - Line ~1372: service-worker.js?v=X.X.X
// 3. Deploy the updated files
//
// How it works:
// - When CACHE_VERSION changes, old caches are automatically deleted
// - Users will be forced to reload and get the latest version
// - The page will automatically reload when the new service worker activates
//
// Version History:
// - v2.0.0: Added manual cache buster system
// - v1.0.0: Initial release
// ==========================================

const CACHE_VERSION = '2.1.0';
const CACHE_NAME = `clearance-genie-v${CACHE_VERSION}`;
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './manifest.json',
  './apriltag.js',
  './apriltag-families/16h5.json',
  './apriltag-families/25h9.json',
  './apriltag-families/36h10.json',
  './apriltag-families/36h11.json',
  './apriltag-families/36h9.json',
  'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js'
  // Note: opencv.js (7.69 MB) is excluded from cache due to size
  // It relies on browser caching and CDN fallback instead
];

// Install event - cache assets
self.addEventListener('install', (event) => {
  console.log(`Service Worker: Installing version ${CACHE_VERSION}...`);
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Caching assets');
        // Try to cache all assets atomically first
        return cache.addAll(ASSETS_TO_CACHE)
          .then(() => {
            console.log('All assets cached successfully');
          })
          .catch((err) => {
            // If atomic caching fails (e.g., CORS issues), cache individually
            console.log('Atomic caching failed, trying individual caching:', err);
            return Promise.allSettled(
              ASSETS_TO_CACHE.map(url =>
                cache.add(url)
                  .then(() => {
                    console.log(`Cached: ${url}`);
                    return true;
                  })
                  .catch(err => {
                    console.log(`Failed to cache ${url}:`, err);
                    return false;
                  })
              )
            );
          });
      })
      .then(() => {
        console.log(`Service Worker: Skipping waiting for version ${CACHE_VERSION}`);
        return self.skipWaiting();
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log(`Service Worker: Activating version ${CACHE_VERSION}...`);
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      const oldCaches = cacheNames.filter(cacheName => cacheName !== CACHE_NAME);
      if (oldCaches.length > 0) {
        console.log(`Service Worker: Deleting ${oldCaches.length} old cache(s):`, oldCaches);
      }
      return Promise.all(
        oldCaches.map((cacheName) => {
          console.log(`Service Worker: Deleting cache: ${cacheName}`);
          return caches.delete(cacheName);
        })
      );
    }).then(() => {
      console.log(`Service Worker: Version ${CACHE_VERSION} now active and controlling all clients`);
      return self.clients.claim();
    })
  );
});

// Fetch event - serve from cache when available, fallback to network
self.addEventListener('fetch', (event) => {
  // Skip chrome-extension and other non-http(s) requests
  if (!event.request.url.startsWith('http')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached response if found
        if (response) {
          return response;
        }
        
        // Otherwise fetch from network
        return fetch(event.request).then((response) => {
          // Cache successful responses (2xx) and redirects (3xx), but not errors (4xx, 5xx)
          if (response.status >= 400) {
            return response;
          }

          // Clone the response as it can only be consumed once
          const responseToCache = response.clone();

          // Cache successful GET requests (async, doesn't block response)
          if (event.request.method === 'GET') {
            caches.open(CACHE_NAME).then((cache) => {
              return cache.put(event.request, responseToCache);
            }).catch((err) => {
              console.log('Failed to cache response:', err);
            });
          }

          return response;
        }).catch((error) => {
          console.log('Fetch failed:', error);
          // Return a basic error response when both network and cache fail
          return new Response('Offline - Resource not available', {
            status: 503,
            statusText: 'Service Unavailable',
            headers: new Headers({ 'Content-Type': 'text/plain' })
          });
        });
      })
  );
});
