<template>
  <div class="wechat-pre-repair-analysis">
    <WechatNavBar title="预修车分析" :showHome="true" />
    
    <div class="main-content">
      <!-- 车辆信息 -->
      <div class="vehicle-info">
        <div class="info-row">
          <span class="info-label">车型</span>
          <span class="info-value">丰田 卡罗拉 2022款</span>
        </div>
        <div class="info-row">
          <span class="info-label">检测时间</span>
          <span class="info-value">2026-03-02 14:30</span>
        </div>
      </div>
      
      <!-- 损伤列表 -->
      <div class="damage-list">
        <div 
          v-for="(item, index) in damageList" 
          :key="index"
          class="damage-item"
          :class="`priority-${item.priority}`"
        >
          <div class="damage-header">
            <el-tag :type="getPriorityType(item.priority)" size="small">{{ item.priorityText }}</el-tag>
            <span class="damage-location">{{ item.location }}</span>
          </div>
          <div class="damage-info">
            <el-tag size="small" :type="getDamageType(item.type)">{{ item.type }}</el-tag>
            <span class="damage-level">{{ item.level }}</span>
          </div>
          <p class="damage-desc">{{ item.impact }}</p>
          <div class="damage-footer">
            <span class="repair-method">{{ item.recommendation }}</span>
            <span class="repair-time">{{ item.time }}</span>
          </div>
        </div>
      </div>
      
      <!-- 总预算 -->
      <div class="budget-summary">
        <div class="budget-row">
          <span>预计总费用</span>
          <span class="budget-amount">¥{{ totalBudget }}</span>
        </div>
        <div class="budget-row">
          <span>预计总时长</span>
          <span class="budget-time">{{ totalTime }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import WechatNavBar from '../components/common/WechatNavBar.vue'

const damageList = ref([
  {
    priority: 'high',
    priorityText: '高优先级',
    location: '前保险杠',
    type: '钣金损伤',
    level: '重度',
    impact: '变形严重，影响安全，建议优先处理',
    recommendation: '钣金修复 + 喷漆',
    time: '4小时',
    cost: 2500
  },
  {
    priority: 'medium',
    priorityText: '中优先级',
    location: '左侧车门',
    type: '车漆损伤',
    level: '中度',
    impact: '明显划痕，影响美观，需要喷漆',
    recommendation: '喷漆修复',
    time: '2小时',
    cost: 800
  },
  {
    priority: 'low',
    priorityText: '低优先级',
    location: '右侧后视镜',
    type: '轻微损伤',
    level: '轻微',
    impact: '轻微划痕，不影响使用，可择期修复',
    recommendation: '抛光处理',
    time: '30分钟',
    cost: 200
  }
])

const totalBudget = computed(() => {
  return damageList.value.reduce((sum, item) => sum + item.cost, 0)
})

const totalTime = computed(() => {
  const totalMinutes = damageList.value.reduce((sum, item) => {
    const hours = parseInt(item.time)
    const minutes = item.time.includes('分钟') ? parseInt(item.time) : 0
    return sum + (hours * 60) + minutes
  }, 0)
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  return minutes > 0 ? `${hours}小时${minutes}分钟` : `${hours}小时`
})

const getPriorityType = (priority) => {
  const map = { high: 'danger', medium: 'warning', low: 'success' }
  return map[priority] || 'info'
}

const getDamageType = (type) => {
  const map = { '钣金损伤': 'warning', '车漆损伤': 'success', '轻微损伤': 'info' }
  return map[type] || 'info'
}
</script>

<style scoped>
.wechat-pre-repair-analysis {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.main-content {
  padding: 64px 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.vehicle-info {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
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
  color: #909399;
}

.info-value {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.damage-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.damage-item {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  border-left: 4px solid #4096ee;
}

.damage-item.priority-high {
  border-left-color: #F56C6C;
}

.damage-item.priority-medium {
  border-left-color: #E6A23C;
}

.damage-item.priority-low {
  border-left-color: #67C23A;
}

.damage-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.damage-location {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.damage-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.damage-level {
  font-size: 13px;
  color: #606266;
}

.damage-desc {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
  margin: 0 0 12px 0;
}

.damage-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.repair-method {
  font-size: 13px;
  color: #4096ee;
  font-weight: 500;
}

.repair-time {
  font-size: 13px;
  color: #909399;
}

.budget-summary {
  background: #fff;
  border-radius: 12px;
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.budget-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 15px;
  color: #606266;
}

.budget-amount {
  font-size: 20px;
  font-weight: 700;
  color: #F56C6C;
}

.budget-time {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

@media (max-width: 375px) {
  .main-content {
    padding: 60px 12px 20px;
  }
  
  .damage-location {
    font-size: 15px;
  }
  
  .damage-desc {
    font-size: 13px;
  }
}
</style>