<template>
  <div class="pre-repair-analysis">
    <WechatNavBar title="预修车分析" :showHome="true" />
    
    <div class="main-content">
      <!-- 顶部车辆信息 -->
      <div class="vehicle-header">
        <div class="vehicle-info">
          <div class="info-row">
            <span class="info-label">定损单号：</span>
            <span class="info-value">{{ detectionStore.detectionResult?.taskId || '未知' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">检测时间：</span>
            <span class="info-value">{{ new Date().toLocaleString('zh-CN') }}</span>
          </div>
        </div>
      </div>
      
      <!-- 优先级排序列表 -->
      <div class="priority-section">
        <div class="section-header">
          <h2 class="section-title">维修优先级排序</h2>
          <div class="priority-legend">
            <span class="legend-item high">
              <span class="legend-dot"></span>高优先级
            </span>
            <span class="legend-item medium">
              <span class="legend-dot"></span>中优先级
            </span>
            <span class="legend-item low">
              <span class="legend-dot"></span>低优先级
            </span>
          </div>
        </div>
        
        <div class="priority-list">
          <div 
            v-for="(item, index) in damageList" 
            :key="index"
            class="priority-item"
            :class="`priority-${item.priority}`"
          >
            <div class="item-header">
              <div class="priority-indicator">
                <span class="priority-number">{{ index + 1 }}</span>
                <span class="priority-badge" :class="item.priority">{{ getPriorityText(item.priority) }}</span>
              </div>
              <div class="damage-type-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 2v10l4 2"/>
                </svg>
              </div>
            </div>
            
            <div class="damage-content">
              <h3 class="damage-location">{{ item.location }}</h3>
              <div class="damage-tags">
                <span class="damage-tag">{{ item.type }}</span>
                <span class="severity-tag" :class="getSeverityClass(item.level)">{{ item.level }}</span>
              </div>
              
              <div class="impact-analysis">
                <div class="impact-header">
                  <span class="warning-icon">⚠️</span>
                  <span class="impact-title">影响分析</span>
                </div>
                <p class="impact-text">{{ item.impact }}</p>
              </div>
              
              <div class="repair-suggestion">
                <div class="suggestion-header">
                  <svg class="tool-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
                  </svg>
                  <span class="suggestion-title">维修建议</span>
                </div>
                <p class="suggestion-text">{{ item.recommendation }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDetectionStore } from '../store/detection'
import WechatNavBar from '../components/common/WechatNavBar.vue'

const route = useRoute()
const router = useRouter()
const detectionStore = useDetectionStore()

// 从路由参数获取数据
const taskId = route.query.taskId
const from = route.query.from

// 基于检测数据生成预修车分析
const damageList = computed(() => {
  const result = detectionStore.detectionResult
  if (!result || !result.regions) return []
  
  const partMap = {
    'damaged door': '车门', 'damaged window': '车窗', 'damaged headlight': '前大灯',
    'damaged mirror': '后视镜', 'dent': '凹陷', 'damaged hood': '引擎盖',
    'damaged bumper': '保险杠', 'damaged wind shield': '挡风玻璃'
  }
  
  const damageTypeMap = {
    'PAINT': '车漆损伤', 'PAINT_DAMAGE': '车漆损伤',
    'GLASS': '玻璃损伤', 'GLASS_DAMAGE': '玻璃损伤',
    'METAL': '钣金损伤', 'METAL_DAMAGE': '钣金损伤',
    'SCRATCH': '划痕', 'DENT': '凹陷',
    'CRACK': '裂纹', 'BROKEN': '破损'
  }
  
  return result.regions.map((region, index) => {
    const severity = region.severity_level || 'MEDIUM'
    const priority = getPriority(severity)
    const partName = partMap[region.part_code] || region.part_code || '未知部位'
    const damageType = damageTypeMap[region.damage_type] || region.damage_type || '未知损伤'
    
    return {
      priority: priority,
      priorityText: getPriorityText(priority),
      location: partName,
      type: damageType,
      level: getSeverityText(severity),
      impact: getImpactDescription(severity, partName),
      recommendation: getRepairRecommendation(damageType, severity),
      time: getRepairTime(damageType, severity),
      cost: getRepairCost(damageType, severity)
    }
  }).sort((a, b) => {
    // 按优先级倒序排列：高 → 中 → 低
    const priorityOrder = { high: 3, medium: 2, low: 1 }
    return priorityOrder[b.priority] - priorityOrder[a.priority]
  })
})

// 获取优先级
const getPriority = (severity) => {
  if (severity === 'HIGH' || severity === 'SEVERE' || severity === 'CRITICAL') return 'high'
  if (severity === 'MEDIUM' || severity === 'MODERATE') return 'medium'
  return 'low'
}

// 获取优先级文本
const getPriorityText = (priority) => {
  const textMap = {
    'high': '高优先级',
    'medium': '中优先级',
    'low': '低优先级'
  }
  return textMap[priority] || '未知'
}

// 获取严重程度文本
const getSeverityText = (severity) => {
  const textMap = {
    'LOW': '轻微', 'MINOR': '轻微',
    'MEDIUM': '中度', 'MODERATE': '中度',
    'HIGH': '重度', 'SEVERE': '重度', 'CRITICAL': '严重'
  }
  return textMap[severity] || '未知'
}

// 获取影响描述
const getImpactDescription = (severity, partName) => {
  const descriptions = {
    'high': `${partName}损伤严重，影响行车安全，建议立即处理`,
    'medium': `${partName}有明显损伤，影响车辆性能，建议尽快处理`,
    'low': `${partName}轻微损伤，不影响使用，可择期修复`
  }
  return descriptions[getPriority(severity)] || `${partName}需要检查维修`
}

// 获取维修建议
const getRepairRecommendation = (damageType, severity) => {
  const recommendations = {
    '车漆损伤': {
      'high': '钣金修复 + 全车喷漆',
      'medium': '局部喷漆修复',
      'low': '抛光处理'
    },
    '玻璃损伤': {
      'high': '更换玻璃总成',
      'medium': '玻璃修复',
      'low': '抛光处理'
    },
    '钣金损伤': {
      'high': '钣金更换 + 喷漆',
      'medium': '钣金修复 + 喷漆',
      'low': '钣金修复'
    },
    '划痕': {
      'high': '深度划痕修复 + 喷漆',
      'medium': '划痕修复 + 喷漆',
      'low': '抛光处理'
    },
    '凹陷': {
      'high': '钣金更换 + 喷漆',
      'medium': '钣金修复 + 喷漆',
      'low': '凹陷修复'
    },
    '裂纹': {
      'high': '部件更换',
      'medium': '裂纹修复',
      'low': '胶水修复'
    },
    '破损': {
      'high': '部件更换',
      'medium': '部件更换',
      'low': '部件修复'
    }
  }
  
  const priority = getPriority(severity)
  return recommendations[damageType]?.[priority] || '需要专业检查'
}

// 获取维修时间
const getRepairTime = (damageType, severity) => {
  const timeMap = {
    '车漆损伤': { 'high': '4小时', 'medium': '2小时', 'low': '30分钟' },
    '玻璃损伤': { 'high': '2小时', 'medium': '1小时', 'low': '30分钟' },
    '钣金损伤': { 'high': '6小时', 'medium': '4小时', 'low': '2小时' },
    '划痕': { 'high': '3小时', 'medium': '2小时', 'low': '30分钟' },
    '凹陷': { 'high': '5小时', 'medium': '3小时', 'low': '2小时' },
    '裂纹': { 'high': '3小时', 'medium': '2小时', 'low': '1小时' },
    '破损': { 'high': '4小时', 'medium': '3小时', 'low': '2小时' }
  }
  
  const priority = getPriority(severity)
  return timeMap[damageType]?.[priority] || '2小时'
}

// 获取维修费用
const getRepairCost = (damageType, severity) => {
  const costMap = {
    '车漆损伤': { 'high': 2500, 'medium': 1200, 'low': 300 },
    '玻璃损伤': { 'high': 1800, 'medium': 800, 'low': 200 },
    '钣金损伤': { 'high': 3500, 'medium': 2000, 'low': 800 },
    '划痕': { 'high': 1500, 'medium': 800, 'low': 200 },
    '凹陷': { 'high': 3000, 'medium': 1500, 'low': 600 },
    '裂纹': { 'high': 2000, 'medium': 1000, 'low': 400 },
    '破损': { 'high': 2500, 'medium': 1500, 'low': 600 }
  }
  
  const priority = getPriority(severity)
  return costMap[damageType]?.[priority] || 1000
}

// 获取车辆信息
const vehicleInfo = computed(() => {
  const result = detectionStore.detectionResult
  const analysis = detectionStore.llmAnalysis?.analysis
  
  if (analysis?.vehicle_info) {
    return {
      brand: analysis.vehicle_info.brand || '未知品牌',
      model: analysis.vehicle_info.model || '未知车型'
    }
  }
  
  return {
    brand: result?.brand || detectionStore.carBrand || '未知品牌',
    model: '未知车型'
  }
})

// 总预算
const totalBudget = computed(() => {
  return damageList.value.reduce((sum, item) => sum + item.cost, 0)
})

// 总时间
const totalTime = computed(() => {
  const totalMinutes = damageList.value.reduce((sum, item) => {
    const timeStr = item.time
    const match = timeStr.match(/(\d+)小时/)
    const hours = match ? parseInt(match[1]) : 0
    const minuteMatch = timeStr.match(/(\d+)分钟/)
    const minutes = minuteMatch ? parseInt(minuteMatch[1]) : 0
    return sum + hours * 60 + minutes
  }, 0)
  
  if (totalMinutes < 60) {
    return `${totalMinutes}分钟`
  } else {
    const hours = Math.floor(totalMinutes / 60)
    const remainingMinutes = totalMinutes % 60
    return remainingMinutes > 0 ? `${hours}小时${remainingMinutes}分钟` : `${hours}小时`
  }
})

// 获取严重程度CSS类
const getSeverityClass = (level) => {
  const levelStr = String(level).toLowerCase()
  if (levelStr.includes('轻微') || levelStr.includes('轻') || levelStr.includes('low')) return 'light'
  if (levelStr.includes('中等') || levelStr.includes('中') || levelStr.includes('medium')) return 'medium'
  if (levelStr.includes('严重') || levelStr.includes('重') || levelStr.includes('severe') || levelStr.includes('high')) return 'severe';
  return 'medium';
}

// 页面加载时检查数据
onMounted(() => {
  if (!detectionStore.detectionResult && !taskId) {
    router.push('/detection')
  }
})

</script>

<style scoped>
/* ===== 专业预修车分析页面样式 ===== */
.pre-repair-analysis {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.main-content {
  padding: 64px 20px 40px;
  max-width: 900px;
  margin: 0 auto;
}

/* ===== 顶部车辆信息 ===== */
.vehicle-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.vehicle-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  font-size: 14px;
  color: #4a5568;
  font-weight: 500;
}

.info-value {
  font-size: 14px;
  color: #1a202c;
  font-weight: 600;
}

.brand-display {
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 14px;
}

.car-icon {
  width: 20px;
  height: 20px;
}

.detection-time {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #4a5568;
  font-size: 14px;
  font-weight: 500;
}

.time-icon {
  width: 16px;
  height: 16px;
  color: #667eea;
}

/* ===== 优先级排序列表 ===== */
.priority-section {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #1a202c;
  margin: 0;
}

.priority-legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #4a5568;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.legend-item.high .legend-dot {
  background: #e53e3e;
}

.legend-item.medium .legend-dot {
  background: #f59e0b;
}

.legend-item.low .legend-dot {
  background: #10b981;
}

/* ===== 优先级列表项 ===== */
.priority-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.priority-item {
  background: white;
  border-radius: 16px;
  padding: 0;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  overflow: hidden;
  transition: all 0.3s ease;
}

.priority-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
}

