// Service Worker for Clearance Genie PWA
const CACHE_NAME = 'clearance-genie-v1';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './manifest.json',
  'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js'
  // Note: opencv.js (7.69 MB) is excluded from cache due to size
  // It relies on browser caching and CDN fallback instead
];

// Install event - cache assets
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...');
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
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter(cacheName => cacheName !== CACHE_NAME)
          .map((cacheName) => {
            console.log('Service Worker: Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          })
      );
    }).then(() => self.clients.claim())
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
          // Don't cache if not a valid response (allow 200-299 status codes)
          if (!response || response.status < 200 || response.status >= 300) {
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
