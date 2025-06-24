import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ShoppingCart, Users, Truck, Warehouse, BarChart3, Settings, Tags } from 'lucide-react'

export function SalesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Sales</h1>
        <p className="text-gray-600">Manage sales orders and transactions</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <ShoppingCart className="h-5 w-5" />
            <span>Sales Management</span>
          </CardTitle>
          <CardDescription>
            Create and manage sales orders
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500">Sales management functionality coming soon...</p>
        </CardContent>
      </Card>
    </div>
  )
}

export function CategoriesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Categories</h1>
        <p className="text-gray-600">Organize your products into categories</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Tags className="h-5 w-5" />
            <span>Product Categories</span>
          </CardTitle>
          <CardDescription>
            Manage product categories and subcategories
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500">Category management functionality coming soon...</p>
        </CardContent>
      </Card>
    </div>
  )
}

export function SuppliersPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Suppliers</h1>
        <p className="text-gray-600">Manage your product suppliers</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Truck className="h-5 w-5" />
            <span>Supplier Management</span>
          </CardTitle>
          <CardDescription>
            Manage supplier information and relationships
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500">Supplier management functionality coming soon...</p>
        </CardContent>
      </Card>
    </div>
  )
}

export function CustomersPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Customers</h1>
        <p className="text-gray-600">Manage your customer database</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="h-5 w-5" />
            <span>Customer Management</span>
          </CardTitle>
          <CardDescription>
            Manage customer information and loyalty programs
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500">Customer management functionality coming soon...</p>
        </CardContent>
      </Card>
    </div>
  )
}

export function WarehousesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Warehouses</h1>
        <p className="text-gray-600">Manage your storage locations</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Warehouse className="h-5 w-5" />
            <span>Warehouse Management</span>
          </CardTitle>
          <CardDescription>
            Manage warehouse locations and inventory distribution
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500">Warehouse management functionality coming soon...</p>
        </CardContent>
      </Card>
    </div>
  )
}

export function ReportsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
        <p className="text-gray-600">Analytics and business insights</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BarChart3 className="h-5 w-5" />
            <span>Business Reports</span>
          </CardTitle>
          <CardDescription>
            Generate reports and analyze business performance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500">Reporting functionality coming soon...</p>
        </CardContent>
      </Card>
    </div>
  )
}

export function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600">Configure your system preferences</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Settings className="h-5 w-5" />
            <span>System Settings</span>
          </CardTitle>
          <CardDescription>
            Configure application settings and preferences
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500">Settings functionality coming soon...</p>
        </CardContent>
      </Card>
    </div>
  )
}

