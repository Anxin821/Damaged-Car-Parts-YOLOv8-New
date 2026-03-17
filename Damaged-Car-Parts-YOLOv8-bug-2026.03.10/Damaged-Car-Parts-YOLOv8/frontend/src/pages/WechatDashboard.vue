<template>
  <div class="wechat-dashboard">
    <WechatNavBar title="定损看板" :showHome="true" />
    
    <div class="main-content">
      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon total">{{ stats.total }}</div>
          <div class="stat-label">总定损数</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon pending">{{ stats.pending }}</div>
          <div class="stat-label">待处理</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon completed">{{ stats.completed }}</div>
          <div class="stat-label">已完成</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon budget">¥{{ stats.budget }}</div>
          <div class="stat-label">累计预算</div>
        </div>
      </div>
      
      <!-- 定损记录列表 -->
      <div class="records-section">
        <div class="section-header">
          <h3 class="section-title">定损记录</h3>
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
                <span class="record-location">{{ record.location }}</span>
                <span class="record-damage-count" v-if="record.damageCount > 0">{{ record.damageCount }}处损伤</span>
                <span class="record-time">{{ record.time }}</span>
              </div>
            </div>
            <div class="record-right">
              <span class="record-amount">¥{{ record.amount }}</span>
              <el-tag :type="getStatusTagType(record.statusClass)" size="small">
                {{ record.status }}
              </el-tag>
            </div>
          </div>
        </div>
        
        <el-empty v-else description="暂无定损记录">
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

// 从 detectionStore 获取真实检测数据
const records = computed(() => {
  const result = detectionStore.detectionResult
  if (!result || !result.taskId) return []
  
  const regions = result.regions || []
  
  const partMap = {
    'damaged door': '车门', 'damaged window': '车窗', 'damaged headlight': '前大灯',
    'damaged mirror': '后视镜', 'dent': '凹陷', 'damaged hood': '引擎盖',
    'damaged bumper': '保险杠', 'damaged wind shield': '挡风玻璃'
  }
  
  // 计算总费用和最高严重程度
  const totalAmount = regions.reduce((sum, region) => {
    const severity = region.severity_level || 'MEDIUM'
    return sum + calculateAmount(region.damage_type, severity)
  }, 0)
  
  // 获取最高严重程度
  const severityLevels = ['LOW', 'MINOR', 'MEDIUM', 'MODERATE', 'HIGH', 'SEVERE', 'CRITICAL']
  const highestSeverity = regions.reduce((highest, region) => {
    const current = region.severity_level || 'MEDIUM'
    const currentIndex = severityLevels.indexOf(current)
    const highestIndex = severityLevels.indexOf(highest)
    return currentIndex > highestIndex ? current : highest
  }, 'LOW')
  
  const statusMap = {
    'LOW': '已完成', 'MINOR': '已完成',
    'MEDIUM': '待处理', 'MODERATE': '待处理',
    'HIGH': '待处理', 'SEVERE': '待处理', 'CRITICAL': '待处理'
  }
  
  const status = statusMap[highestSeverity] || '待处理'
  
  // 汇总所有损伤部位
  const damageParts = regions.map(region => 
    partMap[region.part_code] || region.part_code || '未知部位'
  ).join('、')
  
  // 返回一个完整的定损报告记录
  return [{
    id: result.taskId.slice(-8),
    time: new Date().toLocaleString('zh-CN', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' }),
    location: damageParts || '未检测到损伤',
    amount: totalAmount,
    damageCount: regions.length,
    status,
    statusClass: status === '已完成' ? 'status-completed' : 'status-pending',
    taskId: result.taskId, // 保存完整的taskId用于跳转
    vehicleBrand: getVehicleBrand(result) // 获取车辆品牌
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

const calculateAmount = (damageType, severity) => {
  const baseAmount = {
    'PAINT': 500, 'PAINT_DAMAGE': 500, 'GLASS': 800, 'GLASS_DAMAGE': 800,
    'METAL': 1000, 'METAL_DAMAGE': 1000, 'SCRATCH': 500, 'DENT': 1000,
    'CRACK': 800, 'BROKEN': 800
  }
  const severityMultiplier = {
    'LOW': 1, 'MINOR': 1, 'MEDIUM': 1.5, 'MODERATE': 1.5,
    'HIGH': 2, 'SEVERE': 2, 'CRITICAL': 3
  }
  const base = baseAmount[damageType] || 500
  const multiplier = severityMultiplier[severity] || 1
  return Math.round(base * multiplier)
}

const stats = computed(() => {
  const list = records.value
  return {
    total: list.length,
    pending: list.filter(r => r.status === '待处理').length,
    completed: list.filter(r => r.status === '已完成').length,
    budget: list.reduce((sum, r) => sum + r.amount, 0)
  }
})

const getStatusTagType = (statusClass) => {
  return statusClass === 'status-completed' ? 'success' : 'warning'
}

const viewRecord = (record) => {
  router.push(`/damage-detail/${record.taskId}`)
}
</script>

<style scoped>
.wechat-dashboard {
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
.stat-icon.pending { color: #E6A23C; }
.stat-icon.completed { color: #67C23A; }
.stat-icon.budget { color: #F56C6C; font-size: 16px; }

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

.record-damage-count {
  background: #f56c6c;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
}

.record-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.record-amount {
  font-size: 16px;
  font-weight: 700;
  color: #F56C6C;
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