import { request } from '@/utils/request'
import type { 
  Order, OrderStatusLog, OrderSummaryBySpec, OrderSummaryByMember,
  PaginatedResponse 
} from '@/types'

export const orderApi = {
  getMyOrders: (params?: { page?: number; page_size?: number; status?: string }) =>
    request.get<PaginatedResponse<Order>>('/orders/my_orders/', { params }),
  
  getActivityOrders: (activityId: string, params?: { page?: number; page_size?: number; status?: string }) =>
    request.get<PaginatedResponse<Order>>('/orders/activity_orders/', { 
      params: { activity: activityId, ...params } 
    }),
  
  getOrders: (params?: { page?: number; page_size?: number; activity?: string; status?: string }) =>
    request.get<PaginatedResponse<Order>>('/orders/', { params }),
  
  getOrder: (id: string) => request.get<Order>(`/orders/${id}/`),
  
  createOrder: (data: {
    activity_id: string
    items: { activity_product_id: string; quantity: number }[]
    receiver_name: string
    receiver_phone: string
    delivery_address?: string
    remark?: string
  }) => request.post<Order>('/orders/', data),
  
  cancelOrder: (id: string) => 
    request.post<{ message: string }>(`/orders/${id}/cancel/`),
  
  payOrder: (id: string) => 
    request.post<{ message: string; order: Order }>(`/orders/${id}/pay/`),
  
  applyRefund: (id: string, reason?: string) =>
    request.post<{ message: string }>(`/orders/${id}/apply_refund/`, { reason }),
  
  updateOrderStatus: (id: string, status: string, remark?: string) =>
    request.post<{ message: string; order: Order }>(`/orders/${id}/update_status/`, { 
      status, 
      remark 
    }),
  
  processRefund: (id: string, action: 'approve' | 'reject', remark?: string) =>
    request.post<{ message: string; order: Order }>(`/orders/${id}/process_refund/`, { 
      action, 
      remark 
    }),
  
  getSummaryBySpec: (activityId: string) =>
    request.get<OrderSummaryBySpec[]>('/orders/summary_by_spec/', { params: { activity: activityId } }),
  
  getSummaryByMember: (activityId: string) =>
    request.get<OrderSummaryByMember[]>('/orders/summary_by_member/', { params: { activity: activityId } }),
  
  getOrderStatusLogs: (id: string) =>
    request.get<OrderStatusLog[]>(`/orders/${id}/status_logs/`),
}