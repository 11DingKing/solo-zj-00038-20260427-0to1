import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

export { dayjs }

export const formatDate = (date: string | Date, format = 'YYYY-MM-DD HH:mm:ss') => {
  return dayjs(date).format(format)
}

export const formatRelativeTime = (date: string | Date) => {
  return dayjs(date).fromNow()
}

export const formatPrice = (price: number) => {
  return `¥${price.toFixed(2)}`
}

export const getOrderStatusTag = (status: string) => {
  const statusMap: Record<string, { type: 'success' | 'warning' | 'danger' | 'info'; text: string }> = {
    pending: { type: 'info', text: '待付款' },
    paid: { type: 'primary', text: '已付款' },
    preparing: { type: 'warning', text: '备货中' },
    delivering: { type: 'warning', text: '配送中' },
    completed: { type: 'success', text: '已完成' },
    cancelled: { type: 'info', text: '已取消' },
    refunding: { type: 'danger', text: '退款中' },
    refunded: { type: 'info', text: '已退款' },
  }
  return statusMap[status] || { type: 'info', text: status }
}

export const getActivityStatusTag = (status: string) => {
  const statusMap: Record<string, { type: 'success' | 'warning' | 'danger' | 'info'; text: string }> = {
    draft: { type: 'info', text: '草稿' },
    active: { type: 'success', text: '进行中' },
    closed: { type: 'warning', text: '已关闭' },
    ended: { type: 'info', text: '已结束' },
  }
  return statusMap[status] || { type: 'info', text: status }
}

export const getLeaderStatusTag = (status: string) => {
  const statusMap: Record<string, { type: 'success' | 'warning' | 'danger' | 'info'; text: string }> = {
    pending: { type: 'warning', text: '待审核' },
    approved: { type: 'success', text: '已通过' },
    rejected: { type: 'danger', text: '已拒绝' },
  }
  return statusMap[status] || { type: 'info', text: status }
}

export const generateOrderNo = () => {
  const timestamp = Date.now().toString()
  const random = Math.random().toString(36).substring(2, 8).toUpperCase()
  return `GB${timestamp}${random}`
}

export const downloadFile = (url: string, filename?: string) => {
  const link = document.createElement('a')
  link.href = url
  if (filename) {
    link.download = filename
  }
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}