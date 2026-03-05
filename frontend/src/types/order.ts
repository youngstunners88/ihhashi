export type OrderStatus = 
  | 'pending' 
  | 'confirmed' 
  | 'preparing' 
  | 'ready' 
  | 'picked_up' 
  | 'in_transit' 
  | 'delivered' 
  | 'cancelled'

export type RefundReason = 
  | 'defective_goods'
  | 'not_as_described'
  | 'wrong_item'
  | 'missing_items'
  | 'damaged_in_transit'
  | 'late_delivery'
  | 'order_cancelled'
  | 'food_safety'
  | 'allergen_issues'
  | 'counterfeit'
  | 'price_error'
  | 'other'

export type RefundStatus = 
  | 'requested'
  | 'ai_review'
  | 'pending_merchant'
  | 'pending_evidence'
  | 'approved'
  | 'partially_approved'
  | 'rejected'
  | 'escalated'
  | 'completed'
  | 'disputed'

export interface RefundItem {
  order_item_id: string
  product_name: string
  quantity: number
  unit_price: number
  total_price: number
  refund_reason: RefundReason
  notes?: string
}

export const REFUND_REASONS: { value: RefundReason; label: string }[] = [
  { value: 'defective_goods', label: 'Defective / Poor Quality' },
  { value: 'not_as_described', label: 'Not as Described' },
  { value: 'wrong_item', label: 'Wrong Item Delivered' },
  { value: 'missing_items', label: 'Missing Items' },
  { value: 'damaged_in_transit', label: 'Damaged During Delivery' },
  { value: 'late_delivery', label: 'Late Delivery' },
  { value: 'food_safety', label: 'Food Safety Concerns' },
  { value: 'allergen_issues', label: 'Allergen Not Disclosed' },
  { value: 'other', label: 'Other Reason' },
]
