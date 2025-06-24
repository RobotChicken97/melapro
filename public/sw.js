// Service Worker for Offline-First Inventory System
const CACHE_NAME = 'inventory-system-v1'
const API_CACHE_NAME = 'inventory-api-v1'

// Files to cache for offline use
const STATIC_CACHE_URLS = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json'
]

// API endpoints to cache
const API_CACHE_URLS = [
  '/api/products',
  '/api/categories',
  '/api/suppliers',
  '/api/customers',
  '/api/warehouses'
]

const API_BASE_URL = 'https://p9hwiqc5jvqq.manus.space'

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('Service Worker installing...')
  
  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(CACHE_NAME).then((cache) => {
        console.log('Caching static assets')
        return cache.addAll(STATIC_CACHE_URLS.filter(url => url !== '/'))
      }),
      // Cache API responses
      caches.open(API_CACHE_NAME).then((cache) => {
        console.log('Pre-caching API responses')
        return Promise.all(
          API_CACHE_URLS.map(url => {
            return fetch(`${API_BASE_URL}${url}`)
              .then(response => {
                if (response.ok) {
                  return cache.put(url, response.clone())
                }
              })
              .catch(err => console.log(`Failed to cache ${url}:`, err))
          })
        )
      })
    ]).then(() => {
      console.log('Service Worker installed successfully')
      // Force activation of new service worker
      return self.skipWaiting()
    })
  )
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker activating...')
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && cacheName !== API_CACHE_NAME) {
            console.log('Deleting old cache:', cacheName)
            return caches.delete(cacheName)
          }
        })
      )
    }).then(() => {
      console.log('Service Worker activated')
      // Take control of all pages immediately
      return self.clients.claim()
    })
  )
})

// Fetch event - implement offline-first strategy
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)
  
  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request))
    return
  }
  
  // Handle static assets
  if (request.method === 'GET') {
    event.respondWith(handleStaticRequest(request))
    return
  }
})

// Handle API requests with offline-first strategy
async function handleApiRequest(request) {
  const url = new URL(request.url)
  const cacheKey = url.pathname + url.search
  
  try {
    // For GET requests, try cache first, then network
    if (request.method === 'GET') {
      const cachedResponse = await caches.match(cacheKey, { cacheName: API_CACHE_NAME })
      
      try {
        // Try to fetch from network
        const networkResponse = await fetch(request)
        
        if (networkResponse.ok) {
          // Update cache with fresh data
          const cache = await caches.open(API_CACHE_NAME)
          await cache.put(cacheKey, networkResponse.clone())
          
          // Notify clients about data update
          notifyClients('data-updated', { url: cacheKey })
          
          return networkResponse
        } else {
          // Network failed, return cached version if available
          return cachedResponse || new Response(
            JSON.stringify({ success: false, error: 'Network error and no cached data' }),
            { status: 503, headers: { 'Content-Type': 'application/json' } }
          )
        }
      } catch (networkError) {
        console.log('Network request failed, using cache:', networkError)
        
        // Return cached version if available
        if (cachedResponse) {
          // Notify clients that we're serving cached data
          notifyClients('serving-cached-data', { url: cacheKey })
          return cachedResponse
        }
        
        // No cache available, return error
        return new Response(
          JSON.stringify({ success: false, error: 'Offline and no cached data available' }),
          { status: 503, headers: { 'Content-Type': 'application/json' } }
        )
      }
    }
    
    // For POST/PUT/DELETE requests, try network first
    if (['POST', 'PUT', 'DELETE'].includes(request.method)) {
      try {
        const networkResponse = await fetch(request.clone())
        
        if (networkResponse.ok) {
          // Invalidate related cache entries
          await invalidateRelatedCache(url.pathname)
          return networkResponse
        } else {
          // Store request for later sync
          await storeFailedRequest(request)
          return new Response(
            JSON.stringify({ success: false, error: 'Request queued for sync', queued: true }),
            { status: 202, headers: { 'Content-Type': 'application/json' } }
          )
        }
      } catch (networkError) {
        console.log('Network request failed, queuing for sync:', networkError)
        
        // Store request for later sync
        await storeFailedRequest(request)
        
        return new Response(
          JSON.stringify({ success: false, error: 'Offline - request queued for sync', queued: true }),
          { status: 202, headers: { 'Content-Type': 'application/json' } }
        )
      }
    }
    
    // Fallback for other methods
    return fetch(request)
    
  } catch (error) {
    console.error('Error handling API request:', error)
    return new Response(
      JSON.stringify({ success: false, error: 'Service worker error' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    )
  }
}

// Handle static asset requests
async function handleStaticRequest(request) {
  try {
    // Try cache first for static assets
    const cachedResponse = await caches.match(request)
    if (cachedResponse) {
      return cachedResponse
    }
    
    // Try network
    const networkResponse = await fetch(request)
    
    if (networkResponse.ok) {
      // Cache the response for future use
      const cache = await caches.open(CACHE_NAME)
      await cache.put(request, networkResponse.clone())
    }
    
    return networkResponse
  } catch (error) {
    console.error('Error handling static request:', error)
    
    // Return cached version if available
    const cachedResponse = await caches.match(request)
    if (cachedResponse) {
      return cachedResponse
    }
    
    // Return offline page or error
    return new Response('Offline', { status: 503 })
  }
}

// Store failed requests for later synchronization
async function storeFailedRequest(request) {
  try {
    const requestData = {
      url: request.url,
      method: request.method,
      headers: Object.fromEntries(request.headers.entries()),
      body: request.method !== 'GET' ? await request.text() : null,
      timestamp: Date.now()
    }
    
    // Store in IndexedDB for persistence
    const db = await openDB()
    const transaction = db.transaction(['pending_requests'], 'readwrite')
    const store = transaction.objectStore('pending_requests')
    await store.add(requestData)
    
    console.log('Stored failed request for sync:', requestData)
  } catch (error) {
    console.error('Error storing failed request:', error)
  }
}

// Invalidate cache entries related to a specific endpoint
async function invalidateRelatedCache(pathname) {
  try {
    const cache = await caches.open(API_CACHE_NAME)
    const keys = await cache.keys()
    
    const relatedKeys = keys.filter(request => {
      const url = new URL(request.url)
      return url.pathname.startsWith(pathname.split('/').slice(0, -1).join('/'))
    })
    
    await Promise.all(relatedKeys.map(key => cache.delete(key)))
    console.log('Invalidated cache entries:', relatedKeys.length)
  } catch (error) {
    console.error('Error invalidating cache:', error)
  }
}

// Notify clients about events
function notifyClients(type, data) {
  self.clients.matchAll().then(clients => {
    clients.forEach(client => {
      client.postMessage({ type, data })
    })
  })
}

// Open IndexedDB for storing pending requests
function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('MelaproDB', 1)
    
    request.onerror = () => reject(request.error)
    request.onsuccess = () => resolve(request.result)
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result
      
      // Create object store for pending requests
      if (!db.objectStoreNames.contains('pending_requests')) {
        const store = db.createObjectStore('pending_requests', { keyPath: 'id', autoIncrement: true })
        store.createIndex('timestamp', 'timestamp', { unique: false })
      }
      
      // Create object store for offline data
      if (!db.objectStoreNames.contains('offline_data')) {
        const store = db.createObjectStore('offline_data', { keyPath: 'key' })
        store.createIndex('timestamp', 'timestamp', { unique: false })
      }
    }
  })
}

