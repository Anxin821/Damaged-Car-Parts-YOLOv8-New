import api from './request'

export const repairApi = {
  // 获取预修车优先级分析
  getPriorityAnalysis: (assessmentId) => api.get(`/repair/assessment/${assessmentId}/priority-analysis`),
  
  // 获取定损维修项目列表
  getRepairItems: (assessmentId, priorityOnly = false) => 
    api.get(`/repair/assessment/${assessmentId}/repair-items`, { 
      params: { priority_only: priorityOnly } 
    }),
  
  // 更新维修项目优先级
  updateRepairPriority: (itemId, priority) => 
    api.put(`/repair/repair-items/${itemId}/priority`, { priority }),
  
  // 批量预修车分析
  batchPriorityAnalysis: (assessmentIds) => 
    api.get('/repair/batch-priority-analysis', { 
      params: { assessment_ids: assessmentIds } 
    })
}
