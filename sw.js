const CACHE_NAME = 'gessai-cache-v1';
const urlsToCache = [
  './',
  './index.html',
  './manifest.json'
];

// Installa il Service Worker e cached i file locali
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

// Intercetta le richieste di rete
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  
  // IGNORA le richieste a domini esterni (Firebase, API, ecc.)
  // Lascia che vadano direttamente alla rete senza caching
  if (url.origin !== self.location.origin) {
    return; 
  }

  // Per le richieste locali, usa la strategia Cache First
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});