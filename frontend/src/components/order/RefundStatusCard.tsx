import { RefundStatus } from '../../types/order'

interface RefundEvidence {
  evidence_type: string
  file_url: string
  description: string
  submitted_at: string
}

interface RefundItem {
  order_item_id: string
  product_name: string
  quantity: number
  unit_price: number
  total_price: number
  refund_reason: string
}

interface Refund {
  id: string
  order_id: string
  total_refund_amount: number
  refund_reason: string
  customer_explanation: string
  status: RefundStatus
  refund_items: RefundItem[]
  evidence: RefundEvidence[]
  ai_decision?: string
  ai_confidence?: number
  ai_reasoning?: string
  approved_amount?: number
  resolution_notes?: string
  created_at: string
  deadline: string
  resolved_at?: string
}

interface RefundStatusCardProps {
  refund: Refund
  onAddEvidence?: (refundId: string) => void
  onOpenDispute?: (refundId: string) => void
}

const statusConfig: Record<RefundStatus, { color: string; icon: string; label: string }> = {
  requested: { color: 'bg-yellow-100 text-yellow-800 border-yellow-300', icon: '📝', label: 'Requested' },
  ai_review: { color: 'bg-purple-100 text-purple-800 border-purple-300', icon: '🤖', label: 'AI Review' },
  pending_merchant: { color: 'bg-blue-100 text-blue-800 border-blue-300', icon: '🏪', label: 'Awaiting Merchant' },
  pending_evidence: { color: 'bg-orange-100 text-orange-800 border-orange-300', icon: '📷', label: 'Evidence Needed' },
  approved: { color: 'bg-green-100 text-green-800 border-green-300', icon: '✅', label: 'Approved' },
  partially_approved: { color: 'bg-teal-100 text-teal-800 border-teal-300', icon: '⚖️', label: 'Partial Approval' },
  rejected: { color: 'bg-red-100 text-red-800 border-red-300', icon: '❌', label: 'Rejected' },
  escalated: { color: 'bg-indigo-100 text-indigo-800 border-indigo-300', icon: '⬆️', label: 'Escalated' },
  completed: { color: 'bg-emerald-100 text-emerald-800 border-emerald-300', icon: '💰', label: 'Completed' },
  disputed: { color: 'bg-rose-100 text-rose-800 border-rose-300', icon: '⚔️', label: 'Disputed' },
}

export function RefundStatusCard({ refund, onAddEvidence, onOpenDispute }: RefundStatusCardProps) {
  const config = statusConfig[refund.status]
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-ZA', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    })
  }

  const daysRemaining = () => {
    const deadline = new Date(refund.deadline)
    const now = new Date()
    const diff = Math.ceil((deadline.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
    return diff
  }

  const remaining = daysRemaining()

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className={`p-4 border-b ${config.color}`}>
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <span className="text-xl">{config.icon}</span>
            <span className="font-semibold">{config.label}</span>
          </div>
          {remaining > 0 && refund.status !== 'completed' && refund.status !== 'rejected' && (
            <span className="text-xs bg-white/50 px-2 py-1 rounded-full">
              {remaining} days remaining
            </span>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        {/* Amount */}
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Refund Amount</span>
          <span className="font-semibold text-gray-900">
            R{(refund.approved_amount || refund.total_refund_amount).toFixed(2)}
            {refund.approved_amount && refund.approved_amount < refund.total_refund_amount && (
              <span className="text-xs text-gray-500 ml-1">
                (of R{refund.total_refund_amount.toFixed(2)} requested)
              </span>
            )}
          </span>
        </div>

        {/* Items */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Items</h4>
          <div className="space-y-1">
            {refund.refund_items.map((item, idx) => (
              <div key={idx} className="flex justify-between text-sm">
                <span className="text-gray-600">
                  {item.quantity}× {item.product_name}
                </span>
                <span className="text-gray-900">R{item.total_price.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* AI Decision */}
        {refund.ai_decision && (
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-sm">🤖</span>
              <span className="text-sm font-medium text-gray-700">AI Assessment</span>
              {refund.ai_confidence && (
                <span className="text-xs bg-gray-200 px-2 py-0.5 rounded-full">
                  {Math.round(refund.ai_confidence * 100)}% confidence
                </span>
              )}
            </div>
            <p className="text-sm text-gray-600">{refund.ai_reasoning}</p>
          </div>
        )}

        {/* Resolution Notes */}
        {refund.resolution_notes && (
          <div className="bg-blue-50 rounded-lg p-3">
            <h4 className="text-sm font-medium text-blue-900 mb-1">Resolution Notes</h4>
            <p className="text-sm text-blue-800">{refund.resolution_notes}</p>
          </div>
        )}

        {/* Timeline */}
        <div className="text-xs text-gray-500 flex justify-between">
          <span>Requested: {formatDate(refund.created_at)}</span>
          {refund.resolved_at && (
            <span>Resolved: {formatDate(refund.resolved_at)}</span>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-2 pt-2 border-t border-gray-100">
          {(refund.status === 'pending_evidence' || refund.status === 'pending_merchant') && onAddEvidence && (
            <button
              onClick={() => onAddEvidence(refund.id)}
              className="flex-1 py-2 px-3 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors"
            >
              Add Evidence
            </button>
          )}
          {refund.status === 'rejected' && onOpenDispute && (
            <button
              onClick={() => onOpenDispute(refund.id)}
              className="flex-1 py-2 px-3 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
            >
              Open Dispute
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
