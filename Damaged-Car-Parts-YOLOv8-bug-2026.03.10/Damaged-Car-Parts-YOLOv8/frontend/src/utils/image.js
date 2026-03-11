/**
 * 图片处理工具
 */

/**
 * 将文件转换为Base64
 * @param {File} file - 图片文件
 * @returns {Promise<string>} - Base64字符串
 */
export const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

/**
 * 压缩图片
 * @param {File} file - 图片文件
 * @param {number} maxWidth - 最大宽度
 * @param {number} quality - 压缩质量 (0-1)
 * @returns {Promise<Blob>} - 压缩后的图片Blob
 */
export const compressImage = (file, maxWidth = 1024, quality = 0.8) => {
  return new Promise((resolve) => {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    const img = new Image()

    img.onload = () => {
      const ratio = Math.min(maxWidth / img.width, maxWidth / img.height)
      canvas.width = img.width * ratio
      canvas.height = img.height * ratio

      ctx.drawImage(img, 0, 0, canvas.width, canvas.height)

      canvas.toBlob((blob) => {
        resolve(blob)
      }, file.type, quality)
    }

    img.src = URL.createObjectURL(file)
  })
}

/**
 * 获取图片尺寸
 * @param {string} url - 图片URL
 * @returns {Promise<{width: number, height: number}>} - 图片尺寸
 */
export const getImageSize = (url) => {
  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => {
      resolve({ width: img.width, height: img.height })
    }
    img.src = url
  })
}

/**
 * 验证图片文件类型
 * @param {File} file - 图片文件
 * @param {string[]} allowedTypes - 允许的文件类型
 * @returns {boolean} - 是否为允许的图片类型
 */
export const validateImageType = (file, allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']) => {
  return allowedTypes.includes(file.type)
}

/**
 * 验证图片文件大小
 * @param {File} file - 图片文件
 * @param {number} maxSize - 最大大小（字节）
 * @returns {boolean} - 是否在允许的大小范围内
 */
export const validateImageSize = (file, maxSize = 5 * 1024 * 1024) => {
  return file.size <= maxSize
}
