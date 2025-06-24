import { getDb, replicateDb } from './shared/services/pouchdb.js'

class OfflineService {
  constructor() {
    this.isOnline = navigator.onLine
    this.listeners = new Map()
    this.dbs = {}
    this.pendingRequests = []
    this.init()
  }

  async init() {
    if ('serviceWorker' in navigator) {
      try {
        await navigator.serviceWorker.register('/sw.js')
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error('Service Worker registration failed:', err)
      }
    }

    window.addEventListener('online', this.handleOnline.bind(this))
    window.addEventListener('offline', this.handleOffline.bind(this))

    this.initDbs()
    await this.loadPendingRequests()
    if (this.isOnline) this.startReplication()
  }

  initDbs() {
    const stores = ['products', 'categories', 'suppliers', 'customers', 'warehouses', 'sales', 'pending_sync']
    stores.forEach((name) => {
      this.dbs[name] = getDb(name)
    })
  }

  startReplication() {
    const remoteBase = 'http://localhost:5984'
    ;['products', 'categories', 'suppliers', 'customers', 'warehouses', 'sales'].forEach((name) => {
      replicateDb(name, `${remoteBase}/${name}`)
    })
  }

  on(event, cb) {
    if (!this.listeners.has(event)) this.listeners.set(event, [])
    this.listeners.get(event).push(cb)
  }

  off(event, cb) {
    const arr = this.listeners.get(event) || []
    const idx = arr.indexOf(cb)
    if (idx > -1) arr.splice(idx, 1)
  }

  emit(event, data) {
    ;(this.listeners.get(event) || []).forEach((cb) => cb(data))
  }

  handleOnline() {
    this.isOnline = true
    this.emit('online')
    this.startReplication()
    this.syncPendingRequests()
  }

  handleOffline() {
    this.isOnline = false
    this.emit('offline')
  }

  async storeData(store, data) {
    const db = this.dbs[store]
    if (!db) return
    if (Array.isArray(data)) {
      await Promise.all(data.map((d) => this.storeData(store, d)))
      return
    }
    try {
      await db.put(data)
    } catch (err) {
      if (err.status === 409) {
        // eslint-disable-next-line no-underscore-dangle
        const existing = await db.get(data._id)
        await db.put({ ...existing, ...data })
      } else {
        throw err
      }
    }
  }

  async getData(store, id = null) {
    const db = this.dbs[store]
    if (!db) return null
    if (id) {
      try {
        return await db.get(id)
      } catch {
        return null
      }
    }
    const { rows } = await db.allDocs({ include_docs: true })
    return rows.map((r) => r.doc)
  }

  async deleteData(store, id) {
    const db = this.dbs[store]
    if (!db) return
    try {
      const doc = await db.get(id)
      await db.remove(doc)
    } catch {
      // ignore errors removing data
    }
  }

  async clearStore(store) {
    if (this.dbs[store]) {
      await this.dbs[store].destroy()
      this.dbs[store] = getDb(store)
    }
  }

  async queueRequest(url, options = {}) {
    const data = {
      url,
      method: options.method || 'GET',
      headers: options.headers || {},
      body: options.body || null,
      timestamp: Date.now(),
    }
    await this.dbs.pending_sync.post(data)
    this.pendingRequests.push(data)
    this.emit('request-queued', data)
  }

  async loadPendingRequests() {
    const docs = await this.getData('pending_sync')
    this.pendingRequests = docs || []
  }

  async syncPendingRequests() {
    if (!this.isOnline || this.pendingRequests.length === 0) return
    const synced = []
    for (const req of this.pendingRequests) {
      try {
        const res = await fetch(req.url, {
          method: req.method,
          headers: req.headers,
          body: req.body,
        })
        if (res.ok) {
          synced.push(req)
          this.emit('request-synced', req)
        }
      } catch {
        // ignore network errors when syncing
      }
    }
    const remaining = []
    for (const req of this.pendingRequests) {
      if (synced.includes(req)) {
        const all = await this.dbs.pending_sync.allDocs({ include_docs: true })
        const doc = all.rows.find((r) => r.doc.timestamp === req.timestamp)
        // eslint-disable-next-line no-underscore-dangle
        if (doc) await this.dbs.pending_sync.remove(doc.id, doc.doc._rev)
      } else {
        remaining.push(req)
      }
    }
    this.pendingRequests = remaining
    this.emit('sync-complete', { syncedCount: synced.length })
  }

  async fetch(url, options = {}) {
    try {
      const response = await fetch(url, options)
      if (response.ok) {
        if (options.method === 'GET' || !options.method) {
          const data = await response.clone().json()
          const store = this.getStoreNameFromUrl(url)
          if (store && data.success && data.data) {
            await this.storeData(store, data.data)
          }
        }
        return response
      }
      throw new Error(`HTTP ${response.status}`)
    } catch (error) {
      if (options.method === 'GET' || !options.method) {
        const store = this.getStoreNameFromUrl(url)
        if (store) {
          const local = await this.getData(store)
          if (local && local.length > 0) {
            return new Response(
              JSON.stringify({ success: true, data: local, offline: true }),
              { status: 200, headers: { 'Content-Type': 'application/json' } },
            )
          }
        }
      } else {
        await this.queueRequest(url, options)
        return new Response(
          JSON.stringify({ success: false, error: 'Offline - request queued for sync', queued: true }),
          { status: 202, headers: { 'Content-Type': 'application/json' } },
        )
      }
      throw error
    }
  }

  getStoreNameFromUrl(url) {
    const path = new URL(url, window.location.origin).pathname
    if (path.includes('/products')) return 'products'
    if (path.includes('/categories')) return 'categories'
    if (path.includes('/suppliers')) return 'suppliers'
    if (path.includes('/customers')) return 'customers'
    if (path.includes('/warehouses')) return 'warehouses'
    if (path.includes('/sales')) return 'sales'
    return null
  }
}

const offlineService = new OfflineService()
export default offlineService
