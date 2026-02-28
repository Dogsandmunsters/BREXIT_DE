const CACHE_NAME = 'can-you-brexit-v1';
const urlsToCache = [
  './',
  './index.html',
  './manifest.json',
  './sounds/click.wav',
  './images/title.jpg',
  './images/icon-192.png',
  './images/icon-512.png',
  './images/coin-heads.png',
  './images/coin-tails.png',
  './images/coin-unflipped.png'
];

// Install service worker and cache resources
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

// Fetch from cache, fallback to network
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Return cached version or fetch from network
        return response || fetch(event.request);
      })
  );
});

// Clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
