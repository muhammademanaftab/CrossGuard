/**
 * Service Worker for PWA
 * Real-world service worker implementation
 *
 * Expected features: serviceworkers, promises, fetch, cache-api,
 * async-functions, const, let, arrow-functions, json, es6
 */

const CACHE_NAME = 'app-cache-v1';
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/styles.css',
    '/app.js',
    '/offline.html'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys()
            .then(keys => {
                return Promise.all(
                    keys
                        .filter(key => key !== CACHE_NAME)
                        .map(key => {
                            console.log(`Deleting old cache: ${key}`);
                            return caches.delete(key);
                        })
                );
            })
            .then(() => self.clients.claim())
    );
});

// Fetch event - network first, fallback to cache
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') return;

    // API requests - network only
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(request)
                .then(response => {
                    // Cache successful API responses briefly
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open('api-cache').then(cache => {
                            cache.put(request, clone);
                        });
                    }
                    return response;
                })
                .catch(() => caches.match(request))
        );
        return;
    }

    // Static assets - cache first
    event.respondWith(
        caches.match(request)
            .then(cached => {
                if (cached) {
                    // Update cache in background
                    fetch(request).then(response => {
                        if (response.ok) {
                            caches.open(CACHE_NAME).then(cache => {
                                cache.put(request, response);
                            });
                        }
                    });
                    return cached;
                }

                return fetch(request)
                    .then(response => {
                        if (!response.ok) throw new Error('Network error');
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then(cache => {
                            cache.put(request, clone);
                        });
                        return response;
                    })
                    .catch(() => {
                        // Fallback for navigation requests
                        if (request.mode === 'navigate') {
                            return caches.match('/offline.html');
                        }
                    });
            })
    );
});

// Push notification event
self.addEventListener('push', (event) => {
    const data = event.data?.json() || {};
    const options = {
        body: data.body || 'New notification',
        icon: '/icon-192.png',
        badge: '/badge.png',
        data: { url: data.url || '/' }
    };

    event.waitUntil(
        self.registration.showNotification(data.title || 'App', options)
    );
});

// Notification click
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    const url = event.notification.data?.url || '/';

    event.waitUntil(
        clients.matchAll({ type: 'window' })
            .then(windowClients => {
                // Focus existing window if available
                for (const client of windowClients) {
                    if (client.url === url && 'focus' in client) {
                        return client.focus();
                    }
                }
                // Open new window
                if (clients.openWindow) {
                    return clients.openWindow(url);
                }
            })
    );
});

// Background sync
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-data') {
        event.waitUntil(syncPendingData());
    }
});

async function syncPendingData() {
    const db = await openDB();
    const pending = await db.getAll('pending-sync');

    for (const item of pending) {
        try {
            const response = await fetch(item.url, {
                method: item.method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(item.data)
            });

            if (response.ok) {
                await db.delete('pending-sync', item.id);
            }
        } catch (error) {
            console.error('Sync failed:', error);
        }
    }
}

// Message handler for communication with main thread
self.addEventListener('message', (event) => {
    if (event.data?.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});
