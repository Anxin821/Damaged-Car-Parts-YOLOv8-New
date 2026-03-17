<template>
  <div class="wechat-repair-dashboard">
    <WechatNavBar title="预修车分析看板" :showHome="true" />
    
    <div class="main-content">
      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon total">{{ stats.total }}</div>
          <div class="stat-label">总分析数</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon high">{{ stats.highPriority }}</div>
          <div class="stat-label">高优先级</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon medium">{{ stats.mediumPriority }}</div>
          <div class="stat-label">中优先级</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon budget">¥{{ stats.totalBudget }}</div>
          <div class="stat-label">预计总费用</div>
        </div>
      </div>
      
      <!-- 预修车分析记录列表 -->
      <div class="records-section">
        <div class="section-header">
          <h3 class="section-title">分析记录</h3>
          <span class="record-count">共 {{ records.length }} 条</span>
        </div>
        
        <div v-if="records.length > 0" class="record-list">
          <div 
            v-for="record in records" 
            :key="record.id" 
            class="record-item"
            @click="viewRecord(record)"
          >
            <div class="record-main">
              <div class="record-id">{{ record.vehicleBrand }}</div>
              <div class="record-info">
                <span class="record-location">{{ record.damageSummary }}</span>
                <span class="record-priority" :class="`priority-${record.highestPriority}`">
                  {{ getPriorityText(record.highestPriority) }}
                </span>
                <span class="record-time">{{ record.time }}</span>
              </div>
            </div>
            <div class="record-right">
              <span class="record-amount">¥{{ record.totalBudget }}</span>
              <span class="record-duration">{{ record.totalTime }}</span>
            </div>
          </div>
        </div>
        
        <el-empty v-else description="暂无预修车分析记录">
          <el-button type="primary" @click="$router.push('/detection')">
            开始AI定损
          </el-button>
        </el-empty>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useDetectionStore } from '../store/detection'
import WechatNavBar from '../components/common/WechatNavBar.vue'

const router = useRouter()
const detectionStore = useDetectionStore()

