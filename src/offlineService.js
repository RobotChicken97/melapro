// Offline Service for managing offline functionality
class OfflineService {
  constructor() {
    this.isOnline = navigator.onLine
    this.serviceWorker = null
    this.pendingRequests = []
    this.listeners = new Map()
    
    // Initialize service worker and event listeners
    this.init()
  }
  
  async init() {
    // Register service worker
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js')
        this.serviceWorker = registration
        console.log('Service Worker registered successfully')
        
        // Listen for service worker messages
        navigator.serviceWorker.addEventListener('message', this.handleServiceWorkerMessage.bind(this))
        
        // Handle service worker updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              this.emit('update-available')
            }
          })
        })
        
      } catch (error) {
        console.error('Service Worker registration failed:', error)
      }
    }
    
    // Listen for online/offline events
    window.addEventListener('online', this.handleOnline.bind(this))
    window.addEventListener('offline', this.handleOffline.bind(this))
    
    // Initialize IndexedDB
    await this.initDB()
    
    // Load pending requests
    await this.loadPendingRequests()
  }
  
  // Initialize IndexedDB for offline storage
  async initDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('MelaproDB', 1)
      
      request.onerror = () => reject(request.error)
      request.onsuccess = () => {
        this.db = request.result
        resolve(this.db)
      }
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result
        
        // Create object stores
        if (!db.objectStoreNames.contains('products')) {
          const store = db.createObjectStore('products', { keyPath: '_id' })
          store.createIndex('sku', 'sku', { unique: true })
          store.createIndex('name', 'name', { unique: false })
        }
        
        if (!db.objectStoreNames.contains('categories')) {
          db.createObjectStore('categories', { keyPath: '_id' })
        }
        
        if (!db.objectStoreNames.contains('suppliers')) {
          db.createObjectStore('suppliers', { keyPath: '_id' })
        }
        
        if (!db.objectStoreNames.contains('customers')) {
          db.createObjectStore('customers', { keyPath: '_id' })
        }
        
        if (!db.objectStoreNames.contains('warehouses')) {
          db.createObjectStore('warehouses', { keyPath: '_id' })
        }
        
        if (!db.objectStoreNames.contains('sales')) {
          const store = db.createObjectStore('sales', { keyPath: '_id' })
          store.createIndex('date', 'created_at', { unique: false })
        }
        
        if (!db.objectStoreNames.contains('pending_sync')) {
          const store = db.createObjectStore('pending_sync', { keyPath: 'id', autoIncrement: true })
          store.createIndex('timestamp', 'timestamp', { unique: false })
        }
      }
    })
  }
  
  // Event listener management
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }
  
  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }
  
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => callback(data))
    }
  }
  
  // Handle online event
  handleOnline() {
    console.log('App is back online')
    this.isOnline = true
    this.emit('online')
    
    // Trigger background sync
    if (this.serviceWorker && 'sync' in window.ServiceWorkerRegistration.prototype) {
      this.serviceWorker.sync.register('sync-pending-requests')
    } else {
      // Fallback: manually sync pending requests
      this.syncPendingRequests()
    }
  }
  
  // Handle offline event
  handleOffline() {
    console.log('App is offline')
    this.isOnline = false
    this.emit('offline')
  }
  
  // Handle service worker messages
  handleServiceWorkerMessage(event) {
    const { type, data } = event.data
    
    switch (type) {
      case 'data-updated':
        this.emit('data-updated', data)
        break
        
      case 'serving-cached-data':
        this.emit('serving-cached-data', data)
        break
        
      case 'request-synced':
        this.emit('request-synced', data)
        break
        
      case 'sync-complete':
        this.emit('sync-complete', data)
        break
        
      default:
        console.log('Unknown service worker message:', type, data)
    }
  }
  
  // Store data locally
  async storeData(storeName, data) {
    if (!this.db) await this.initDB()
    
    const transaction = this.db.transaction([storeName], 'readwrite')
    const store = transaction.objectStore(storeName)
    
    if (Array.isArray(data)) {
      // Store multiple items
      await Promise.all(data.map(item => store.put(item)))
    } else {
      // Store single item
      await store.put(data)
    }
    
    console.log(`Stored data in ${storeName}:`, data)
  }
  
  // Get data from local storage
  async getData(storeName, key = null) {
    if (!this.db) await this.initDB()
    
    const transaction = this.db.transaction([storeName], 'readonly')
    const store = transaction.objectStore(storeName)
    
    if (key) {
      return await store.get(key)
    } else {
      return await store.getAll()
    }
  }
  
  // Delete data from local storage
  async deleteData(storeName, key) {
    if (!this.db) await this.initDB()
    
    const transaction = this.db.transaction([storeName], 'readwrite')
    const store = transaction.objectStore(storeName)
    await store.delete(key)
  }
  
  // Clear all data from a store
  async clearStore(storeName) {
    if (!this.db) await this.initDB()
    
    const transaction = this.db.transaction([storeName], 'readwrite')
    const store = transaction.objectStore(storeName)
    await store.clear()
  }
  
  // Queue request for later sync
  async queueRequest(url, options = {}) {
    const requestData = {
      url,
      method: options.method || 'GET',
      headers: options.headers || {},
      body: options.body || null,
      timestamp: Date.now()
    }
    
    // Store in IndexedDB
    await this.storeData('pending_sync', requestData)
    
    // Add to in-memory queue
    this.pendingRequests.push(requestData)
    
    this.emit('request-queued', requestData)
    console.log('Request queued for sync:', requestData)
  }
  
  // Load pending requests from storage
  async loadPendingRequests() {
    try {
      this.pendingRequests = await this.getData('pending_sync') || []
      console.log(`Loaded ${this.pendingRequests.length} pending requests`)
    } catch (error) {
      console.error('Error loading pending requests:', error)
      this.pendingRequests = []
    }
  }
  
  // Sync pending requests
  async syncPendingRequests() {
    if (!this.isOnline || this.pendingRequests.length === 0) {
      return
    }
    
    console.log(`Syncing ${this.pendingRequests.length} pending requests`)
    
    const successfulSyncs = []
    
    for (const request of this.pendingRequests) {
      try {
        const response = await fetch(request.url, {
          method: request.method,
          headers: request.headers,
          body: request.body
        })
        
        if (response.ok) {
          successfulSyncs.push(request)
          this.emit('request-synced', request)
        }
      } catch (error) {
        console.error('Sync failed for request:', request.url, error)
      }
    }
    
    // Remove successfully synced requests
    for (const syncedRequest of successfulSyncs) {
      const index = this.pendingRequests.indexOf(syncedRequest)
      if (index > -1) {
        this.pendingRequests.splice(index, 1)
        await this.deleteData('pending_sync', syncedRequest.id)
      }
    }
    
    this.emit('sync-complete', { syncedCount: successfulSyncs.length })
  }
  
  // Get pending requests count
  getPendingRequestsCount() {
    return this.pendingRequests.length
  }
  
  // Check if app is online
  getOnlineStatus() {
    return this.isOnline
  }
  
  // Force update service worker
  async updateServiceWorker() {
    if (this.serviceWorker) {
      const newWorker = this.serviceWorker.waiting
      if (newWorker) {
        newWorker.postMessage({ type: 'skip-waiting' })
        window.location.reload()
      }
    }
  }
  
  // Clear all offline data
  async clearOfflineData() {
    const stores = ['products', 'categories', 'suppliers', 'customers', 'warehouses', 'sales', 'pending_sync']
    
    for (const store of stores) {
      await this.clearStore(store)
    }
    
    // Clear service worker caches
    if (this.serviceWorker) {
      const channel = new MessageChannel()
      this.serviceWorker.active.postMessage({ type: 'clear-cache' }, [channel.port2])
    }
    
    console.log('All offline data cleared')
  }
  
  // Enhanced fetch with offline support
  async fetch(url, options = {}) {
    try {
      // Try network first
      const response = await fetch(url, options)
      
      if (response.ok) {
        // Store successful GET responses locally
        if (options.method === 'GET' || !options.method) {
          const data = await response.clone().json()
          
          // Determine store name from URL
          const storeName = this.getStoreNameFromUrl(url)
          if (storeName && data.success && data.data) {
            await this.storeData(storeName, data.data)
          }
        }
        
        return response
      } else {
        throw new Error(`HTTP ${response.status}`)
      }
    } catch (error) {
      console.log('Network request failed, trying offline:', error)
      
      // For GET requests, try to serve from local storage
      if (options.method === 'GET' || !options.method) {
        const storeName = this.getStoreNameFromUrl(url)
        if (storeName) {
          const localData = await this.getData(storeName)
          if (localData && localData.length > 0) {
            return new Response(JSON.stringify({
              success: true,
              data: localData,
              offline: true
            }), {
              status: 200,
              headers: { 'Content-Type': 'application/json' }
            })
          }
        }
      } else {
        // For POST/PUT/DELETE, queue for later sync
        await this.queueRequest(url, options)
        return new Response(JSON.stringify({
          success: false,
          error: 'Offline - request queued for sync',
          queued: true
        }), {
          status: 202,
          headers: { 'Content-Type': 'application/json' }
        })
      }
      
      throw error
    }
  }
  
  // Get store name from URL
  getStoreNameFromUrl(url) {
    const urlObj = new URL(url, window.location.origin)
    const path = urlObj.pathname
    
    if (path.includes('/products')) return 'products'
    if (path.includes('/categories')) return 'categories'
    if (path.includes('/suppliers')) return 'suppliers'
    if (path.includes('/customers')) return 'customers'
    if (path.includes('/warehouses')) return 'warehouses'
    if (path.includes('/sales')) return 'sales'
    
    return null
  }
}

// Create singleton instance
const offlineService = new OfflineService()

export default offlineService

