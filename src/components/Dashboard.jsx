import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Package, 
  ShoppingCart, 
  Users, 
  TrendingUp, 
  AlertTriangle,
  DollarSign,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'

// Mock data for charts
const salesData = [
  { name: 'Mon', sales: 4000, orders: 24 },
  { name: 'Tue', sales: 3000, orders: 18 },
  { name: 'Wed', sales: 5000, orders: 32 },
  { name: 'Thu', sales: 4500, orders: 28 },
  { name: 'Fri', sales: 6000, orders: 38 },
  { name: 'Sat', sales: 5500, orders: 35 },
  { name: 'Sun', sales: 3500, orders: 22 }
]

const topProducts = [
  { name: 'Paracetamol 500mg', sold: 150, revenue: 22500 },
  { name: 'Vitamin C 1000mg', sold: 89, revenue: 44500 },
  { name: 'Hand Sanitizer 250ml', sold: 67, revenue: 53600 },
  { name: 'Baby Diapers Size M', sold: 45, revenue: 112500 }
]

export function Dashboard() {
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalSales: 0,
    totalCustomers: 0,
    lowStockItems: 0,
    todayRevenue: 0,
    todayOrders: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate API call to fetch dashboard data
    const fetchDashboardData = async () => {
      try {
        // In a real app, this would be API calls
        setStats({
          totalProducts: 156,
          totalSales: 1247,
          totalCustomers: 89,
          lowStockItems: 12,
          todayRevenue: 45600,
          todayOrders: 23
        })
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  const StatCard = ({ title, value, icon: Icon, change, changeType, description }) => (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {change && (
          <div className="flex items-center space-x-1 text-xs text-muted-foreground">
            {changeType === 'increase' ? (
              <ArrowUpRight className="h-3 w-3 text-green-600" />
            ) : (
              <ArrowDownRight className="h-3 w-3 text-red-600" />
            )}
            <span className={changeType === 'increase' ? 'text-green-600' : 'text-red-600'}>
              {change}%
            </span>
            <span>from last month</span>
          </div>
        )}
        {description && (
          <p className="text-xs text-muted-foreground mt-1">{description}</p>
        )}
      </CardContent>
    </Card>
  )

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Welcome back! Here's what's happening with your inventory.</p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Products"
          value={stats.totalProducts.toLocaleString()}
          icon={Package}
          change={12}
          changeType="increase"
          description="Active products in inventory"
        />
        <StatCard
          title="Total Sales"
          value={stats.totalSales.toLocaleString()}
          icon={ShoppingCart}
          change={8}
          changeType="increase"
          description="Completed transactions"
        />
        <StatCard
          title="Customers"
          value={stats.totalCustomers.toLocaleString()}
          icon={Users}
          change={5}
          changeType="increase"
          description="Registered customers"
        />
        <StatCard
          title="Low Stock Items"
          value={stats.lowStockItems}
          icon={AlertTriangle}
          description="Items below reorder point"
        />
      </div>

      {/* Today's Performance */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <DollarSign className="h-5 w-5" />
              <span>Today's Revenue</span>
            </CardTitle>
            <CardDescription>Revenue generated today</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">
              ₦{stats.todayRevenue.toLocaleString()}
            </div>
            <p className="text-sm text-muted-foreground mt-2">
              From {stats.todayOrders} orders
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>Sales Trend</span>
            </CardTitle>
            <CardDescription>Last 7 days performance</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={100}>
              <LineChart data={salesData}>
                <Line 
                  type="monotone" 
                  dataKey="sales" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Charts and Tables */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Sales Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Weekly Sales</CardTitle>
            <CardDescription>Sales performance over the last 7 days</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={salesData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip 
                  formatter={(value, name) => [
                    name === 'sales' ? `₦${value.toLocaleString()}` : value,
                    name === 'sales' ? 'Revenue' : 'Orders'
                  ]}
                />
                <Bar dataKey="sales" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Top Products */}
        <Card>
          <CardHeader>
            <CardTitle>Top Selling Products</CardTitle>
            <CardDescription>Best performing products this month</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topProducts.map((product, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-sm">{product.name}</p>
                    <p className="text-xs text-gray-500">{product.sold} units sold</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-sm">₦{product.revenue.toLocaleString()}</p>
                    <Badge variant="secondary" className="text-xs">
                      #{index + 1}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks and shortcuts</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <Button className="h-20 flex flex-col space-y-2">
              <Package className="h-6 w-6" />
              <span>Add Product</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col space-y-2">
              <ShoppingCart className="h-6 w-6" />
              <span>New Sale</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col space-y-2">
              <Users className="h-6 w-6" />
              <span>Add Customer</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col space-y-2">
              <AlertTriangle className="h-6 w-6" />
              <span>Low Stock Alert</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

