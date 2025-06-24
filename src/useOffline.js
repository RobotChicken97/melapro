import { useState, useEffect, useCallback } from 'react'
import offlineService from './offlineService'

export function useOffline() {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [pendingRequests, setPendingRequests] = useState(0)
  const [isServingCachedData, setIsServingCachedData] = useState(false)
  const [lastSyncTime, setLastSyncTime] = useState(null)
  const [updateAvailable, setUpdateAvailable] = useState(false)

  useEffect(() => {
    // Set up event listeners
    const handleOnline = () => {
      setIsOnline(true)
      setIsServingCachedData(false)
    }

    const handleOffline = () => {
      setIsOnline(false)
    }

    const handleDataUpdated = (data) => {
      console.log('Data updated from network:', data)
      setIsServingCachedData(false)
    }

    const handleServingCachedData = (data) => {
      console.log('Serving cached data:', data)
      setIsServingCachedData(true)
    }

    const handleRequestQueued = (request) => {
      setPendingRequests(prev => prev + 1)
    }

    const handleRequestSynced = (request) => {
      setPendingRequests(prev => Math.max(0, prev - 1))
    }

    const handleSyncComplete = (data) => {
      setLastSyncTime(new Date())
      setPendingRequests(0)
      console.log(`Sync complete: ${data.syncedCount} requests synced`)
    }

    const handleUpdateAvailable = () => {
      setUpdateAvailable(true)
    }

    // Register event listeners
    offlineService.on('online', handleOnline)
    offlineService.on('offline', handleOffline)
    offlineService.on('data-updated', handleDataUpdated)
    offlineService.on('serving-cached-data', handleServingCachedData)
    offlineService.on('request-queued', handleRequestQueued)
    offlineService.on('request-synced', handleRequestSynced)
    offlineService.on('sync-complete', handleSyncComplete)
    offlineService.on('update-available', handleUpdateAvailable)

    // Initialize pending requests count
    setPendingRequests(offlineService.getPendingRequestsCount())

    // Cleanup
    return () => {
      offlineService.off('online', handleOnline)
      offlineService.off('offline', handleOffline)
      offlineService.off('data-updated', handleDataUpdated)
      offlineService.off('serving-cached-data', handleServingCachedData)
      offlineService.off('request-queued', handleRequestQueued)
      offlineService.off('request-synced', handleRequestSynced)
      offlineService.off('sync-complete', handleSyncComplete)
      offlineService.off('update-available', handleUpdateAvailable)
    }
  }, [])

  // Enhanced fetch function with offline support
  const offlineFetch = useCallback(async (url, options = {}) => {
    return offlineService.fetch(url, options)
  }, [])

  // Store data locally
  const storeData = useCallback(async (storeName, data) => {
    return offlineService.storeData(storeName, data)
  }, [])

  // Get data from local storage
  const getData = useCallback(async (storeName, key = null) => {
    return offlineService.getData(storeName, key)
  }, [])

  // Clear offline data
  const clearOfflineData = useCallback(async () => {
    return offlineService.clearOfflineData()
  }, [])

  // Update service worker
  const updateApp = useCallback(async () => {
    return offlineService.updateServiceWorker()
  }, [])

  // Sync pending requests manually
  const syncNow = useCallback(async () => {
    return offlineService.syncPendingRequests()
  }, [])

  return {
    isOnline,
    pendingRequests,
    isServingCachedData,
    lastSyncTime,
    updateAvailable,
    offlineFetch,
    storeData,
    getData,
    clearOfflineData,
    updateApp,
    syncNow
  }
}

// Hook for offline-aware API calls
export function useOfflineApi() {
  const { offlineFetch, isOnline, isServingCachedData } = useOffline()

  const apiCall = useCallback(async (endpoint, options = {}) => {
    const url = `https://p9hwiqc5jvqq.manus.space/api${endpoint}`
    
    try {
      const response = await offlineFetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      })

      const data = await response.json()
      return { ...data, offline: !isOnline && response.status === 200 }
    } catch (error) {
      console.error('API call failed:', error)
      throw error
    }
  }, [offlineFetch, isOnline])

  const get = useCallback((endpoint) => {
    return apiCall(endpoint, { method: 'GET' })
  }, [apiCall])

  const post = useCallback((endpoint, body) => {
    return apiCall(endpoint, {
      method: 'POST',
      body: JSON.stringify(body)
    })
  }, [apiCall])

  const put = useCallback((endpoint, body) => {
    return apiCall(endpoint, {
      method: 'PUT',
      body: JSON.stringify(body)
    })
  }, [apiCall])

  const del = useCallback((endpoint) => {
    return apiCall(endpoint, { method: 'DELETE' })
  }, [apiCall])

  return {
    get,
    post,
    put,
    delete: del,
    isOnline,
    isServingCachedData
  }
}

