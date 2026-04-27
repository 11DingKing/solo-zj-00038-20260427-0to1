export interface User {
  id: number
  username: string
  email: string
  role: 'admin' | 'leader' | 'member'
  phone: string
  is_leader: boolean
  is_admin: boolean
  leader_status?: 'pending' | 'approved' | 'rejected'
  shop_name?: string
  shop_address?: string
}

export interface ProductSpec {
  id: string
  name: string
  price: number
  stock: number
  is_active: boolean
}

export interface Product {
  id: string
  name: string
  image: string
  description: string
  is_active: boolean
  specs: ProductSpec[]
  min_price: number
  total_stock: number
  specs_count: number
}

export interface ActivityProduct {
  id: string
  product: string
  product_name: string
  product_image: string
  product_spec: string
  spec_name: string
  original_price: number
  group_price: number
  limit_per_user: number
  is_active: boolean
  sold_quantity: number
  available_stock: number
}

export interface GroupBuyActivity {
  id: string
  title: string
  description: string
  leader: number
  leader_name: string
  leader_shop_name: string
  status: 'draft' | 'active' | 'closed' | 'ended'
  status_display: string
  start_time: string
  end_time: string
  delivery_type: 'pickup' | 'delivery'
  delivery_type_display: string
  pickup_address: string
  min_order_amount: number
  share_code: string
  is_active: boolean
  participant_count: number
  total_orders: number
  total_amount: number
  products: ActivityProduct[]
  created_at: string
}

export interface OrderItem {
  id: string
  product_name: string
  spec_name: string
  unit_price: number
  quantity: number
  subtotal: number
  product_image?: string
}

export interface Order {
  id: string
  order_no: string
  activity: string
  activity_title?: string
  leader_name?: string
  status: 'pending' | 'paid' | 'preparing' | 'delivering' | 'completed' | 'cancelled' | 'refunding' | 'refunded'
  status_display: string
  total_amount: number
  receiver_name: string
  receiver_phone: string
  delivery_address: string
  remark: string
  paid_at: string
  delivered_at: string
  completed_at: string
  items: OrderItem[]
  can_cancel: boolean
  can_pay: boolean
  can_apply_refund: boolean
  is_refundable: boolean
  created_at: string
}

export interface OrderStatusLog {
  id: string
  from_status: string
  from_status_display: string
  to_status: string
  to_status_display: string
  operator: number
  operator_name: string
  remark: string
  created_at: string
}

export interface GroupBuyJoin {
  id: string
  user_name: string
  product_name: string
  spec_name: string
  quantity: number
  unit_price: number
  created_at: string
}

export interface AdminDashboard {
  total_amount: number
  active_leaders: number
  total_orders: number
  last_30_days_orders: number
  pending_leader_count: number
  trading_trend: {
    date: string
    total_amount: number
    order_count: number
  }[]
  hot_products: {
    product_name: string
    spec_name: string
    total_quantity: number
    total_amount: number
    order_count: number
  }[]
}

export interface LeaderDashboard {
  monthly_amount: number
  monthly_order_count: number
  total_amount: number
  total_order_count: number
  refunded_count: number
  refunded_amount: number
  refund_rate: number
  active_activities: number
  recent_orders: Order[]
}

export interface OrderSummaryBySpec {
  product_name: string
  spec_name: string
  total_quantity: number
  total_amount: number
}

export interface OrderSummaryByMemberItem {
  product_name: string
  spec_name: string
  unit_price: number
  quantity: number
  subtotal: number
}

export interface OrderSummaryByMember {
  user_id: number
  user_name: string
  receiver_name: string
  receiver_phone: string
  delivery_address: string
  total_quantity: number
  total_amount: number
  items: OrderSummaryByMemberItem[]
}

export interface ApiResponse<T = any> {
  code?: number
  message?: string
  data: T
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}