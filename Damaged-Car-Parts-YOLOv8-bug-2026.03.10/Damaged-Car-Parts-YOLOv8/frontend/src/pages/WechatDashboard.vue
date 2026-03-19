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
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useDetectionStore } from '../store/detection'
import { historyApi } from '../api/history'
import WechatNavBar from '../components/common/WechatNavBar.vue'

const router = useRouter()
const detectionStore = useDetectionStore()

// 从数据库加载的历史记录
const historyRecords = ref([])
const loading = ref(false)

// 页面加载时从数据库获取历史记录
onMounted(async () => {
  loading.value = true
  console.log('[Dashboard] 开始加载历史记录...')
  try {
    const response = await historyApi.getHistory({ pageSize: 100 })
    console.log('[Dashboard] API响应:', response)
    console.log('[Dashboard] response.list:', response.list)
    if (response.list) {
      console.log('[Dashboard] 获取到记录数:', response.list.length)
      // 强制触发Vue响应式更新
      historyRecords.value = []
      await nextTick()
      historyRecords.value = response.list.map(item => ({
        id: item.taskId?.slice(-8) || item.id,
        time: new Date(item.createdAt || item.timestamp).toLocaleString('zh-CN', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' }),
        location: item.location || '车辆损伤检测',
        amount: item.amount || 0,
        damageCount: item.damageCount || item.regions?.length || 0,
        status: item.status === 'completed' ? '已完成' : '待处理',
        statusClass: item.status === 'completed' ? 'status-completed' : 'status-pending',
        taskId: item.taskId || item.id,
        vehicleBrand: item.brand || item.vehicleBrand || '未知品牌'
      }))
      console.log('[Dashboard] 映射后的记录:', historyRecords.value)
      // 再次强制刷新
      await nextTick()
    } else {
      console.warn('[Dashboard] API返回数据格式不正确:', response)
    }
  } catch (error) {
    console.error('[Dashboard] 获取历史记录失败:', error)
  } finally {
    loading.value = false
    console.log('[Dashboard] 最终records:', records.value)
  }
})

// 简化测试：直接返回历史记录
const records = computed(() => {
  console.log('[Dashboard] records计算属性执行, historyRecords长度:', historyRecords.value.length)
  console.log('[Dashboard] historyRecords内容:', historyRecords.value)
  return historyRecords.value
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