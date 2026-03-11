/**
 * 应用常量
 */

// API相关常量
export const API = {
  BASE_URL: '/api',
  TIMEOUT: 10000,
  ENDPOINTS: {
    DETECTION: '/detection',
    USER: {
      LOGIN: '/user/login',
      REGISTER: '/user/register',
      INFO: '/user/info'
    },
    HISTORY: '/history'
  }
}

// 本地存储键名
export const STORAGE_KEYS = {
  TOKEN: 'token',
  THEME: 'theme',
  DETECTION_HISTORY: 'detectionHistory',
  USER_INFO: 'userInfo'
}

// 图片相关常量
export const IMAGE = {
  MAX_SIZE: 5 * 1024 * 1024, // 5MB
  ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
  MAX_WIDTH: 1024
}

// 检测相关常量
export const DETECTION = {
  STATUS: {
    PENDING: 'pending',
    PROCESSING: 'processing',
    SUCCESS: 'success',
    ERROR: 'error'
  },
  DAMAGE_TYPES: [
    'scratch',
    'dent',
    'crack',
    'broken',
    'missing'
  ],
  SEVERITY_LEVELS: [
    'minor',
    'moderate',
    'severe'
  ]
}

// 路由相关常量
export const ROUTES = {
  HOME: '/',
  DETECTION: '/detection',
  HISTORY: '/history',
  LOGIN: '/login',
  PROFILE: '/profile',
  ABOUT: '/about',
  NOT_FOUND: '/:pathMatch(.*)*'
}

// 响应状态码
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  SERVER_ERROR: 500
}
