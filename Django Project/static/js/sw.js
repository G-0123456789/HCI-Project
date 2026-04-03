/**
 * sw.js — Service Worker for CityMender SA
 * Caches app shell for offline use.
 */
const CACHE_NAME  = 'citymender-v1';
const STATIC_URLS = [
  '/',
  '/map/',
  '/hub/',
  '/static/css/main.css',
  '/static/js/app.js',
  '/static/js/voice.js',
  '/static/js/offline.js',
  'https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap',
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return Promise.allSettled(STATIC_URLS.map(url => cache.add(url).catch(() => {})));
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const { request } = e;

  // Never intercept POST requests or API calls
  if (request.method !== 'GET') return;
  if (request.url.includes('/api/')) return;
  if (request.url.includes('/admin/')) return;

  e.respondWith(
    caches.match(request).then(cached => {
      const networkFetch = fetch(request).then(res => {
        if (res && res.status === 200 && res.type !== 'opaque') {
          const clone = res.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
        }
        return res;
      });
      // Cache-first for static assets, network-first for pages
      if (cached && request.destination === 'style' || request.destination === 'script' || request.destination === 'font') {
        return cached;
      }
      return networkFetch.catch(() => cached || new Response('Offline', { status: 503 }));
    })
  );
});
