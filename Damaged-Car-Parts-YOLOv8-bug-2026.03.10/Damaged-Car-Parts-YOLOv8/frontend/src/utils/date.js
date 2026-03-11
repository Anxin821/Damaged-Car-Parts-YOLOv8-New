/**
 * 日期工具
 */

/**
 * 格式化日期
 * @param {Date|string|number} date - 日期
 * @param {string} format - 格式化模板
 * @returns {string} - 格式化后的日期字符串
 */
export const formatDate = (date, format = 'YYYY-MM-DD') => {
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 获取相对时间
 * @param {Date|string|number} date - 日期
 * @returns {string} - 相对时间字符串
 */
export const getRelativeTime = (date) => {
  const now = new Date()
  const past = new Date(date)
  const diff = now - past

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 30) return `${days}天前`
  if (days < 365) return `${Math.floor(days / 30)}个月前`
  return `${Math.floor(days / 365)}年前`
}

/**
 * 获取今天的日期
 * @returns {Date} - 今天的日期
 */
export const getToday = () => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return today
}

/**
 * 获取本周的开始日期
 * @returns {Date} - 本周一的日期
 */
export const getWeekStart = () => {
  const today = new Date()
  const day = today.getDay() || 7
  const diff = today.getDate() - day + 1
  const weekStart = new Date(today)
  weekStart.setDate(diff)
  weekStart.setHours(0, 0, 0, 0)
  return weekStart
}

/**
 * 获取本月的开始日期
 * @returns {Date} - 本月1号的日期
 */
export const getMonthStart = () => {
  const today = new Date()
  const monthStart = new Date(today.getFullYear(), today.getMonth(), 1)
  monthStart.setHours(0, 0, 0, 0)
  return monthStart
}

/**
 * 判断是否是今天
 * @param {Date|string|number} date - 日期
 * @returns {boolean} - 是否是今天
 */
export const isToday = (date) => {
  const today = getToday()
  const d = new Date(date)
  d.setHours(0, 0, 0, 0)
  return d.getTime() === today.getTime()
}

/**
 * 计算两个日期之间的天数差
 * @param {Date|string|number} date1 - 第一个日期
 * @param {Date|string|number} date2 - 第二个日期
 * @returns {number} - 天数差
 */
export const getDaysDiff = (date1, date2) => {
  const d1 = new Date(date1)
  const d2 = new Date(date2)
  const diff = Math.abs(d1 - d2)
  return Math.floor(diff / 86400000)
}
