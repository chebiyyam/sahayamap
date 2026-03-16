const CACHE_NAME = 'sahayamap-v1';
const ASSETS = [
    '/',
    '/safety',
    '/relief',
    '/static/manifest.json',
    '/static/icon-192.png',
    '/static/icon-512.png',
    'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
    'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
];

// Install — cache all assets
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
    );
});

// Activate — clean old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
        )
    );
});

// Fetch — serve from cache if offline
self.addEventListener('fetch', event => {
    // For API calls (submit, reports) — network only, don't cache
    if (event.request.url.includes('/submit') ||
        event.request.url.includes('/reports') ||
        event.request.url.includes('/relief_data') ||
        event.request.url.includes('/submit_relief')) {
        event.respondWith(
            fetch(event.request).catch(() =>
                new Response(JSON.stringify({
                    success: false,
                    offline: true,
                    message: 'You are offline. Report will be saved when connection returns.'
                }), { headers: { 'Content-Type': 'application/json' } })
            )
        );
        return;
    }

    // For everything else — cache first, network fallback
    event.respondWith(
        caches.match(event.request).then(cached => {
            return cached || fetch(event.request).then(response => {
                return caches.open(CACHE_NAME).then(cache => {
                    cache.put(event.request, response.clone());
                    return response;
                });
            });
        }).catch(() => caches.match('/'))
    );
});