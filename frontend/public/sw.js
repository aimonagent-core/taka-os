const CACHE_NAME = 'taka-os-v1';
const STATIC_CACHE = `${CACHE_NAME}-static`;
const API_CACHE = `${CACHE_NAME}-api`;
const IMAGE_CACHE = `${CACHE_NAME}-images`;

const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
];

// Install : precache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    }).then(() => {
      self.skipWaiting();
    })
  );
});

// Activate : cleanup old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name.startsWith('taka-os-') && name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    }).then(() => {
      self.clients.claim();
    })
  );
});

// Fetch : routing strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // API calls : Network-First
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/external/')) {
    event.respondWith(networkFirst(request, API_CACHE, 3600));
    return;
  }

  // Images : Stale-While-Revalidate
  if (request.destination === 'image') {
    event.respondWith(staleWhileRevalidate(request, IMAGE_CACHE));
    return;
  }

  // Static assets : Cache-First
  event.respondWith(cacheFirst(request, STATIC_CACHE));
});

// Strategies
async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    if (request.mode === 'navigate') {
      return cache.match('/index.html');
    }
    throw error;
  }
}

async function networkFirst(request, cacheName, maxAgeSeconds) {
  const cache = await caches.open(cacheName);

  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const responseToCache = networkResponse.clone();
      const headers = new Headers(responseToCache.headers);
      headers.set('x-cache-timestamp', Date.now().toString());

      const cachedResponse = new Response(responseToCache.body, {
        status: responseToCache.status,
        statusText: responseToCache.statusText,
        headers,
      });
      cache.put(request, cachedResponse);
    }
    return networkResponse;
  } catch (error) {
    const cached = await cache.match(request);
    if (cached) {
      const timestamp = cached.headers.get('x-cache-timestamp');
      if (timestamp) {
        const age = (Date.now() - parseInt(timestamp)) / 1000;
        if (age < maxAgeSeconds) {
          return cached;
        }
      }
    }
    return new Response(
      JSON.stringify({ error: 'Offline', message: 'Donnees non disponibles hors ligne' }),
      { status: 503, headers: { 'Content-Type': 'application/json' } }
    );
  }
}

async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);

  const fetchPromise = fetch(request).then((response) => {
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  }).catch(() => cached);

  return cached || fetchPromise;
}
