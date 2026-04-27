import QRCode from 'qrcode'

export interface PosterConfig {
  title: string
  coverImage: string
  minPrice: number
  participantCount: number
  endTime: string
  leaderName: string
  shopName: string
  shareLink: string
}

export const generatePoster = async (config: PosterConfig): Promise<string> => {
  return new Promise((resolve, reject) => {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    
    if (!ctx) {
      reject(new Error('Failed to get canvas context'))
      return
    }
    
    const width = 600
    const height = 900
    canvas.width = width
    canvas.height = height
    
    const gradient = ctx.createLinearGradient(0, 0, 0, height)
    gradient.addColorStop(0, '#FF6B6B')
    gradient.addColorStop(1, '#FF8E53')
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, width, height)
    
    ctx.fillStyle = '#FFFFFF'
    roundRect(ctx, 20, 20, width - 40, 350, 16)
    ctx.fill()
    
    if (config.coverImage) {
      const img = new Image()
      img.crossOrigin = 'anonymous'
      
      img.onload = async () => {
        const coverWidth = width - 80
        const coverHeight = 280
        const coverX = 40
        const coverY = 40
        
        ctx.save()
        roundRect(ctx, coverX, coverY, coverWidth, coverHeight, 8)
        ctx.clip()
        
        const imgRatio = img.width / img.height
        const coverRatio = coverWidth / coverHeight
        
        let drawWidth, drawHeight, offsetX, offsetY
        
        if (imgRatio > coverRatio) {
          drawHeight = coverHeight
          drawWidth = img.width * (coverHeight / img.height)
          offsetX = (coverWidth - drawWidth) / 2
          offsetY = 0
        } else {
          drawWidth = coverWidth
          drawHeight = img.height * (coverWidth / img.width)
          offsetX = 0
          offsetY = (coverHeight - drawHeight) / 2
        }
        
        ctx.drawImage(img, coverX + offsetX, coverY + offsetY, drawWidth, drawHeight)
        ctx.restore()
        
        drawPosterContent(ctx, canvas, config, resolve)
      }
      
      img.onerror = async () => {
        drawPlaceholderImage(ctx)
        drawPosterContent(ctx, canvas, config, resolve)
      }
      
      img.src = config.coverImage
    } else {
      drawPlaceholderImage(ctx)
      drawPosterContent(ctx, canvas, config, resolve)
    }
  })
}

function drawPlaceholderImage(ctx: CanvasRenderingContext2D) {
  const coverX = 40
  const coverY = 40
  const coverWidth = 520
  const coverHeight = 280
  
  ctx.fillStyle = '#F5F5F5'
  roundRect(ctx, coverX, coverY, coverWidth, coverHeight, 8)
  ctx.fill()
  
  ctx.fillStyle = '#CCCCCC'
  ctx.font = '48px sans-serif'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText('📷', coverX + coverWidth / 2, coverY + coverHeight / 2)
}

async function drawPosterContent(
  ctx: CanvasRenderingContext2D,
  canvas: HTMLCanvasElement,
  config: PosterConfig,
  resolve: (value: string) => void
) {
  const width = canvas.width
  let currentY = 400
  
  ctx.fillStyle = '#FFFFFF'
  roundRect(ctx, 20, currentY, width - 40, 150, 16)
  ctx.fill()
  
  ctx.fillStyle = '#333333'
  ctx.font = 'bold 28px sans-serif'
  ctx.textAlign = 'left'
  ctx.textBaseline = 'top'
  
  const title = truncateText(config.title, 420, ctx)
  ctx.fillText(title, 40, currentY + 20)
  
  ctx.fillStyle = '#FF6B6B'
  ctx.font = 'bold 36px sans-serif'
  ctx.fillText(`¥${config.minPrice.toFixed(2)}`, 40, currentY + 70)
  
  ctx.fillStyle = '#999999'
  ctx.font = '16px sans-serif'
  ctx.fillText('起', 40 + ctx.measureText(`¥${config.minPrice.toFixed(2)}`).width + 5, currentY + 82)
  
  ctx.fillStyle = '#666666'
  ctx.font = '16px sans-serif'
  ctx.fillText(`${config.participantCount}人已参加`, 40, currentY + 120)
  
  currentY += 170
  
  ctx.fillStyle = '#FFFFFF'
  roundRect(ctx, 20, currentY, width - 40, 300, 16)
  ctx.fill()
  
  const qrCodeDataUrl = await generateQRCode(config.shareLink, 180)
  const qrImg = new Image()
  
  qrImg.onload = () => {
    const qrX = 40
    const qrY = currentY + 30
    
    ctx.fillStyle = '#F5F5F5'
    roundRect(ctx, qrX - 5, qrY - 5, 190, 190, 8)
    ctx.fill()
    
    ctx.drawImage(qrImg, qrX, qrY, 180, 180)
    
    ctx.fillStyle = '#333333'
    ctx.font = 'bold 20px sans-serif'
    ctx.fillText('扫码立即参与', qrX + 210, qrY + 50)
    
    ctx.fillStyle = '#666666'
    ctx.font = '14px sans-serif'
    ctx.fillText(`团长: ${config.leaderName}`, qrX + 210, qrY + 85)
    ctx.fillText(`店铺: ${config.shopName || '未知'}`, qrX + 210, qrY + 110)
    
    ctx.fillStyle = '#999999'
    ctx.font = '12px sans-serif'
    ctx.fillText(`截止时间: ${config.endTime}`, 40, currentY + 260)
    
    resolve(canvas.toDataURL('image/png'))
  }
  
  qrImg.onerror = () => {
    ctx.fillStyle = '#333333'
    ctx.font = 'bold 20px sans-serif'
    ctx.fillText('扫码立即参与', 40, currentY + 50)
    
    ctx.fillStyle = '#666666'
    ctx.font = '14px sans-serif'
    ctx.fillText(`团长: ${config.leaderName}`, 40, currentY + 85)
    ctx.fillText(`店铺: ${config.shopName || '未知'}`, 40, currentY + 110)
    ctx.fillText(`链接: ${config.shareLink}`, 40, currentY + 135)
    
    resolve(canvas.toDataURL('image/png'))
  }
  
  qrImg.src = qrCodeDataUrl
}

async function generateQRCode(text: string, size: number): Promise<string> {
  try {
    return await QRCode.toDataURL(text, {
      width: size,
      margin: 2,
      color: {
        dark: '#000000',
        light: '#FFFFFF'
      }
    })
  } catch {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    canvas.width = size
    canvas.height = size
    
    if (ctx) {
      ctx.fillStyle = '#FFFFFF'
      ctx.fillRect(0, 0, size, size)
      ctx.fillStyle = '#000000'
      ctx.font = `${size / 10}px sans-serif`
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText('QR', size / 2, size / 2)
    }
    
    return canvas.toDataURL('image/png')
  }
}

function roundRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  width: number,
  height: number,
  radius: number
) {
  ctx.beginPath()
  ctx.moveTo(x + radius, y)
  ctx.lineTo(x + width - radius, y)
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius)
  ctx.lineTo(x + width, y + height - radius)
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height)
  ctx.lineTo(x + radius, y + height)
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius)
  ctx.lineTo(x, y + radius)
  ctx.quadraticCurveTo(x, y, x + radius, y)
  ctx.closePath()
}

function truncateText(text: string, maxWidth: number, ctx: CanvasRenderingContext2D): string {
  let truncated = text
  while (ctx.measureText(truncated).width > maxWidth && truncated.length > 0) {
    truncated = truncated.slice(0, -1)
  }
  return truncated.length < text.length ? truncated + '...' : truncated
}