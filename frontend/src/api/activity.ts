import { request } from '@/utils/request'
import type { GroupBuyActivity, ActivityProduct, GroupBuyJoin, PaginatedResponse } from '@/types'

export const activityApi = {
  getActivities: (params?: { 
    page?: number; 
    page_size?: number; 
    status?: string;
    leader?: string;
  }) => request.get<PaginatedResponse<GroupBuyActivity>>('/activities/', { params }),
  
  getActiveActivities: (params?: { page?: number; page_size?: number }) =>
    request.get<PaginatedResponse<GroupBuyActivity>>('/activities/', { 
      params: { ...params, status: 'active' } 
    }),
  
  getMyActivities: (params?: { page?: number; page_size?: number }) =>
    request.get<GroupBuyActivity[]>('/activities/my_activities/', { params }),
  
  getActivity: (id: string) => request.get<GroupBuyActivity>(`/activities/${id}/`),
  
  getActivityByShareCode: (code: string) => 
    request.get<GroupBuyActivity>('/activities/by_share_code/', { params: { code } }),
  
  createActivity: (data: {
    title: string
    description: string
    start_time: string
    end_time: string
    delivery_type: 'pickup' | 'delivery'
    pickup_address: string
    min_order_amount: number
    products: {
      product: string
      product_spec: string
      group_price: number
      limit_per_user?: number
    }[]
  }) => request.post<GroupBuyActivity>('/activities/', data),
  
  publishActivity: (id: string) => 
    request.post<{ message: string; share_code: string; share_link: string }>(
      `/activities/${id}/publish/`
    ),
  
  closeActivity: (id: string) => 
    request.post<{ message: string }>(`/activities/${id}/close/`),
  
  getActivityJoins: (id: string, params?: { page?: number; page_size?: number }) =>
    request.get<PaginatedResponse<GroupBuyJoin>>(`/activities/${id}/joins/`, { params }),
  
  getShareInfo: (id: string) =>
    request.get<{
      id: string
      title: string
      share_code: string
      share_link: string
      cover_image: string
      min_price: number
      participant_count: number
      end_time: string
      leader_name: string
      shop_name: string
    }>(`/activities/${id}/share_info/`),
  
  getActivityProducts: (activityId?: string) =>
    request.get<ActivityProduct[]>('/activities/products/', { params: { activity: activityId } }),
}