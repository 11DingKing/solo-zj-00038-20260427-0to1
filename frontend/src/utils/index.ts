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

export interface PosterOptions {
  title: string
  coverImage: string
  minPrice: number
  participantCount: number
  endTime: string
  leaderName: string
  shopName: string
  shareLink: string
}

export const generatePoster = async (options: PosterOptions): Promise<string> => {
  const { title, minPrice, participantCount, endTime, leaderName, shopName, shareLink } = options
  const canvas = document.createElement('canvas')
  const width = 375
  const height = 600
  canvas.width = width * 2
  canvas.height = height * 2
  const ctx = canvas.getContext('2d')!
  ctx.scale(2, 2)

  // Background
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, width, height)

  // Header gradient
  const gradient = ctx.createLinearGradient(0, 0, width, 120)
  gradient.addColorStop(0, '#409EFF')
  gradient.addColorStop(1, '#67C23A')
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, width, 120)

  // Title
  ctx.fillStyle = '#ffffff'
  ctx.font = 'bold 20px sans-serif'
  ctx.textAlign = 'center'
  const displayTitle = title.length > 16 ? title.substring(0, 16) + '...' : title
  ctx.fillText(displayTitle, width / 2, 50)

  // Shop name
  if (shopName) {
    ctx.font = '14px sans-serif'
    ctx.fillText(shopName, width / 2, 80)
  }

  // Leader
  ctx.font = '12px sans-serif'
  ctx.fillText(`团长: ${leaderName}`, width / 2, 105)

  // Info section
  ctx.textAlign = 'left'
  ctx.fillStyle = '#333333'
  ctx.font = 'bold 16px sans-serif'
  ctx.fillText('活动信息', 20, 160)

  ctx.fillStyle = '#666666'
  ctx.font = '14px sans-serif'
  ctx.fillText(`最低价格: ¥${Number(minPrice).toFixed(2)}`, 20, 195)
  ctx.fillText(`参与人数: ${participantCount}人`, 20, 225)
  ctx.fillText(`截止时间: ${endTime}`, 20, 255)

  // Divider
  ctx.strokeStyle = '#EBEEF5'
  ctx.lineWidth = 1
  ctx.beginPath()
  ctx.moveTo(20, 280)
  ctx.lineTo(width - 20, 280)
  ctx.stroke()

  // QR code placeholder area
  ctx.fillStyle = '#f5f7fa'
  ctx.fillRect(width / 2 - 60, 300, 120, 120)
  ctx.fillStyle = '#909399'
  ctx.font = '12px sans-serif'
  ctx.textAlign = 'center'
  ctx.fillText('扫码参与团购', width / 2, 445)

  // Share link
  ctx.fillStyle = '#C0C4CC'
  ctx.font = '10px sans-serif'
  const displayLink = shareLink.length > 40 ? shareLink.substring(0, 40) + '...' : shareLink
  ctx.fillText(displayLink, width / 2, 475)

  // Footer
  ctx.fillStyle = '#409EFF'
  ctx.fillRect(20, 510, width - 40, 44)
  ctx.fillStyle = '#ffffff'
  ctx.font = 'bold 16px sans-serif'
  ctx.fillText('立即参与团购', width / 2, 538)

  // Watermark
  ctx.fillStyle = '#C0C4CC'
  ctx.font = '10px sans-serif'
  ctx.fillText('社区团购平台', width / 2, 580)

  return canvas.toDataURL('image/png')
}