/**
 * 价格计算工具
 */

/**
 * 计算折扣价格
 * @param {number} originalPrice - 原价
 * @param {number} discount - 折扣（0-1）
 * @returns {number} - 折扣后价格
 */
export const calculateDiscountPrice = (originalPrice, discount) => {
  return originalPrice * discount
}

/**
 * 计算税费
 * @param {number} price - 价格
 * @param {number} taxRate - 税率（0-1）
 * @returns {number} - 税费
 */
export const calculateTax = (price, taxRate) => {
  return price * taxRate
}

/**
 * 计算总价
 * @param {Array} items - 商品列表
 * @param {Function} priceGetter - 价格获取函数
 * @returns {number} - 总价
 */
export const calculateTotalPrice = (items, priceGetter = item => item.price) => {
  return items.reduce((total, item) => total + priceGetter(item), 0)
}

/**
 * 计算平均价格
 * @param {Array} items - 商品列表
 * @param {Function} priceGetter - 价格获取函数
 * @returns {number} - 平均价格
 */
export const calculateAveragePrice = (items, priceGetter = item => item.price) => {
  if (items.length === 0) return 0
  return calculateTotalPrice(items, priceGetter) / items.length
}

/**
 * 格式化价格范围
 * @param {number} minPrice - 最低价格
 * @param {number} maxPrice - 最高价格
 * @param {string} currency - 货币符号
 * @returns {string} - 价格范围字符串
 */
export const formatPriceRange = (minPrice, maxPrice, currency = '¥') => {
  if (minPrice === maxPrice) {
    return `${currency}${minPrice.toFixed(2)}`
  }
  return `${currency}${minPrice.toFixed(2)} - ${currency}${maxPrice.toFixed(2)}`
}
