import api from './request'

export const historyApi = {
  // 获取历史记录列表 (修正路径为 /api/detection/history)
  getHistory: (params = {}) => api.get('/detection/history', { params }),
  // 删除历史记录
  deleteHistory: (taskId) => api.delete(`/detection/history/${taskId}`),
  // 清空历史记录
  clearHistory: () => api.delete('/detection/history')
}
