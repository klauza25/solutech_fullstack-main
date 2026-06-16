/**
 * =============================================================================
 * SERVICE WORKER SOLUTECH
 * Mise en cache des assets pour fonctionnement hors-ligne complet
 * Stratégie : Cache-first pour les assets, Network-first pour les données
 * =============================================================================
 */

const CACHE_NAME = 'solutech-v2.0';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
];

// Installation du service worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] Cache ouvert :', CACHE_NAME);
      return cache.addAll(STATIC_ASSETS);
    })
  );
  // Activer immédiatement
  self.skipWaiting();
});

// Activation et nettoyage des anciens caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
  // Prendre le contrôle immédiatement
  self.clients.claim();
});

// Interception des requêtes
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Stratégie différente selon le type de requête
  if (request.method !== 'GET') {
    // Requêtes POST/PUT/DELETE : réseau uniquement
    return;
  }

  if (url.origin === location.origin) {
    // Requêtes vers notre domaine
    if (request.url.includes('/api/')) {
      // API : network-first avec fallback cache
      event.respondWith(networkFirstStrategy(request));
    } else {
      // Assets statiques : cache-first
      event.respondWith(cacheFirstStrategy(request));
    }
  }
  // Autres requêtes : laisser passer
});

/**
 * Stratégie Cache-First pour les assets statiques
 */
async function cacheFirstStrategy(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    // Mettre à jour le cache en arrière-plan
    event.waitUntil(updateCache(request));
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch {
    // Fallback pour navigation
    if (request.mode === 'navigate') {
      return caches.match('/index.html');
    }
    return new Response('Offline', { status: 503 });
  }
}

/**
 * Stratégie Network-First pour les données API
 */
async function networkFirstStrategy(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      // Ajouter un header pour indiquer que c'est une réponse stale
      const headers = new Headers(cachedResponse.headers);
      headers.set('X-From-Cache', 'true');
      return new Response(cachedResponse.body, {
        status: cachedResponse.status,
        statusText: cachedResponse.statusText,
        headers,
      });
    }
    
    // Fallback pour les requêtes API échouées
    return new Response(JSON.stringify({ error: 'offline' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

/**
 * Mettre à jour le cache en arrière-plan
 */
async function updateCache(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      await cache.put(request, response);
    }
  } catch {
    // Ignorer les erreurs de mise à jour
  }
}

// Gestion des notifications push (futur)
self.addEventListener('push', (event) => {
  const data = event.data?.json() ?? {};
  const title = data.title ?? 'SOLUTECH';
  const options = {
    body: data.body ?? 'Nouvelle notification',
    icon: '/icon-192x192.png',
    badge: '/icon-192x192.png',
    vibrate: [100, 50, 100],
    data: data.url ?? '/',
  };
  
  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// Gestion du clic sur les notifications
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data)
  );
});
