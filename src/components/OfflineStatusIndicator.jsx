import { useState } from 'react'
import { useOffline } from '../useOffline'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Wifi, 
  WifiOff, 
  RefreshCw, 
  Download, 
  AlertCircle,
  CheckCircle,
  Clock,
  X
} from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

export function OfflineStatusIndicator() {
  const {
    isOnline,
    pendingRequests,
    isServingCachedData,
    lastSyncTime,
    updateAvailable,
    syncNow,
    updateApp,
    clearOfflineData
  } = useOffline()
  
  const [showDetails, setShowDetails] = useState(false)
  const [syncing, setSyncing] = useState(false)

  const handleSync = async () => {
    setSyncing(true)
    try {
      await syncNow()
    } catch (error) {
      console.error('Sync failed:', error)
    } finally {
      setSyncing(false)
    }
  }

  const handleUpdate = async () => {
    try {
      await updateApp()
    } catch (error) {
      console.error('Update failed:', error)
    }
  }

  const handleClearData = async () => {
    if (confirm('Are you sure you want to clear all offline data? This cannot be undone.')) {
      try {
        await clearOfflineData()
        alert('Offline data cleared successfully')
      } catch (error) {
        console.error('Clear data failed:', error)
        alert('Failed to clear offline data')
      }
    }
  }

  const getStatusColor = () => {
    if (!isOnline) return 'destructive'
    if (isServingCachedData) return 'secondary'
    return 'default'
  }

  const getStatusText = () => {
    if (!isOnline) return 'Offline'
    if (isServingCachedData) return 'Cached Data'
    return 'Online'
  }

  const getStatusIcon = () => {
    if (!isOnline) return WifiOff
    if (isServingCachedData) return Clock
    return Wifi
  }

  const StatusIcon = getStatusIcon()

  return (
    <>
      {/* Status Badge */}
      <div className="flex items-center space-x-2">
        <Badge 
          variant={getStatusColor()}
          className="cursor-pointer"
          onClick={() => setShowDetails(true)}
        >
          <StatusIcon className="h-3 w-3 mr-1" />
          {getStatusText()}
        </Badge>
        
        {pendingRequests > 0 && (
          <Badge variant="outline" className="text-orange-600 border-orange-600">
            {pendingRequests} pending
          </Badge>
        )}
        
        {updateAvailable && (
          <Badge variant="outline" className="text-blue-600 border-blue-600">
            Update available
          </Badge>
        )}
      </div>

      {/* Details Dialog */}
      <Dialog open={showDetails} onOpenChange={setShowDetails}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <StatusIcon className="h-5 w-5" />
              <span>Connection Status</span>
            </DialogTitle>
            <DialogDescription>
              Manage your offline data and synchronization
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            {/* Connection Status */}
            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <StatusIcon className="h-4 w-4" />
                    <span className="font-medium">{getStatusText()}</span>
                  </div>
                  <Badge variant={getStatusColor()}>
                    {isOnline ? 'Connected' : 'Disconnected'}
                  </Badge>
                </div>
                
                {isServingCachedData && (
                  <p className="text-sm text-muted-foreground mt-2">
                    You're viewing cached data. Some information may be outdated.
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Pending Requests */}
            {pendingRequests > 0 && (
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Clock className="h-4 w-4 text-orange-500" />
                      <span className="font-medium">Pending Sync</span>
                    </div>
                    <Badge variant="outline" className="text-orange-600 border-orange-600">
                      {pendingRequests} requests
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">
                    Changes will be synced when you're back online.
                  </p>
                  {isOnline && (
                    <Button 
                      size="sm" 
                      className="mt-2"
                      onClick={handleSync}
                      disabled={syncing}
                    >
                      {syncing ? (
                        <>
                          <RefreshCw className="h-3 w-3 mr-1 animate-spin" />
                          Syncing...
                        </>
                      ) : (
                        <>
                          <RefreshCw className="h-3 w-3 mr-1" />
                          Sync Now
                        </>
                      )}
                    </Button>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Last Sync */}
            {lastSyncTime && (
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="font-medium">Last Sync</span>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">
                    {lastSyncTime.toLocaleString()}
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Update Available */}
            {updateAvailable && (
              <Card>
                <CardContent className="pt-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Download className="h-4 w-4 text-blue-500" />
                      <span className="font-medium">Update Available</span>
                    </div>
                    <Button size="sm" onClick={handleUpdate}>
                      Update Now
                    </Button>
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">
                    A new version of the app is available.
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Offline Features */}
            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center space-x-2 mb-2">
                  <AlertCircle className="h-4 w-4" />
                  <span className="font-medium">Offline Features</span>
                </div>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• View products and inventory</li>
                  <li>• Create and edit products</li>
                  <li>• Record sales transactions</li>
                  <li>• Manage customers and suppliers</li>
                  <li>• Auto-sync when back online</li>
                </ul>
              </CardContent>
            </Card>
          </div>

          <DialogFooter className="flex justify-between">
            <Button 
              variant="outline" 
              size="sm"
              onClick={handleClearData}
              className="text-red-600 hover:text-red-700"
            >
              Clear Offline Data
            </Button>
            <Button onClick={() => setShowDetails(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

