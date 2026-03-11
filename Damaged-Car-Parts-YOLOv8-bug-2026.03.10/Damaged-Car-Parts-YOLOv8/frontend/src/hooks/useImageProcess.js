import { ref } from 'vue'

/**
 * 图片处理逻辑hook
 */
export function useImageProcess() {
  const previewUrl = ref(null)
  const processing = ref(false)
  const error = ref(null)

  /**
   * 生成图片预览URL
   * @param {File} file - 图片文件
   * @returns {string} 预览URL
   */
  const generatePreview = (file) => {
    if (!file) {
      previewUrl.value = null
      return null
    }

    try {
      const url = URL.createObjectURL(file)
      previewUrl.value = url
      return url
    } catch (err) {
      error.value = '生成预览失败'
      return null
    }
  }

  /**
   * 压缩图片
   * @param {File} file - 原始图片文件
   * @param {number} maxWidth - 最大宽度
   * @param {number} quality - 压缩质量 (0-1)
   * @returns {Promise<Blob>} 压缩后的图片Blob
   */
  const compressImage = async (file, maxWidth = 1200, quality = 0.8) => {
    processing.value = true
    error.value = null

    try {
      return new Promise((resolve, reject) => {
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')
        const img = new Image()

        img.onload = () => {
          const { width, height } = img
          const aspectRatio = width / height

          let newWidth = width
          let newHeight = height

          if (width > maxWidth) {
            newWidth = maxWidth
            newHeight = maxWidth / aspectRatio
          }

          canvas.width = newWidth
          canvas.height = newHeight

          ctx.drawImage(img, 0, 0, newWidth, newHeight)

          canvas.toBlob(
            (blob) => {
              if (blob) {
                resolve(blob)
              } else {
                reject(new Error('压缩失败'))
              }
            },
            'image/jpeg',
            quality
          )
        }

        img.onerror = () => {
          reject(new Error('图片加载失败'))
        }

        img.src = URL.createObjectURL(file)
      })
    } catch (err) {
      error.value = '压缩图片失败'
      throw err
    } finally {
      processing.value = false
    }
  }

  /**
   * 验证图片文件
   * @param {File} file - 图片文件
   * @returns {Object} 验证结果
   */
  const validateImage = (file) => {
    if (!file) {
      return { valid: false, message: '请选择图片' }
    }

    const validTypes = ['image/jpeg', 'image/jpg', 'image/png']
    if (!validTypes.includes(file.type)) {
      return { valid: false, message: '只支持 JPG、PNG 格式图片' }
    }

    const maxSize = 10 * 1024 * 1024 // 10MB
    if (file.size > maxSize) {
      return { valid: false, message: '图片大小不能超过 10MB' }
    }

    return { valid: true, message: '' }
  }

  /**
   * 清理预览URL
   */
  const cleanupPreview = () => {
    if (previewUrl.value) {
      URL.revokeObjectURL(previewUrl.value)
      previewUrl.value = null
    }
  }

  return {
    previewUrl,
    processing,
    error,
    generatePreview,
    compressImage,
    validateImage,
    cleanupPreview
  }
}