import { request } from '@/utils/request'
import type { User, PaginatedResponse } from '@/types'

export const userApi = {
  getProfile: () => request.get<User>('/users/profile/'),
  
  updateProfile: (data: Partial<User>) => request.put<User>('/users/profile/', data),
  
  getPendingLeaders: () => request.get<User[]>('/users/pending_leaders/'),
  
  approveLeader: (userId: number, status: 'approved' | 'rejected') => 
    request.post(`/users/${userId}/approve_leader/`, { leader_status: status }),
  
  getUsers: (params?: { page?: number; page_size?: number; role?: string }) =>
    request.get<PaginatedResponse<User>>('/users/', { params }),
  
  getUser: (id: number) => request.get<User>(`/users/${id}/`),
}