.high-priority {
  border-left: 4px solid #e53e3e;
}

.medium-priority {
  border-left: 4px solid #f59e0b;
}

.low-priority {
  border-left: 4px solid #10b981;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px 16px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.priority-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
}

.priority-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  color: white;
}

.high-priority .priority-number {
  background: linear-gradient(135deg, #e53e3e, #dc2626);
}

.medium-priority .priority-number {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.low-priority .priority-number {
  background: linear-gradient(135deg, #10b981, #059669);
}

.priority-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 12px;
}

.priority-badge.high {
  background: rgba(229, 62, 62, 0.1);
  color: #e53e3e;
}

.priority-badge.medium {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.priority-badge.low {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.damage-type-icon {
  width: 24px;
  height: 24px;
  color: #6b7280;
}

.damage-content {
  padding: 20px 24px;
}

.damage-location {
  font-size: 18px;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 12px;
}

.damage-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.damage-tag {
  background: #f3f4f6;
  color: #374151;
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
}

.severity-tag {
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
}

.severity-tag.light {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.severity-tag.medium {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.severity-tag.severe {
  background: rgba(229, 62, 62, 0.1);
  color: #e53e3e;
}

.impact-analysis, .repair-suggestion {
  margin-bottom: 16px;
}

.impact-header, .suggestion-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.warning-icon, .info-icon, .check-icon {
  font-size: 16px;
}

.impact-title, .suggestion-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.impact-text, .suggestion-text {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.6;
  margin: 0;
  padding-left: 24px;
}

.tool-icon {
  width: 16px;
  height: 16px;
  color: #667eea;
}

/* ===== 响应式设计 ===== */
@media (max-width: 768px) {
  .main-content {
    padding: 60px 16px 24px;
  }
  
  .vehicle-header {
    padding: 20px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .priority-legend {
    flex-wrap: wrap;
  }
  
  .item-header {
    padding: 16px 20px 12px;
  }
  
  .damage-content {
    padding: 16px 20px;
  }
  
  .damage-location {
    font-size: 16px;
  }
}

@media (max-width: 375px) {
  .main-content {
    padding: 56px 12px 20px;
  }
  
  .vehicle-header, .priority-section {
    padding: 16px;
    border-radius: 16px;
  }
  
  .section-title {
    font-size: 18px;
  }
  
  .damage-location {
    font-size: 16px;
  }
  
  .priority-number {
    width: 28px;
    height: 28px;
    font-size: 12px;
  }
}

/* 预修车分析样式 */
.priority-group {
  margin-bottom: 24px;
}

.priority-group:last-child {
  margin-bottom: 0;
}

.priority-group-title {
  font-size: 18px;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.priority-group-title::before {
  content: '';
  width: 4px;
  height: 4px;
  border-radius: 50%;
}

.priority-group.high::before {
  background: #e53e3e;
}

.priority-group.medium::before {
  background: #f59e0b;
}

.priority-group.low::before {
  background: #10b981;
}

.priority-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.priority-item {
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  border-left: 3px solid #e2e8f0;
}

.priority-item.high {
  border-left-color: #e53e3e;
}

.priority-item.medium {
  border-left-color: #f59e0b;
}

.priority-item.low {
  border-left-color: #10b981;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.item-name {
  font-size: 16px;
  font-weight: 600;
  color: #1a202c;
}

.item-badge {
  font-size: 14px;
  color: #6b7280;
  background: #e2e8f0;
  padding: 4px 8px;
  border-radius: 4px;
}

.item-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.impact-item, .suggestion-item {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.impact-label, .suggestion-label {
  font-size: 14px;
  color: #4a5568;
  font-weight: 500;
  min-width: 80px;
}

.impact-text {
  font-size: 14px;
  color: #1a202c;
  line-height: 1.5;
  flex: 1;
}

.suggestion-text {
  font-size: 14px;
  color: #1a202c;
  line-height: 1.5;
  flex: 1;
  color: #1a202c;
  line-height: 1.5;
  flex: 1;
}

</style>