const CACHE_NAME = 'reader-cache-v1'
const STATIC_CACHE = 'reader-static-v1'
const API_CACHE = 'reader-api-v1'

// Files to cache
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/favicon.ico',
  '/assets/logo.png',
  '/assets/icons/icon-192x192.png',
  '/assets/icons/icon-512x512.png'
]

// Install event - cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    Promise.all([
      caches.open(STATIC_CACHE).then((cache) => {
        return cache.addAll(STATIC_ASSETS)
      }),
      caches.open(API_CACHE)
    ])
  )
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => {
            return name.startsWith('reader-') && 
                   name !== STATIC_CACHE && 
                   name !== API_CACHE
          })
          .map((name) => {
            return caches.delete(name)
          })
      )
    })
  )
})

// Fetch event - handle requests
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url)

  // API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      caches.open(API_CACHE).then((cache) => {
        return fetch(event.request)
          .then((response) => {
            // Cache successful API responses
            if (response.ok) {
              cache.put(event.request, response.clone())
            }
            return response
          })
          .catch(() => {
            // Return cached response if offline
            return cache.match(event.request)
          })
      })
    )
    return
  }

  // Static assets
  if (STATIC_ASSETS.includes(url.pathname)) {
    event.respondWith(
      caches.match(event.request).then((response) => {
        return response || fetch(event.request)
      })
    )
    return
  }

  // Other requests
  event.respondWith(
    fetch(event.request)
      .catch(() => {
        return caches.match(event.request)
      })
  )
})

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-document-changes') {
    event.waitUntil(syncDocumentChanges())
  }
})

async function syncDocumentChanges() {
  const cache = await caches.open(API_CACHE)
  const requests = await cache.keys()
  
  for (const request of requests) {
    if (request.method === 'POST' || request.method === 'PUT') {
      try {
        const response = await fetch(request)
        if (response.ok) {
          await cache.delete(request)
        }
      } catch (error) {
        console.error('Failed to sync:', error)
      }
    }
  }
}

// Push notifications
self.addEventListener('push', (event) => {
  const data = event.data.json()
  
  const options = {
    body: data.body,
    icon: '/assets/icons/icon-192x192.png',
    badge: '/assets/icons/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url
    }
  }

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  )
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  
  if (event.notification.data.url) {
    event.waitUntil(
      clients.openWindow(event.notification.data.url)
    )
  }
}) 