// 前端适配：使用结构化 API
// 修改 detection.js 和 detection.js 以支持新的数据结构

import { computed, onMounted } from 'vue'
import { useDetectionStore } from './store/detection'
import api from './api'

// ===== detection.js API 适配 =====

// 在原有的 detectionApi 对象中添加新方法
const detectionApi = {
  // ... 原有方法保持不变
  
  // 新增：获取结构化评估报告
  getStructuredAssessment: (taskId) => api.get(`/detection/structured/${taskId}`),
  
  // 新增：获取评估摘要
  getAssessmentSummary: (taskId) => api.get(`/detection/structured/${taskId}/summary`),
  
  // 新增：获取统计数据
  getDamageLevelStats: () => api.get('/detection/structured/stats/damage-level'),
  getRepairPriorityStats: () => api.get('/detection/structured/stats/repair-priority'),
  
  // 兼容性：保持原有接口不变
  getResult: (taskId, options = {}) => api.get(`/detection/result/${taskId}`, options),
  // ... 其他原有方法
}

export { detectionApi }

// ===== detection.js Store 适配 =====

import { defineStore } from 'pinia'
import { detectionApi } from './detection'

export const useDetectionStore = defineStore('detection', {
  state: () => ({
    // ... 原有 state 保持不变
    structuredAssessment: null,  // 新增：结构化评估数据
    assessmentSummary: null,     // 新增：评估摘要
    damageStats: null,           // 新增：统计数据
  }),
  
  getters: {
    // ... 原有 getters 保持不变
    
    // 新增：从结构化数据获取损伤部位
    damageParts: (state) => {
      return state.structuredAssessment?.damage_parts || []
    },
    
    // 新增：从结构化数据获取维修项目
    repairItems: (state) => {
      return state.structuredAssessment?.repair_items || []
    },
    
    // 新增：从结构化数据获取安全提示
    safetyTips: (state) => {
      return state.structuredAssessment?.safety_tips || []
    },
    
    // 新增：总费用（从结构化数据）
    totalCost: (state) => {
      return state.structuredAssessment?.assessment?.total_cost || 0
    },
    
    // 新增：车辆信息（从结构化数据）
    vehicleInfoStructured: (state) => {
      return state.structuredAssessment?.vehicle_info || null
    }
  },
  
  actions: {
    // ... 原有 actions 保持不变
    
    // 新增：获取结构化评估报告
    async fetchStructuredAssessment(taskId) {
      try {
        const response = await detectionApi.getStructuredAssessment(taskId)
        this.structuredAssessment = response.data
        
        // 同时更新摘要
        this.assessmentSummary = {
          id: response.data.assessment.id,
          task_id: response.data.assessment.task_id,
          status: response.data.assessment.status,
          vehicle_brand: response.data.assessment.vehicle_brand,
          vehicle_model: response.data.assessment.vehicle_model,
          total_cost: response.data.assessment.total_cost,
          damage_parts_count: response.data.damage_parts.length,
          repair_items_count: response.data.repair_items.length,
          safety_tips_count: response.data.safety_tips.length,
          created_at: response.data.assessment.created_at,
          completed_at: response.data.assessment.completed_at
        }
        
        return response.data
      } catch (error) {
        console.error('获取结构化评估数据失败:', error)
        throw error
      }
    },
    
    // 新增：获取统计数据
    async fetchDamageStats() {
      try {
        const [damageLevelStats, repairPriorityStats] = await Promise.all([
          detectionApi.getDamageLevelStats(),
          detectionApi.getRepairPriorityStats()
        ])
        
        this.damageStats = {
          damageLevel: damageLevelStats.data,
          repairPriority: repairPriorityStats.data
        }
        
        return this.damageStats
      } catch (error) {
        console.error('获取统计数据失败:', error)
        throw error
      }
    },
    
    // 新增：保存评估数据（结构化）
    async saveStructuredAssessment(taskId, assessmentData) {
      try {
        // 这里需要根据实际的后端保存接口来实现
        const response = await api.post('/detection/structured/save', {
          task_id: taskId,
          ...assessmentData
        })
        
        // 保存成功后刷新数据
        await this.fetchStructuredAssessment(taskId)
        
        return response.data
      } catch (error) {
        console.error('保存结构化评估数据失败:', error)
        throw error
      }
    }
  }
})

