/**
 * 缓存工具
 */

/**
 * 存储数据到localStorage
 * @param {string} key - 缓存键名
 * @param {any} value - 缓存值
 * @param {number} expire - 过期时间（毫秒）
 */
export const setCache = (key, value, expire = null) => {
  const data = {
    value,
    expire: expire ? Date.now() + expire : null
  }
  localStorage.setItem(key, JSON.stringify(data))
}

/**
 * 从localStorage获取数据
 * @param {string} key - 缓存键名
 * @returns {any} - 缓存值
 */
export const getCache = (key) => {
  const item = localStorage.getItem(key)
  if (!item) return null

  try {
    const data = JSON.parse(item)
    if (data.expire && Date.now() > data.expire) {
      localStorage.removeItem(key)
      return null
    }
    return data.value
  } catch (error) {
    localStorage.removeItem(key)
    return null
  }
}

/**
 * 删除localStorage中的数据
 * @param {string} key - 缓存键名
 */
export const removeCache = (key) => {
  localStorage.removeItem(key)
}

/**
 * 清空localStorage
 */
export const clearCache = () => {
  localStorage.clear()
}

/**
 * 存储数据到sessionStorage
 * @param {string} key - 缓存键名
 * @param {any} value - 缓存值
 */
export const setSessionCache = (key, value) => {
  sessionStorage.setItem(key, JSON.stringify(value))
}

/**
 * 从sessionStorage获取数据
 * @param {string} key - 缓存键名
 * @returns {any} - 缓存值
 */
export const getSessionCache = (key) => {
  const item = sessionStorage.getItem(key)
  if (!item) return null

  try {
    return JSON.parse(item)
  } catch (error) {
    sessionStorage.removeItem(key)
    return null
  }
}

/**
 * 删除sessionStorage中的数据
 * @param {string} key - 缓存键名
 */
export const removeSessionCache = (key) => {
  sessionStorage.removeItem(key)
}

/**
 * 清空sessionStorage
 */
export const clearSessionCache = () => {
  sessionStorage.clear()
}
