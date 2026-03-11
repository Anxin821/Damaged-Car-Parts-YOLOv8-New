/**
 * 格式化工具
 */

/**
 * 格式化数字为千分位
 * @param {number} num - 数字
 * @returns {string} - 格式化后的字符串
 */
export const formatNumber = (num) => {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @returns {string} - 格式化后的文件大小
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 格式化价格
 * @param {number} price - 价格
 * @param {string} currency - 货币符号
 * @returns {string} - 格式化后的价格
 */
export const formatPrice = (price, currency = '¥') => {
  return `${currency}${formatNumber(price.toFixed(2))}`
}

/**
 * 格式化百分比
 * @param {number} value - 数值
 * @param {number} total - 总数
 * @param {number} decimals - 小数位数
 * @returns {string} - 格式化后的百分比
 */
export const formatPercentage = (value, total, decimals = 2) => {
  if (total === 0) return '0%'
  const percentage = (value / total) * 100
  return `${percentage.toFixed(decimals)}%`
}

/**
 * 格式化数组为字符串
 * @param {Array} array - 数组
 * @param {string} separator - 分隔符
 * @returns {string} - 格式化后的字符串
 */
export const formatArray = (array, separator = ', ') => {
  return array.join(separator)
}

/**
 * 格式化对象为查询字符串
 * @param {Object} obj - 对象
 * @returns {string} - 查询字符串
 */
export const formatQueryString = (obj) => {
  return Object.keys(obj)
    .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(obj[key])}`)
    .join('&')
}
