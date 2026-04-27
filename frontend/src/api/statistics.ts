import { request } from '@/utils/request'
import type { AdminDashboard, LeaderDashboard } from '@/types'

export const statisticsApi = {
  getAdminDashboard: () => request.get<AdminDashboard>('/statistics/admin_dashboard/'),
  
  getLeaderDashboard: () => request.get<LeaderDashboard>('/statistics/leader_dashboard/'),
  
  exportOrdersCsv: (activityId: string) => 
    `/api/statistics/export_orders_csv/?activity=${activityId}`,
  
  exportSummaryBySpecCsv: (activityId: string) => 
    `/api/statistics/export_summary_by_spec/?activity=${activityId}`,
  
  exportSummaryByMemberCsv: (activityId: string) => 
    `/api/statistics/export_summary_by_member/?activity=${activityId}`,
}