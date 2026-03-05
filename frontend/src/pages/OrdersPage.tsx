import { useState, useEffect } from 'react'
import { OrderCard } from '../components/order/OrderCard'
import { RefundRequestModal, RefundRequestData } from '../components/order/RefundRequestModal'
import { RefundStatusCard } from '../components/order/RefundStatusCard'
import { OrderStatus, RefundStatus } from '../types/order'

interface OrderItem {
  product_id: string
  product_name: string
  quantity: number
  unit_price: number
  total_price: number
}

interface DeliveryInfo {
  address_label: string
  address_line1: string
  address_line2?: string
  city: string
  area?: string
  recipient_phone: string
}

interface Order {
  id: string
  buyer_id: string
  store_id: string
  rider_id?: string
  items: OrderItem[]
  subtotal: number
  delivery_fee: number
  total: number
  currency: string
  status: OrderStatus
  delivery_info: DeliveryInfo
  created_at: string
  delivered_at?: string
  payment_method: string
  payment_status: string
  buyer_notes?: string
  refund?: RefundInfo
}

interface RefundInfo {
  id: string
  order_id: string
  total_refund_amount: number
  refund_reason: string
  customer_explanation: string
  status: RefundStatus
  created_at: string
  deadline: string
  ai_decision?: string
  ai_confidence?: number
  approved_amount?: number
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'active' | 'past' | 'refunds'>('active')
  const [refundModalOrder, setRefundModalOrder] = useState<Order | null>(null)
  const [refunds, setRefunds] = useState<RefundInfo[]>([])

  useEffect(() => {
    fetchOrders()
    fetchRefunds()
  }, [])

  const fetchOrders = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_BASE}/orders/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) throw new Error('Failed to fetch orders')
      
      const data = await response.json()
      setOrders(data.orders || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const fetchRefunds = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_BASE}/refunds/my-requests`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setRefunds(data || [])
      }
    } catch (err) {
      console.error('Failed to fetch refunds:', err)
    }
  }

  const handleRequestRefund = async (orderId: string) => {
    const order = orders.find(o => o.id === orderId)
    if (order) {
      setRefundModalOrder(order)
    }
  }

  const handleTrackOrder = (orderId: string) => {
    window.location.href = `/track/${orderId}`
  }

  const submitRefundRequest = async (refundData: RefundRequestData) => {
    const token = localStorage.getItem('token')
    const response = await fetch(`${API_BASE}/refunds/request`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(refundData),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to submit refund request')
    }

    await fetchRefunds()
  }

  const activeStatuses: OrderStatus[] = ['pending', 'confirmed', 'preparing', 'ready', 'picked_up', 'in_transit']
  const pastStatuses: OrderStatus[] = ['delivered', 'cancelled']

  const filteredOrders = orders.filter(order => {
    if (activeTab === 'active') return activeStatuses.includes(order.status)
    if (activeTab === 'past') return pastStatuses.includes(order.status)
    return false
  })

  const tabs = [
    { id: 'active', label: 'Active', count: orders.filter(o => activeStatuses.includes(o.status)).length },
    { id: 'past', label: 'Past', count: orders.filter(o => pastStatuses.includes(o.status)).length },
    { id: 'refunds', label: 'Refunds', count: refunds.length },
  ] as const

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-500">Loading orders...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={fetchOrders}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="p-4">
          <h1 className="text-xl font-bold text-gray-900">My Orders</h1>
        </div>
        
        {/* Tabs */}
        <div className="flex border-t">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 py-3 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.label}
              {tab.count > 0 && (
                <span className={`ml-1 px-2 py-0.5 rounded-full text-xs ${
                  activeTab === tab.id ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
                }`}>
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {activeTab === 'refunds' ? (
          <div className="space-y-4">
            {refunds.length === 0 ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2zM10 8.5a.5.5 0 11-1 0 .5.5 0 011 0zm5 5a.5.5 0 11-1 0 .5.5 0 011 0z" />
                  </svg>
                </div>
                <p className="text-gray-500">No refund requests</p>
              </div>
            ) : (
              refunds.map(refund => (
                <RefundStatusCard
                  key={refund.id}
                  refund={refund}
                  onViewDetails={(id) => window.location.href = `/refunds/${id}`}
                />
              ))
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {filteredOrders.length === 0 ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                  </svg>
                </div>
                <p className="text-gray-500 mb-1">No {activeTab} orders</p>
                <p className="text-sm text-gray-400">
                  {activeTab === 'active' ? 'Your active orders will appear here' : 'Your order history will appear here'}
                </p>
              </div>
            ) : (
              filteredOrders.map(order => (
                <OrderCard
                  key={order.id}
                  order={order}
                  onRequestRefund={handleRequestRefund}
                  onTrackOrder={handleTrackOrder}
                />
              ))
            )}
          </div>
        )}
      </div>

      {/* Refund Modal */}
      {refundModalOrder && (
        <RefundRequestModal
          orderId={refundModalOrder.id}
          items={refundModalOrder.items}
          onClose={() => setRefundModalOrder(null)}
          onSubmit={submitRefundRequest}
        />
      )}
    </div>
  )
}
