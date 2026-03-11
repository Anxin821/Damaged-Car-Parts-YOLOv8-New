import api from './request'

export const reportsApi = {
  // 获取仪表板统计数据
  getDashboard: (days = 30) => api.get('/reports/dashboard', { params: { days } }),
  
  // 获取损伤类型统计
  getDamageTypes: (params = {}) => api.get('/reports/damage-types', { params }),
  
  // 获取品牌分布统计
  getBrandDistribution: (days = 30) => 
    api.get('/reports/brand-distribution', { params: { days } }),
  
  // 获取月度趋势分析
  getMonthlyTrend: (months = 12) => 
    api.get('/reports/monthly-trend', { params: { months } }),
  
  // 获取损伤严重程度分析
  getSeverityAnalysis: (days = 30) => 
    api.get('/reports/severity-analysis', { params: { days } }),
  
  // 获取处理时间分析
  getProcessingTime: (days = 30) => 
    api.get('/reports/processing-time', { params: { days } }),
  
  // 获取准确性指标
  getAccuracyMetrics: (days = 30) => 
    api.get('/reports/accuracy-metrics', { params: { days } }),
  
  // 获取综合统计报表
  getComprehensive: (days = 30) => 
    api.get('/reports/comprehensive', { params: { days } })
}
