const CACHE_NAME = 'reader-cache-v1'
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/favicon.ico',
  '/logo192.png',
  '/logo512.png'
]

// Install event - cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(STATIC_ASSETS)
      })
  )
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      )
    })
  )
})

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return

  // Handle API requests
  if (event.request.url.includes('/api/')) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // Clone the response
          const responseToCache = response.clone()

          // Cache the API response
          caches.open(CACHE_NAME)
            .then((cache) => {
              cache.put(event.request, responseToCache)
            })

          return response
        })
        .catch(() => {
          // If network fails, try to serve from cache
          return caches.match(event.request)
        })
    )
    return
  }

  // Handle static assets and pages
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached response if found
        if (response) {
          return response
        }

        // Otherwise fetch from network
        return fetch(event.request)
          .then((response) => {
            // Don't cache if not a valid response
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response
            }

            // Clone the response
            const responseToCache = response.clone()

            // Cache the new response
            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseToCache)
              })

            return response
          })
      })
  )
})

// Background sync for failed requests
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-failed-requests') {
    event.waitUntil(syncFailedRequests())
  }
})

async function syncFailedRequests() {
  const cache = await caches.open(CACHE_NAME)
  const requests = await cache.keys()

  for (const request of requests) {
    if (request.url.includes('/api/')) {
      try {
        const response = await fetch(request)
        if (response.ok) {
          await cache.put(request, response)
        }
      } catch (error) {
        console.error('Failed to sync request:', error)
      }
    }
  }
} 