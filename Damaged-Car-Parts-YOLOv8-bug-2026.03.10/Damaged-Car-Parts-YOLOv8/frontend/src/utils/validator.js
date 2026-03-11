/**
 * 验证工具
 */

/**
 * 验证邮箱格式
 * @param {string} email - 邮箱地址
 * @returns {boolean} - 是否为有效邮箱
 */
export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * 验证手机号格式
 * @param {string} phone - 手机号
 * @returns {boolean} - 是否为有效手机号
 */
export const validatePhone = (phone) => {
  const phoneRegex = /^1[3-9]\d{9}$/
  return phoneRegex.test(phone)
}

/**
 * 验证密码强度
 * @param {string} password - 密码
 * @returns {object} - 密码强度信息
 */
export const validatePassword = (password) => {
  const strength = {
    score: 0,
    message: ''
  }

  if (password.length < 6) {
    strength.message = '密码长度至少6位'
    return strength
  }

  if (password.length >= 8) strength.score += 1
  if (/[A-Z]/.test(password)) strength.score += 1
  if (/[a-z]/.test(password)) strength.score += 1
  if (/\d/.test(password)) strength.score += 1
  if (/[^A-Za-z0-9]/.test(password)) strength.score += 1

  switch (strength.score) {
    case 1:
      strength.message = '密码强度：弱'
      break
    case 2:
    case 3:
      strength.message = '密码强度：中'
      break
    case 4:
    case 5:
      strength.message = '密码强度：强'
      break
  }

  return strength
}

/**
 * 验证身份证号格式
 * @param {string} idCard - 身份证号
 * @returns {boolean} - 是否为有效身份证号
 */
export const validateIdCard = (idCard) => {
  const idCardRegex = /^[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[0-9Xx]$/
  return idCardRegex.test(idCard)
}

/**
 * 验证URL格式
 * @param {string} url - URL地址
 * @returns {boolean} - 是否为有效URL
 */
export const validateUrl = (url) => {
  try {
    new URL(url)
    return true
  } catch (error) {
    return false
  }
}

/**
 * 验证是否为空
 * @param {any} value - 要验证的值
 * @returns {boolean} - 是否为空
 */
export const isEmpty = (value) => {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim() === ''
  if (Array.isArray(value)) return value.length === 0
  if (typeof value === 'object') return Object.keys(value).length === 0
  return false
}
