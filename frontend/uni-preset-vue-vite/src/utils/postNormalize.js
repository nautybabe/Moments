const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const normalizeUrl = (url) => {
  if (!url) return ''
  const fixed = url.replace(/\\/g, '/')
  if (/^https?:\/\//i.test(fixed)) return fixed
  if (fixed.startsWith('/media/')) return `${API_BASE}${fixed}`
  return fixed
}

export function normalizePosts(list = [], fallbackAvatar = '') {
  return (list || []).map(item => {
    const mediaList = (item.media || []).filter(Boolean).map(normalizeUrl)
    const dedupMedia = Array.from(new Set(mediaList))
    const imageRegex = /\.(png|jpe?g|webp|gif|bmp|svg)$/i

    let type = item.type || (dedupMedia.length ? 'image' : 'text')
    let poster = item.poster ? normalizeUrl(item.poster) : ''
    let media = dedupMedia
    let mediaImages = dedupMedia.filter(url => imageRegex.test(url))
    let videoSrc = ''

    if (type === 'video') {
      let videoUrl = ''
      const images = []
      dedupMedia.forEach(url => {
        if (!url) return
        const isImage = imageRegex.test(url)
        const looksLikeVideo = url.includes('/uploads/videos/') || /\.mp4$/i.test(url)
        if (!videoUrl && (looksLikeVideo || !isImage)) {
          videoUrl = url
        } else if (isImage) {
          images.push(url)
        }
      })
      if (!videoUrl && images.length) {
        type = 'image'
        media = images
        mediaImages = images
        videoSrc = ''
        poster = ''
      } else {
        media = videoUrl ? [videoUrl] : []
        videoSrc = videoUrl
        mediaImages = images
        if (!poster || poster.includes('/uploads/videos/')) poster = ''
      }
    } else {
      // 非视频类型保留图片数组
      mediaImages = mediaImages.length ? mediaImages : dedupMedia
    }

    return {
      ...item,
      type,
      media,
      poster,
      mediaImages,
      videoSrc,
      avatar: item.avatar ? normalizeUrl(item.avatar) : (fallbackAvatar || item.avatar),
      time: item.time
    }
  })
}

export const apiBase = API_BASE
