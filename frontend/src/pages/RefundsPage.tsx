import { useState, useEffect } from 'react'
import { RefundStatusCard } from '../../components/order/RefundStatusCard'
import { RefundStatus } from '../../types/order'

interface Refund {
  id: string
  order_id: string
  total_refund_amount: number
  refund_reason: string
  status: RefundStatus
  created_at: string
  deadline: string
  refund_items: Array<{
    product_name: string
    quantity: number
    total_price: number
  }>
}

export function RefundsPage() {
  const [refunds, setRefunds] = useState<Refund[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<RefundStatus | 'all'>('all')

  useEffect(() => {
    fetchRefunds()
  }, [filter])

  const fetchRefunds = async () => {
    setLoading(true)
    try {
      const url = filter === 'all' 
        ? '/api/v1/refunds/my-requests'
        : `/api/v1/refunds/my-requests?status=${filter}`
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setRefunds(data)
      }
    } catch (error) {
      console.error('Failed to fetch refunds:', error)
    } finally {
      setLoading(false)
    }
  }

  const statusFilters: { value: RefundStatus | 'all'; label: string }[] = [
    { value: 'all', label: 'All' },
    { value: 'requested', label: 'Requested' },
    { value: 'ai_review', label: 'In Review' },
    { value: 'approved', label: 'Approved' },
    { value: 'completed', label: 'Completed' },
    { value: 'rejected', label: 'Rejected' },
  ]

  const summary = {
    total: refunds.length,
    pending: refunds.filter(r => ['requested', 'ai_review', 'pending_merchant', 'pending_evidence'].includes(r.status)).length,
    approved: refunds.filter(r => r.status === 'approved' || r.status === 'completed').length,
    rejected: refunds.filter(r => r.status === 'rejected').length,
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-3xl mx-auto px-4 py-6">
          <h1 className="text-2xl font-bold text-gray-900">My Refunds</h1>
          <p className="text-sm text-gray-500 mt-1">
            Track and manage your refund requests
          </p>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-4 gap-3 mb-6">
          <div className="bg-white rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-gray-900">{summary.total}</p>
            <p className="text-xs text-gray-500">Total</p>
          </div>
          <div className="bg-white rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-yellow-600">{summary.pending}</p>
            <p className="text-xs text-gray-500">Pending</p>
          </div>
          <div className="bg-white rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-green-600">{summary.approved}</p>
            <p className="text-xs text-gray-500">Approved</p>
          </div>
          <div className="bg-white rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-red-600">{summary.rejected}</p>
            <p className="text-xs text-gray-500">Rejected</p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-2 overflow-x-auto pb-4 mb-4">
          {statusFilters.map((f) => (
            <button
              key={f.value}
              onClick={() => setFilter(f.value)}
              className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
                filter === f.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* Refunds List */}
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
          </div>
        ) : refunds.length === 0 ? (
          <div className="bg-white rounded-lg p-12 text-center">
            <svg className="w-16 h-16 mx-auto text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mt-4">No Refunds Found</h3>
            <p className="text-sm text-gray-500 mt-1">
              {filter === 'all' 
                ? "You haven't requested any refunds yet."
                : `No ${filter.replace('_', ' ')} refunds.`}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {refunds.map((refund) => (
              <RefundStatusCard
                key={refund.id}
                refund={refund as any}
              />
            ))}
          </div>
        )}

        {/* CPA Notice */}
        <div className="mt-8 bg-gray-100 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Your Rights Under South African Law</h4>
          <ul className="text-xs text-gray-600 space-y-1">
            <li>• Consumer Protection Act (CPA) guarantees refunds for defective goods within 6 months</li>
            <li>• Refunds must be processed within 10 business days</li>
            <li>• You may escalate unresolved disputes to the Consumer Goods and Services Ombud (CGSO)</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
