import api from './request'

export const historyApi = {
  // 获取历史记录列表
  getHistory: () => api.get('/history'),
  // 获取历史记录详情
  getHistoryDetail: (id) => api.get(`/history/${id}`),
  // 删除历史记录
  deleteHistory: (id) => api.delete(`/history/${id}`),
  // 清空历史记录
  clearHistory: () => api.delete('/history')
}
