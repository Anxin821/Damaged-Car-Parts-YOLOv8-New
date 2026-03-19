import api from './request'

export const detectionApi = {
  // 上传图片进行检测
  detect: (formData, onProgress) => api.post('/detection', formData, {
    timeout: 120000,
    onUploadProgress: (progressEvent) => {
      if (onProgress) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(percentCompleted)
      }
    }
  }),
  
  // 获取检测结果（轮询）
  getDetectionResult: (taskId, options = {}) => {
    const {
      interval = 2000, // 轮询间隔（毫秒）
      timeout = 60000, // 超时时间（毫秒）
      onProgress // 进度回调
    } = options
    
    return new Promise((resolve, reject) => {
      let startTime = Date.now()
      let pollingInterval
      
      const poll = () => {
        api.get(`/detection/result/${taskId}`, {}, { timeout: 120000 })
          .then(result => {
            if (result.status === 'completed') {
              clearInterval(pollingInterval)
              resolve(result)
            } else if (result.status === 'failed') {
              clearInterval(pollingInterval)
              reject(new Error('检测失败'))
            } else {
              // 检测中，继续轮询
              if (onProgress) {
                onProgress(result.progress || 0)
              }
              
              // 检查是否超时
              if (Date.now() - startTime > timeout) {
                clearInterval(pollingInterval)
                reject(new Error('检测超时'))
              }
            }
          })
          .catch(error => {
            clearInterval(pollingInterval)
            reject(error)
          })
      }
      
      // 立即执行一次
      poll()
      // 设置轮询
      pollingInterval = setInterval(poll, interval)
    })
  },
  
  // 获取历史记录（支持分页和筛选）
  getHistory: (params = {}) => {
    const {
      page = 1,
      pageSize = 10,
      startDate,
      endDate,
      damageType,
      severity
    } = params
    
    return api.get('/detection/history', {
      params: {
        page,
        pageSize,
        startDate,
        endDate,
        damageType,
        severity
      }
    })
  },
  
  // 获取检测详情
  getDetail: (id) => api.get(`/detection/${id}`),
  
  // 删除历史记录
  deleteHistory: (id) => api.delete(`/detection/history/${id}`),
  
  // 批量删除历史记录
  batchDeleteHistory: (ids) => api.delete('/detection/history', {
    data: { ids }
  }),
  
  // 导出报告
  exportReport: (id, format = 'pdf') => {
    return api.get(`/detection/export/${id}`, {
      params: { format },
      responseType: 'blob' // 重要：设置响应类型为blob
    }).then(blob => {
      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.style.display = 'none'
      a.href = url
      a.download = `detection-report-${id}.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      return true
    })
  },
  
  // LLM大模型分析
  analyzeWithLLM: (taskId) => api.post('/llm/analyze', null, {
    params: { task_id: taskId },
    timeout: 180000  // 180秒，与后端超时匹配
  })
}