// 模拟预修车分析记录数据（实际应该从API获取）
const records = computed(() => {
  const result = detectionStore.detectionResult
  if (!result || !result.taskId) return []
  
  const regions = result.regions || []
  
  const partMap = {
    'damaged door': '车门', 'damaged window': '车窗', 'damaged headlight': '前大灯',
    'damaged mirror': '后视镜', 'dent': '凹陷', 'damaged hood': '引擎盖',
    'damaged bumper': '保险杠', 'damaged wind shield': '挡风玻璃'
  }
  
  // 计算优先级分布
  const priorityCount = {
    high: 0,
    medium: 0,
    low: 0
  }
  
  // 模拟优先级分配（基于损伤严重程度）
  regions.forEach(region => {
    const severity = region.severity_level || 'MEDIUM'
    if (severity === 'HIGH' || severity === 'SEVERE' || severity === 'CRITICAL') {
      priorityCount.high++
    } else if (severity === 'MEDIUM' || severity === 'MODERATE') {
      priorityCount.medium++
    } else {
      priorityCount.low++
    }
  })
  
  // 计算总预算和时间
  const totalBudget = regions.reduce((sum, region) => {
    const severity = region.severity_level || 'MEDIUM'
    return sum + calculateBudget(region.damage_type, severity)
  }, 0)
  
  const totalTime = regions.reduce((sum, region) => {
    const severity = region.severity_level || 'MEDIUM'
    return sum + calculateTime(region.damage_type, severity)
  }, 0)
  
  // 获取最高优先级
  const highestPriority = priorityCount.high > 0 ? 'high' : 
                         priorityCount.medium > 0 ? 'medium' : 'low'
  
  // 汇总损伤部位
  const damageParts = regions.map(region => 
    partMap[region.part_code] || region.part_code || '未知部位'
  ).join('、')
  
  // 获取车辆品牌
  const vehicleBrand = getVehicleBrand(result)
  
  // 返回一个完整的预修车分析记录
  return [{
    id: result.taskId.slice(-8),
    vehicleBrand: vehicleBrand,
    damageSummary: damageParts || '未检测到损伤',
    damageCount: regions.length,
    highestPriority: highestPriority,
    priorityCount: priorityCount,
    totalBudget: totalBudget,
    totalTime: formatTotalTime(totalTime),
    time: new Date().toLocaleString('zh-CN', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' }),
    taskId: result.taskId // 保存完整的taskId用于跳转
  }]
})

// 获取车辆品牌的辅助函数
const getVehicleBrand = (result) => {
  // 优先从豆包分析结果获取
  const analysis = detectionStore.llmAnalysis?.analysis
  if (analysis?.vehicle_info?.brand) {
    return analysis.vehicle_info.brand
  }
  // 其次从YOLO检测结果获取
  if (result?.brand) {
    return result.brand
  }
  // 最后从detectionStore获取
  if (detectionStore.carBrand) {
    return detectionStore.carBrand
  }
  return '未知品牌'
}

// 计算维修预算
const calculateBudget = (damageType, severity) => {
  const baseBudget = {
    'PAINT': 800, 'PAINT_DAMAGE': 800, 'GLASS': 1200, 'GLASS_DAMAGE': 1200,
    'METAL': 2500, 'METAL_DAMAGE': 2500, 'SCRATCH': 500, 'DENT': 2000,
    'CRACK': 1500, 'BROKEN': 1800
  }
  const severityMultiplier = {
    'LOW': 0.5, 'MINOR': 0.5, 'MEDIUM': 1, 'MODERATE': 1,
    'HIGH': 1.5, 'SEVERE': 1.5, 'CRITICAL': 2
  }
  const base = baseBudget[damageType] || 1000
  const multiplier = severityMultiplier[severity] || 1
  return Math.round(base * multiplier)
}

// 计算维修时间（分钟）
const calculateTime = (damageType, severity) => {
  const baseTime = {
    'PAINT': 120, 'PAINT_DAMAGE': 120, 'GLASS': 60, 'GLASS_DAMAGE': 60,
    'METAL': 240, 'METAL_DAMAGE': 240, 'SCRATCH': 30, 'DENT': 180,
    'CRACK': 90, 'BROKEN': 120
  }
  const severityMultiplier = {
    'LOW': 0.5, 'MINOR': 0.5, 'MEDIUM': 1, 'MODERATE': 1,
    'HIGH': 1.5, 'SEVERE': 1.5, 'CRITICAL': 2
  }
  const base = baseTime[damageType] || 120
  const multiplier = severityMultiplier[severity] || 1
  return Math.round(base * multiplier)
}

// 格式化总时间
const formatTotalTime = (minutes) => {
  if (minutes < 60) {
    return `${minutes}分钟`
  } else {
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = minutes % 60
    return remainingMinutes > 0 ? `${hours}小时${remainingMinutes}分钟` : `${hours}小时`
  }
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

// 统计数据
const stats = computed(() => {
  const list = records.value
  return {
    total: list.length,
    highPriority: list.reduce((sum, r) => sum + r.priorityCount.high, 0),
    mediumPriority: list.reduce((sum, r) => sum + r.priorityCount.medium, 0),
    totalBudget: list.reduce((sum, r) => sum + r.totalBudget, 0)
  }
})

// 查看记录详情
const viewRecord = (record) => {
  router.push({
    path: '/pre-repair',
    query: { 
      taskId: record.taskId,
      from: 'dashboard'
    }
  })
}
</script>

<style scoped>
.wechat-repair-dashboard {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.main-content {
  padding: 64px 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px 8px;
  text-align: center;
}

.stat-icon {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 8px;
}

.stat-icon.total { color: #4096EE; }
.stat-icon.high { color: #F56C6C; }
.stat-icon.medium { color: #E6A23C; }
.stat-icon.budget { color: #67C23A; font-size: 16px; }

.stat-label {
  font-size: 12px;
  color: #909399;
}

/* 记录列表 */
.records-section {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.record-count {
  font-size: 13px;
  color: #909399;
}

.record-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.record-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.record-item:hover {
  background: #e6f7ff;
}

.record-main {
  flex: 1;
}

.record-id {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.record-info {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 13px;
  color: #909399;
}

.record-location {
  color: #606266;
  font-weight: 500;
}

.record-priority {
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
  color: white;
}

.record-priority.priority-high {
  background: #f56c6c;
}

.record-priority.priority-medium {
  background: #e6a23c;
}

.record-priority.priority-low {
  background: #67c23a;
}

.record-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.record-amount {
  font-size: 16px;
  font-weight: 700;
  color: #F56C6C;
}

.record-duration {
  font-size: 12px;
  color: #909399;
}

@media (max-width: 375px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .main-content {
    padding: 60px 12px 20px;
  }
}
</style>
