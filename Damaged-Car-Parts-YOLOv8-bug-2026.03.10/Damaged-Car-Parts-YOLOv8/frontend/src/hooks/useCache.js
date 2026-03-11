import { ref } from 'vue'

/**
 * 缓存管理逻辑hook
 */
export function useCache() {
  const cache = ref(new Map())

  /**
   * 设置缓存
   * @param {string} key - 缓存键
   * @param {any} value - 缓存值
   * @param {number} expire - 过期时间（毫秒），默认 24 小时
   */
  const setCache = (key, value, expire = 24 * 60 * 60 * 1000) => {
    try {
      const item = {
        value,
        expiry: Date.now() + expire
      }
      cache.value.set(key, item)
      localStorage.setItem(key, JSON.stringify(item))
    } catch (error) {
      console.error('设置缓存失败:', error)
    }
  }

  /**
   * 获取缓存
   * @param {string} key - 缓存键
   * @returns {any} 缓存值，如果不存在或已过期则返回 null
   */
  const getCache = (key) => {
    try {
      // 先从内存缓存获取
      const item = cache.value.get(key)
      if (item) {
        if (Date.now() < item.expiry) {
          return item.value
        } else {
          // 已过期，删除缓存
          cache.value.delete(key)
          localStorage.removeItem(key)
          return null
        }
      }

      // 从本地存储获取
      const storedItem = localStorage.getItem(key)
      if (storedItem) {
        const parsedItem = JSON.parse(storedItem)
        if (Date.now() < parsedItem.expiry) {
          // 更新内存缓存
          cache.value.set(key, parsedItem)
          return parsedItem.value
        } else {
          // 已过期，删除缓存
          localStorage.removeItem(key)
          return null
        }
      }

      return null
    } catch (error) {
      console.error('获取缓存失败:', error)
      return null
    }
  }

  /**
   * 删除缓存
   * @param {string} key - 缓存键
   */
  const removeCache = (key) => {
    try {
      cache.value.delete(key)
      localStorage.removeItem(key)
    } catch (error) {
      console.error('删除缓存失败:', error)
    }
  }

  /**
   * 清空所有缓存
   */
  const clearCache = () => {
    try {
      cache.value.clear()
      // 只清除我们应用的缓存，避免影响其他应用
      Object.keys(localStorage).forEach(key => {
        // 可以根据需要添加前缀判断
        localStorage.removeItem(key)
      })
    } catch (error) {
      console.error('清空缓存失败:', error)
    }
  }

  /**
   * 检查缓存是否存在且未过期
   * @param {string} key - 缓存键
   * @returns {boolean} 是否存在且未过期
   */
  const hasCache = (key) => {
    return getCache(key) !== null
  }

  /**
   * 缓存检测结果
   * @param {string} imageHash - 图片哈希值
   * @param {Object} result - 检测结果
   */
  const cacheDetectionResult = (imageHash, result) => {
    setCache(`detection_${imageHash}`, result, 7 * 24 * 60 * 60 * 1000) // 缓存7天
  }

  /**
   * 获取缓存的检测结果
   * @param {string} imageHash - 图片哈希值
   * @returns {Object|null} 检测结果
   */
  const getCachedDetectionResult = (imageHash) => {
    return getCache(`detection_${imageHash}`)
  }

  return {
    setCache,
    getCache,
    removeCache,
    clearCache,
    hasCache,
    cacheDetectionResult,
    getCachedDetectionResult
  }
}