// Background sync event
self.addEventListener('sync', (event) => {
  console.log('Background sync triggered:', event.tag)
  
  if (event.tag === 'sync-pending-requests') {
    event.waitUntil(syncPendingRequests())
  }
})

// Sync pending requests when back online
async function syncPendingRequests() {
  try {
    const db = await openDB()
    const transaction = db.transaction(['pending_requests'], 'readwrite')
    const store = transaction.objectStore('pending_requests')
    const requests = await store.getAll()
    
    console.log(`Syncing ${requests.length} pending requests`)
    
    for (const requestData of requests) {
      try {
        const response = await fetch(requestData.url, {
          method: requestData.method,
          headers: requestData.headers,
          body: requestData.body
        })
        
        if (response.ok) {
          // Request succeeded, remove from pending
          await store.delete(requestData.id)
          console.log('Synced request:', requestData.url)
          
          // Notify clients about successful sync
          notifyClients('request-synced', { url: requestData.url })
        } else {
          console.log('Sync failed for request:', requestData.url, response.status)
        }
      } catch (error) {
        console.log('Sync error for request:', requestData.url, error)
      }
    }
    
    // Notify clients that sync is complete
    notifyClients('sync-complete', { syncedCount: requests.length })
    
  } catch (error) {
    console.error('Error syncing pending requests:', error)
  }
}

// Message event for communication with main thread
self.addEventListener('message', (event) => {
  const { type, data } = event.data
  
  switch (type) {
    case 'skip-waiting':
      self.skipWaiting()
      break
      
    case 'get-pending-requests':
      getPendingRequests().then(requests => {
        event.ports[0].postMessage({ requests })
      })
      break
      
    case 'clear-cache':
      clearAllCaches().then(() => {
        event.ports[0].postMessage({ success: true })
      })
      break
      
    default:
      console.log('Unknown message type:', type)
  }
})

// Get pending requests count
async function getPendingRequests() {
  try {
    const db = await openDB()
    const transaction = db.transaction(['pending_requests'], 'readonly')
    const store = transaction.objectStore('pending_requests')
    return await store.getAll()
  } catch (error) {
    console.error('Error getting pending requests:', error)
    return []
  }
}

// Clear all caches
async function clearAllCaches() {
  try {
    const cacheNames = await caches.keys()
    await Promise.all(cacheNames.map(name => caches.delete(name)))
    console.log('All caches cleared')
  } catch (error) {
    console.error('Error clearing caches:', error)
  }
}

