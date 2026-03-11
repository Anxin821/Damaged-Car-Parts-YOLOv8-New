import api from './request'

export const feedbackApi = {
  // 提交意见与反馈
  create: (payload) => api.post('/feedback', payload),
  
  // 获取反馈列表（管理端）
  getList: (params = {}) => api.get('/feedback', { params }),
  
  // 获取反馈详情
  getDetail: (id) => api.get(`/feedback/${id}`),
  
  // 处理/回复反馈（管理端） sh
  update: (id, payload) => api.put(`/feedback/${id}`, payload)
}

