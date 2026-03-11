import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 用于存储请求取消令牌的映射
const cancelTokenMap = new Map()

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 生成请求唯一标识
    const requestKey = `${config.method}:${config.url}`
    
    // 取消之前的同名请求
    if (cancelTokenMap.has(requestKey)) {
      cancelTokenMap.get(requestKey)()
    }
    
    // 创建新的取消令牌
    const source = axios.CancelToken.source()
    config.cancelToken = source.token
    cancelTokenMap.set(requestKey, source.cancel)
    
    // 添加 token 认证信息
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    // 从取消令牌映射中移除已完成的请求
    const requestKey = `${response.config.method}:${response.config.url}`
    cancelTokenMap.delete(requestKey)
    
    return response.data
  },
  error => {
    // 从取消令牌映射中移除失败的请求
    if (error.config) {
      const requestKey = `${error.config.method}:${error.config.url}`
      cancelTokenMap.delete(requestKey)
    }
    
    // 统一处理错误
    if (axios.isCancel(error)) {
      console.log('请求已取消:', error.message)
    } else if (error.response) {
      // 服务器返回错误
      console.error('API 响应错误:', {
        status: error.response.status,
        data: error.response.data
      })
      
      // 可以根据状态码进行不同的处理
      switch (error.response.status) {
        case 401:
          // 未授权，跳转到登录页
          // router.push('/login')
          break
        case 403:
          // 禁止访问
          console.error('无权限访问')
          break
        case 404:
          // 资源不存在
          console.error('请求的资源不存在')
          break
        case 500:
          // 服务器错误
          console.error('服务器内部错误')
          break
        default:
          console.error('请求失败:', error.response.status)
      }
    } else if (error.request) {
      // 请求已发出，但没有收到响应
      console.error('未收到响应:', error.request)
    } else {
      // 请求配置出错
      console.error('请求配置错误:', error.message)
    }
    
    return Promise.reject(error)
  }
)

// 请求重试机制
const retryRequest = (config, retryCount = 3, retryDelay = 1000) => {
  return new Promise((resolve, reject) => {
    const attempt = (count) => {
      api(config)
        .then(resolve)
        .catch(error => {
          if (count > 0 && !axios.isCancel(error) && 
              (error.code === 'ECONNABORTED' || 
               (error.response && error.response.status >= 500))) {
            console.log(`请求重试 ${3 - count + 1}/3`)
            setTimeout(() => attempt(count - 1), retryDelay)
          } else {
            reject(error)
          }
        })
    }
    attempt(retryCount)
  })
}

// 封装常用的请求方法
const request = {
  // GET 请求
  get(url, params = {}, config = {}) {
    return api({
      method: 'get',
      url,
      params,
      ...config
    })
  },
  
  // POST 请求
  post(url, data = {}, config = {}) {
    return api({
      method: 'post',
      url,
      data,
      ...config
    })
  },
  
  // PUT 请求
  put(url, data = {}, config = {}) {
    return api({
      method: 'put',
      url,
      data,
      ...config
    })
  },
  
  // DELETE 请求
  delete(url, params = {}, config = {}) {
    return api({
      method: 'delete',
      url,
      params,
      ...config
    })
  },
  
  // 带重试的请求
  retry(url, config = {}) {
    return retryRequest({
      url,
      ...config
    })
  },
  
  // 取消请求
  cancel(url, method = 'get') {
    const requestKey = `${method}:${url}`
    if (cancelTokenMap.has(requestKey)) {
      cancelTokenMap.get(requestKey)('请求被取消')
      cancelTokenMap.delete(requestKey)
      return true
    }
    return false
  },
  
  // 取消所有请求
  cancelAll() {
    cancelTokenMap.forEach(cancel => cancel('所有请求被取消'))
    cancelTokenMap.clear()
  }
}

export default request

