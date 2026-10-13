const CACHE_NAME = 'product-manager-shell-v1.1.0';
const APP_SHELL = [
  '/styles.css',
  '/manifest.webmanifest',
  '/js/api.js',
  '/js/dashboard.js',
  '/js/products.js',
  '/js/pwa.js',
  '/js/brand.js',
  '/assets/icons/open-source-mark.svg',
  '/assets/icons/product-manager-brand.svg',
  '/assets/icons/product-manager-192.png',
  '/assets/icons/product-manager-512.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((key) => key.startsWith('product-manager-shell-') && key !== CACHE_NAME)
        .map((key) => caches.delete(key)),
    )),
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin || url.pathname.startsWith('/api/')) return;

  if (request.mode === 'navigate') return;

  event.respondWith(
    caches.match(request).then((cached) => {
      const network = fetch(request).then((response) => {
        if (response.ok) caches.open(CACHE_NAME).then((cache) => cache.put(request, response.clone()));
        return response;
      });
      return cached || network;
    }),
  );
});
