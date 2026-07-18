/* ============================================
   Searcher Browser — Service Worker
   Provides offline caching & PWA installability
   ============================================ */

const CACHE_NAME = 'searcher-mobile-v1';
const OFFLINE_URL = 'offline.html';

const ASSETS_TO_CACHE = [
    './',
    'index.html',
    'style.css',
    'app.js',
    'manifest.json',
    'offline.html',
    'icons/icon-192.png',
    'icons/icon-512.png',
];

// ==========================================
// INSTALL — Cache critical assets
// ==========================================
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[SW] Caching app shell');
                return cache.addAll(ASSETS_TO_CACHE);
            })
            .then(() => self.skipWaiting())
    );
});

// ==========================================
// ACTIVATE — Clean old caches
// ==========================================
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((name) => name !== CACHE_NAME)
                    .map((name) => {
                        console.log('[SW] Removing old cache:', name);
                        return caches.delete(name);
                    })
            );
        }).then(() => self.clients.claim())
    );
});

// ==========================================
// FETCH — Cache-first for app shell, network-first for others
// ==========================================
self.addEventListener('fetch', (event) => {
    // Only handle GET requests
    if (event.request.method !== 'GET') return;

    const url = new URL(event.request.url);

    // For same-origin app shell assets, use cache-first
    if (url.origin === self.location.origin) {
        event.respondWith(
            caches.match(event.request)
                .then((cached) => {
                    if (cached) {
                        // Return cached version, but also update cache in background
                        const fetchPromise = fetch(event.request).then((response) => {
                            if (response && response.status === 200) {
                                const clone = response.clone();
                                caches.open(CACHE_NAME).then((cache) => {
                                    cache.put(event.request, clone);
                                });
                            }
                            return response;
                        }).catch(() => { /* ignore network errors */ });

                        return cached;
                    }

                    // Not cached — try network
                    return fetch(event.request)
                        .then((response) => {
                            if (response && response.status === 200) {
                                const clone = response.clone();
                                caches.open(CACHE_NAME).then((cache) => {
                                    cache.put(event.request, clone);
                                });
                            }
                            return response;
                        })
                        .catch(() => {
                            // If it's a navigation request, show offline page
                            if (event.request.mode === 'navigate') {
                                return caches.match(OFFLINE_URL);
                            }
                        });
                })
        );
    } else {
        // For external requests, try network first, fall back to offline page for navigations
        event.respondWith(
            fetch(event.request)
                .catch(() => {
                    if (event.request.mode === 'navigate') {
                        return caches.match(OFFLINE_URL);
                    }
                })
        );
    }
});
