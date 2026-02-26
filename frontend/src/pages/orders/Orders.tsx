import { Link } from 'react-router-dom'
import { ArrowLeft, Package, Clock, CheckCircle, MapPin } from 'lucide-react'

const mockOrders = [
  {
    id: 'ORD-001',
    status: 'delivered',
    total: 95,
    createdAt: '2024-01-15T10:30:00Z',
    items: [{ name: 'Stainless Steel Spork', quantity: 2 }],
    deliveryAddress: '123 Main Street, Johannesburg',
  },
  {
    id: 'ORD-002',
    status: 'in_transit',
    total: 145,
    createdAt: '2024-01-16T14:00:00Z',
    items: [{ name: 'Bic Ballpoint Pens (10pk)', quantity: 3 }, { name: 'Notebook A5', quantity: 2 }],
    deliveryAddress: '45 Office Park, Sandton',
    estimatedArrival: '14:45',
  },
]

const statusConfig: Record<string, { label: string; color: string; icon: any }> = {
  pending: { label: 'Pending', color: 'text-yellow-600 bg-yellow-50', icon: Clock },
  confirmed: { label: 'Confirmed', color: 'text-blue-600 bg-blue-50', icon: CheckCircle },
  in_transit: { label: 'On the way', color: 'text-[#FF6B35] bg-orange-50', icon: Package },
  delivered: { label: 'Delivered', color: 'text-green-600 bg-green-50', icon: CheckCircle },
}

export default function Orders() {
  return (
    <div className="min-h-screen bg-gray-50 pb-6">
      <header className="bg-white px-4 py-3 flex items-center border-b border-gray-100 sticky top-0">
        <Link to="/" className="p-2 -ml-2">
          <ArrowLeft className="w-6 h-6" />
        </Link>
        <h1 className="text-lg font-semibold ml-2">Orders</h1>
      </header>

      <div className="max-w-lg mx-auto px-4 py-4 space-y-3">
        {mockOrders.map(order => {
          const config = statusConfig[order.status]
          const StatusIcon = config.icon
          return (
            <Link key={order.id} to={`/orders/${order.id}`} className="card block">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-500">{order.id}</span>
                <span className={`text-xs font-medium px-2 py-1 rounded-full ${config.color}`}>
                  {config.label}
                </span>
              </div>
              <div className="flex items-start gap-2 mb-2">
                <StatusIcon className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm font-medium">
                    {order.items.map(i => `${i.quantity}x ${i.name}`).join(', ')}
                  </p>
                  <div className="flex items-center gap-1 text-xs text-gray-500 mt-1">
                    <MapPin className="w-3 h-3" />
                    {order.deliveryAddress}
                  </div>
                </div>
              </div>
              <div className="flex justify-between items-center pt-2 border-t border-gray-100">
                <span className="text-xs text-gray-400">
                  {new Date(order.createdAt).toLocaleDateString('en-ZA')}
                </span>
                <span className="font-bold text-[#FF6B35]">R{order.total}</span>
              </div>
            </Link>
          )
        })}

        {mockOrders.length === 0 && (
          <div className="text-center py-20">
            <Package className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No orders yet</p>
            <Link to="/products" className="text-[#FF6B35] text-sm mt-2 inline-block">
              Start shopping
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}