// ===== WechatDamageDetail.vue 组件适配 =====

// 在 script setup 中添加新的 computed 和方法

import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const detectionStore = useDetectionStore()
const route = useRoute()
const taskId = computed(() => route.params.taskId)
const hasData = computed(() => detectionStore.detectionResult && detectionStore.detectionResult.taskId === taskId.value)
const llmAnalysis = computed(() => detectionStore.llmAnalysis)

// 从结构化数据获取车辆信息
const vehicleInfoStructured = computed(() => {
  const structured = detectionStore.structuredAssessment
  if (!structured?.vehicle_info) return { brand: '待识别', model: '待识别' }
  
  return {
    brand: structured.vehicle_info.brand,
    model: structured.vehicle_info.model
  }
})

// 从结构化数据获取损伤详情
const damageInfoStructured = computed(() => {
  const structured = detectionStore.structuredAssessment
  if (!structured) return null
  
  const assessment = structured.assessment
  const damageParts = structured.damage_parts || []
  const repairItems = structured.repair_items || []
  
  return {
    id: assessment.task_id,
    carModel: `${assessment.vehicle_brand} ${assessment.vehicle_model}`,
    detectionTime: assessment.created_at,
    damageCount: damageParts.length,
    damageDetails: damageParts.map(part => ({
      location: part.part_name,
      type: part.damage_type || '未知损伤',
      level: part.damage_level,
      levelClass: getSeverityClass(part.damage_level),
      repairPriority: part.repair_priority,
      repairSuggestion: part.repair_suggestion
    })),
    budgetDetails: repairItems.map(item => ({
      item: item.item_name,
      severity: item.repair_priority,
      operation: item.repair_method || '未知',
      partNumber: item.parts_name || '',
      parts: item.parts_cost,
      labor: item.labor_cost,
      total: item.total_cost,
      notes: item.notes || ''
    })),
    totalBudget: assessment.total_cost || 0,
    currentImage: ''  // 需要从其他地方获取
  }
})

// 获取安全提示（结构化）
const safetyTipsStructured = computed(() => {
  return detectionStore.safetyTips.map(tip => tip.tip_text)
})

// 获取维修建议（结构化）
const repairSuggestionStructured = computed(() => {
  const assessment = detectionStore.structuredAssessment?.assessment
  return assessment?.assessment_conclusion || ''
})

// 在 onMounted 中添加结构化数据获取
onMounted(async () => {
  if (taskId.value) {
    try {
      // 优先获取结构化数据
      await detectionStore.fetchStructuredAssessment(taskId.value)
    } catch (error) {
      console.warn('获取结构化数据失败，回退到原有方式:', error)
      
      // 回退到原有的数据获取方式
      if (!hasData.value) {
        try {
          await detectionStore.getResult(taskId.value, { timeout: 60000, interval: 1000 })
        } catch (err) {
          console.error('获取检测结果失败:', err)
        }
      }
      
      if (!llmAnalysis.value) {
        try {
          await detectionStore.fetchLLMAnalysis(taskId.value)
        } catch (err) {
          console.error('获取AI分析结果失败:', err)
        }
      }
    }
  }
})

// 获取严重程度样式类（兼容豆包返回的中文）
const getSeverityClass = (severity) => {
  const severityMap = {
    '轻微': 'severity-low',
    '轻度': 'severity-low',
    '中等': 'severity-medium',
    '中度': 'severity-medium',
    '严重': 'severity-high',
    '重度': 'severity-high'
  }
  return severityMap[severity] || 'severity-unknown'
}

// 在模板中使用结构化数据（示例）
/*
<div v-if="vehicleInfoStructured">
  <p>品牌：{{ vehicleInfoStructured.brand }}</p>
  <p>车型：{{ vehicleInfoStructured.model }}</p>
</div>

<div v-if="damageInfoStructured">
  <div v-for="item in damageInfoStructured.damageDetails" :key="item.location">
    {{ item.location }} - {{ item.level }}
  </div>
</div>
*/
