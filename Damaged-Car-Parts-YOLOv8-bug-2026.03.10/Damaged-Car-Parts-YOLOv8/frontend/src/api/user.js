import api from './request'

export const userApi = {
  // 登录
  login: (data) => api.post('/user/login', data),
  
  // 注册
  register: (data) => api.post('/user/register', data),
  
  // 获取用户信息
  getInfo: () => api.get('/user/info'),
  
  // 更新用户信息
  updateInfo: (data) => api.put('/user/info', data),
  
  // 修改密码
  changePassword: (data) => api.put('/user/password', data),
  
  // 上传头像
  uploadAvatar: (file, onProgress) => {
    const formData = new FormData()
    formData.append('avatar', file)
    
    return api.post('/user/avatar', formData, {
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(percentCompleted)
        }
      }
    })
  },
  
  // 获取用户统计
  getStatistics: () => api.get('/user/statistics'),
  
  // 登出
  logout: () => api.post('/user/logout')
}

