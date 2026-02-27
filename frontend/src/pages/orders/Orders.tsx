import { useEffect } from 'react'
import { Link, useParams, useSearchParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Package, Clock, CheckCircle, Truck, MapPin, Loader2, RefreshCw } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../../App'
import { ordersAPI } from '../../lib/api'

const statusConfig: Record<string, { label: string; color: string; icon: any; description: string }> = {
  pending:    { label: 'Pending',      color: 'text-yellow-700 bg-yellow-50 border-yellow-200',   icon: Clock,        description: 'Waiting for merchant to confirm' },
  confirmed:  { label: 'Confirmed',    color: 'text-blue-700 bg-blue-50 border-blue-200',         icon: CheckCircle,  description: 'Merchant is preparing your order' },
  preparing:  { label: 'Preparing',    color: 'text-purple-700 bg-purple-50 border-purple-200',   icon: Package,      description: 'Your order is being packed' },
  ready:      { label: 'Ready',        color: 'text-indigo-700 bg-indigo-50 border-indigo-200',   icon: Package,      description: 'Waiting for rider pickup' },
  picked_up:  { label: 'Picked up',   color: 'text-orange-700 bg-orange-50 border-orange-200',   icon: Truck,        description: 'Rider has your order' },
  in_transit: { label: 'On the way',  color: 'text-orange-700 bg-orange-50 border-orange-200',   icon: Truck,        description: 'Your order is on its way' },
  delivered:  { label: 'Delivered',   color: 'text-green-700 bg-green-50 border-green-200',      icon: CheckCircle,  description: 'Delivered successfully' },
  cancelled:  { label: 'Cancelled',   color: 'text-red-700 bg-red-50 border-red-200',            icon: Package,      description: 'Order was cancelled' },
}

