import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { detectionApi } from '@/api'

export const useDetectionStore = defineStore('detection', () => {
  // 状态
  const currentImage = ref(null)
  const detectionResult = ref(null)
  const history = ref([])
  const loading = ref(false)
  const error = ref(null)
  const damages = ref([])
  const selectedDamage = ref(null)
  const carBrand = ref('')
  const carBrandConfidence = ref(0)
  const carModel = ref(null)
  const llmAnalysis = ref(null)
  const llmLoading = ref(false)

  // 计算属性
  const totalCost = computed(() => {
    if (!damages.value.length) return 0
    return damages.value.reduce((sum, damage) => sum + parseInt(damage.cost), 0)
  })

  const damageCount = computed(() => {
    return damages.value.length
  })

  const priorityGroups = computed(() => {
    const groups = {
      high: [],
      medium: [],
      low: []
    }

    damages.value.forEach(damage => {
      switch (damage.severity) {
        case 'severe':
          groups.high.push(damage)
          break
        case 'moderate':
          groups.medium.push(damage)
          break
        case 'minor':
          groups.low.push(damage)
          break
        default:
          groups.low.push(damage)
      }
    })

    return groups
  })

  // 操作
  const uploadImage = async (formData, onProgress) => {
    loading.value = true
    error.value = null
    
    try {
      const result = await detectionApi.detect(formData, onProgress)
      detectionResult.value = result
      
      // Store brand information
      carBrand.value = result?.brand || ''
      carBrandConfidence.value = result?.brand_confidence || 0
      
      // Store car model information
      carModel.value = result?.car_model || null
      
      if (result?.regions) {
        damages.value = result.regions.map(region => ({
          id: region.id,
          type: region.damage_type,
          severity: region.severity_level.toLowerCase(),
          part: region.part_code,
          confidence: region.confidence,
          bbox: region.bbox,
          cost: 0 // 成本在repair_items中
        }))
      }
      if (result?.images?.length > 0) {
        currentImage.value = result.images[0].image_url
      }
      return result
    } catch (err) {
      error.value = err.message || '上传失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchLLMAnalysis = async (taskId) => {
    error.value = null
    try {
      const result = await detectionApi.getLLMAnalysis(taskId)
      llmAnalysis.value = result
      return result
    } catch (err) {
      throw err
    }
  }

  const getResult = async (taskId, options) => {
    loading.value = true
    error.value = null
    
    try {
      const result = await detectionApi.getDetectionResult(taskId, options)
      detectionResult.value = result
      
      // Store brand information
      carBrand.value = result?.brand || ''
      carBrandConfidence.value = result?.brand_confidence || 0
      
      // Store car model information
      carModel.value = result?.car_model || null
      
      // 处理后端返回的数据结构，转换为前端期望的格式
      if (result?.regions) {
        damages.value = result.regions.map(region => ({
          id: region.id,
          type: region.damage_type,
          severity: region.severity_level.toLowerCase(),
          part: region.part_code,
          confidence: region.confidence,
          bbox: region.bbox,
          cost: 0 // 成本在repair_items中
        }))
      }

      if (result?.images?.length > 0) {
        currentImage.value = result.images[0].image_url
      }
      return result
    } catch (err) {
      error.value = err.message || '获取结果失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchHistory = async (params) => {
    loading.value = true
    error.value = null
    
    try {
      const result = await detectionApi.getHistory(params)
      history.value = result.data || []
      return result
    } catch (err) {
      error.value = err.message || '获取历史记录失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearResult = () => {
    detectionResult.value = null
    currentImage.value = null
    damages.value = []
    selectedDamage.value = null
    error.value = null
    carBrand.value = ''
    carBrandConfidence.value = 0
    carModel.value = null
    llmAnalysis.value = null
    llmLoading.value = false
  }

  const analyzeWithLLM = async (taskId) => {
    console.log('开始LLM分析，taskId:', taskId)
    llmLoading.value = true
    error.value = null
    
    try {
      console.log('调用API...')
      const result = await detectionApi.analyzeWithLLM(taskId)
      console.log('API返回结果:', result)
      llmAnalysis.value = result
      console.log('llmAnalysis已设置:', llmAnalysis.value)
      return result
    } catch (err) {
      console.error('LLM分析失败:', err)
      error.value = err.message || 'AI分析失败'
      throw err
    } finally {
      llmLoading.value = false
      console.log('llmLoading已设置为false')
    }
  }

  const selectDamage = (damage) => {
    selectedDamage.value = damage
  }

  return {
    // 状态
    currentImage,
    detectionResult,
    history,
    loading,
    error,
    damages,
    selectedDamage,
    carBrand,
    carBrandConfidence,
    carModel,
    llmAnalysis,
    llmLoading,
    // 计算属性
    totalCost,
    damageCount,
    priorityGroups,
    // 操作
    uploadImage,
    getResult,
    fetchHistory,
    clearResult,
    selectDamage,
    analyzeWithLLM,
    fetchLLMAnalysis
  }
}, {
  // 持久化配置
  persist: {
    key: 'detection-store',
    storage: localStorage,
    paths: ['history']
  }
})

