/**
 * DOM操作工具
 */

/**
 * 获取DOM元素
 * @param {string} selector - 选择器
 * @param {HTMLElement} parent - 父元素
 * @returns {HTMLElement|null} - DOM元素
 */
export const getElement = (selector, parent = document) => {
  return parent.querySelector(selector)
}

/**
 * 获取多个DOM元素
 * @param {string} selector - 选择器
 * @param {HTMLElement} parent - 父元素
 * @returns {NodeList} - DOM元素列表
 */
export const getElements = (selector, parent = document) => {
  return parent.querySelectorAll(selector)
}

/**
 * 添加类名
 * @param {HTMLElement} element - DOM元素
 * @param {string} className - 类名
 */
export const addClass = (element, className) => {
  if (element) {
    element.classList.add(className)
  }
}

/**
 * 移除类名
 * @param {HTMLElement} element - DOM元素
 * @param {string} className - 类名
 */
export const removeClass = (element, className) => {
  if (element) {
    element.classList.remove(className)
  }
}

/**
 * 切换类名
 * @param {HTMLElement} element - DOM元素
 * @param {string} className - 类名
 */
export const toggleClass = (element, className) => {
  if (element) {
    element.classList.toggle(className)
  }
}

/**
 * 检查是否有类名
 * @param {HTMLElement} element - DOM元素
 * @param {string} className - 类名
 * @returns {boolean} - 是否有类名
 */
export const hasClass = (element, className) => {
  if (element) {
    return element.classList.contains(className)
  }
  return false
}

/**
 * 设置样式
 * @param {HTMLElement} element - DOM元素
 * @param {Object} styles - 样式对象
 */
export const setStyle = (element, styles) => {
  if (element) {
    Object.assign(element.style, styles)
  }
}

/**
 * 获取元素位置
 * @param {HTMLElement} element - DOM元素
 * @returns {Object} - 元素位置信息
 */
export const getElementPosition = (element) => {
  if (!element) return { top: 0, left: 0, width: 0, height: 0 }
  const rect = element.getBoundingClientRect()
  return {
    top: rect.top + window.scrollY,
    left: rect.left + window.scrollX,
    width: rect.width,
    height: rect.height
  }
}

/**
 * 滚动到元素
 * @param {HTMLElement} element - DOM元素
 * @param {Object} options - 滚动选项
 */
export const scrollToElement = (element, options = {}) => {
  if (element) {
    element.scrollIntoView({
      behavior: 'smooth',
      block: 'center',
      inline: 'center',
      ...options
    })
  }
}

/**
 * 防抖函数
 * @param {Function} func - 要执行的函数
 * @param {number} delay - 延迟时间（毫秒）
 * @returns {Function} - 防抖后的函数
 */
export const debounce = (func, delay) => {
  let timeoutId
  return (...args) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func.apply(null, args), delay)
  }
}

/**
 * 节流函数
 * @param {Function} func - 要执行的函数
 * @param {number} limit - 时间限制（毫秒）
 * @returns {Function} - 节流后的函数
 */
export const throttle = (func, limit) => {
  let inThrottle
  return (...args) => {
    if (!inThrottle) {
      func.apply(null, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}