export default function Orders() {
  const { id: orderId } = useParams()
  const [searchParams] = useSearchParams()
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const isNewOrder = searchParams.get('new') === '1'

  // If not authenticated, redirect to auth
  useEffect(() => {
    if (!isAuthenticated) navigate('/auth', { replace: true })
  }, [isAuthenticated, navigate])

  // Single order view
  const { data: orderData, isLoading: orderLoading, refetch: refetchOrder } = useQuery({
    queryKey: ['order', orderId],
    queryFn: () => ordersAPI.get(orderId!).then(r => r.data),
    enabled: !!orderId && isAuthenticated,
    refetchInterval: orderId ? 15_000 : false, // Poll every 15s for active orders
  })

  // Orders list
  const { data: ordersData, isLoading: ordersLoading, refetch: refetchOrders } = useQuery({
    queryKey: ['orders'],
    queryFn: () => ordersAPI.list({ limit: 20 }).then(r => r.data),
    enabled: !orderId && isAuthenticated,
    staleTime: 30_000,
  })

  // ─── Single Order Detail ────────────────────────────────────────────────────
  if (orderId) {
    if (orderLoading) return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-[#FF6B35]" />
      </div>
    )

    const order = orderData
    if (!order) return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 text-center px-6">
        <Package className="w-12 h-12 text-gray-300" />
        <p className="text-gray-500">Order not found</p>
        <Link to="/orders" className="text-[#FF6B35] font-medium">Back to Orders</Link>
      </div>
    )

    const config = statusConfig[order.status] ?? statusConfig['pending']
    const StatusIcon = config.icon
    const isActive = ['pending', 'confirmed', 'preparing', 'ready', 'picked_up', 'in_transit'].includes(order.status)

    return (
      <div className="min-h-screen bg-gray-50 pb-8">
        <header className="bg-white border-b border-gray-100 sticky top-0 z-10">
          <div className="max-w-lg mx-auto px-4 py-3 flex items-center justify-between">
            <Link to="/orders" className="flex items-center gap-2">
              <ArrowLeft className="w-6 h-6" />
              <h1 className="text-lg font-semibold">Order #{order.id?.slice(-8).toUpperCase()}</h1>
            </Link>
            {isActive && (
              <button onClick={() => refetchOrder()} className="text-gray-400 hover:text-gray-600">
                <RefreshCw className="w-5 h-5" />
              </button>
            )}
          </div>
        </header>

        <div className="max-w-lg mx-auto px-4 py-4 space-y-4">
          {/* Success banner for new orders */}
          {isNewOrder && (
            <div className="bg-green-50 border border-green-200 rounded-xl p-4 text-center">
              <CheckCircle className="w-8 h-8 text-green-500 mx-auto mb-1" />
              <p className="font-semibold text-green-800">Order placed successfully!</p>
              <p className="text-green-600 text-sm mt-1">You'll receive updates as your order progresses</p>
            </div>
          )}

          {/* Status */}
          <div className="bg-white rounded-xl shadow-sm p-4">
            <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm font-medium mb-2 ${config.color}`}>
              <StatusIcon className="w-4 h-4" />
              {config.label}
            </div>
            <p className="text-gray-500 text-sm">{config.description}</p>
            {order.estimated_delivery && (
              <p className="text-sm font-medium mt-2 text-gray-700">
                Estimated arrival: {new Date(order.estimated_delivery).toLocaleTimeString('en-ZA', { hour: '2-digit', minute: '2-digit' })}
              </p>
            )}
          </div>

          {/* Rider info if assigned */}
          {order.rider && (
            <div className="bg-white rounded-xl shadow-sm p-4">
              <h3 className="font-semibold mb-2 flex items-center gap-2"><Truck className="w-4 h-4 text-[#FF6B35]" /> Your Rider</h3>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{order.rider.name}</p>
                  <p className="text-sm text-gray-500">{order.rider.vehicle_type ?? 'Motorcycle'}</p>
                </div>
                <a href={`tel:${order.rider.phone}`} className="bg-[#FF6B35] text-white px-4 py-2 rounded-xl text-sm font-medium">
                  Call
                </a>
              </div>
            </div>
          )}

          {/* Items */}
          <div className="bg-white rounded-xl shadow-sm p-4">
            <h3 className="font-semibold mb-3">Items</h3>
            <div className="space-y-2">
              {(order.items ?? []).map((item: any, i: number) => (
                <div key={i} className="flex justify-between text-sm">
                  <span className="text-gray-700">{item.quantity}× {item.product_name ?? item.name}</span>
                  <span className="font-medium">R{item.total_price ?? (item.unit_price * item.quantity)}</span>
                </div>
              ))}
              <div className="border-t pt-2 flex justify-between font-bold">
                <span>Total</span>
                <span className="text-[#FF6B35]">R{order.total}</span>
              </div>
            </div>
          </div>

          {/* Delivery address */}
          {order.delivery_info && (
            <div className="bg-white rounded-xl shadow-sm p-4">
              <h3 className="font-semibold mb-2 flex items-center gap-2"><MapPin className="w-4 h-4 text-[#FF6B35]" /> Delivery Address</h3>
              <p className="text-sm text-gray-600">
                {order.delivery_info.address_line1}{order.delivery_info.address_line2 ? `, ${order.delivery_info.address_line2}` : ''},{' '}
                {order.delivery_info.city}
              </p>
            </div>
          )}
        </div>
      </div>
    )
  }

  // ─── Orders List ──────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gray-50 pb-6">
      <header className="bg-white border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-lg mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center">
            <Link to="/" className="p-2 -ml-2"><ArrowLeft className="w-6 h-6" /></Link>
            <h1 className="text-lg font-semibold ml-2">My Orders</h1>
          </div>
          <button onClick={() => refetchOrders()} className="text-gray-400 hover:text-gray-600">
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </header>

      <div className="max-w-lg mx-auto px-4 py-4 space-y-3">
        {ordersLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-[#FF6B35]" />
          </div>
        ) : (ordersData?.orders ?? []).length === 0 ? (
          <div className="text-center py-20">
            <Package className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 font-medium">No orders yet</p>
            <Link to="/products" className="text-[#FF6B35] text-sm mt-2 inline-block font-medium">Start shopping</Link>
          </div>
        ) : (
          (ordersData?.orders ?? []).map((order: any) => {
            const config = statusConfig[order.status] ?? statusConfig['pending']
            const StatusIcon = config.icon
            return (
              <Link key={order.id} to={`/orders/${order.id}`} className="bg-white rounded-xl shadow-sm p-4 block hover:shadow-md transition">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-400 font-medium">#{order.id?.slice(-8).toUpperCase()}</span>
                  <span className={`text-xs font-medium px-2.5 py-1 rounded-full border ${config.color}`}>{config.label}</span>
                </div>
                <div className="flex items-start gap-2 mb-2">
                  <StatusIcon className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                  <p className="text-sm font-medium line-clamp-1">
                    {(order.items ?? []).map((i: any) => `${i.quantity}× ${i.product_name ?? i.name}`).join(', ') || '—'}
                  </p>
                </div>
                <div className="flex justify-between items-center text-xs text-gray-400">
                  <span>{order.created_at ? new Date(order.created_at).toLocaleDateString('en-ZA') : ''}</span>
                  <span className="font-bold text-[#FF6B35] text-sm">R{order.total}</span>
                </div>
              </Link>
            )
          })
        )}
      </div>
    </div>
  )
}
