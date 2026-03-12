<template>
  <div class="wechat-dashboard">
    <!-- 导航栏 -->
    <WechatNavBar title="定损看板" :showHome="true" />
    
    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 统计卡片区域 -->
      <div class="stats-section">
        <el-row :gutter="12" class="stats-grid">
          <!-- 总定损数 -->
          <el-col :span="12">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-content">
                <div class="stat-icon total-icon">
                  <el-icon><Grid /></el-icon>
                </div>
                <div class="stat-value">{{ stats.total }}</div>
                <div class="stat-label">总定损数</div>
              </div>
            </el-card>
          </el-col>
          
          <!-- 待处理数 -->
          <el-col :span="12">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-content">
                <div class="stat-icon pending-icon">
                  <el-icon><Clock /></el-icon>
                </div>
                <div class="stat-value">{{ stats.pending }}</div>
                <div class="stat-label">待处理数</div>
              </div>
            </el-card>
          </el-col>
          
          <!-- 已完成数 -->
          <el-col :span="12">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-content">
                <div class="stat-icon completed-icon">
                  <el-icon><CircleCheck /></el-icon>
                </div>
                <div class="stat-value">{{ stats.completed }}</div>
                <div class="stat-label">已完成数</div>
              </div>
            </el-card>
          </el-col>
          
          <!-- 累计预算 -->
          <el-col :span="12">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-content">
                <div class="stat-icon budget-icon">
                  <el-icon><Money /></el-icon>
                </div>
                <div class="stat-value">¥{{ stats.budget }}</div>
                <div class="stat-label">累计预算</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <!-- 定损记录列表 -->
      <div class="records-section">
        <el-row justify="space-between" align="middle" class="section-header">
          <el-col :span="8">
            <h3 class="section-title">定损记录</h3>
          </el-col>
          <el-col :span="16" class="text-right">
            <el-button type="primary" link @click="openFilter">
              筛选
              <el-icon class="ml-1"><ArrowDown /></el-icon>
            </el-button>
          </el-col>
        </el-row>
        
        <!-- 记录列表 -->
        <div v-if="records.length > 0">
          <el-card 
            v-for="record in records" 
            :key="record.id" 
            class="record-card" 
            shadow="hover"
          >
            <el-row :gutter="12">
              <el-col :span="8">
                <div class="record-image">
                  <el-image 
                    :src="record.image" 
                    alt="定损照片" 
                    class="record-img"
                    fit="cover"
                  />
                  <!-- 模拟YOLO标注框 -->
                  <div class="detection-box" :style="record.boxStyle"></div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="record-info">
                  <el-row justify="space-between" align="middle" class="record-header">
                    <el-col>
                      <div class="record-id">编号: {{ record.id }}</div>
                    </el-col>
                    <el-col>
                      <el-tag 
                        :type="getStatusTagType(record.statusClass)"
                        size="small"
                        effect="dark"
                      >
                        {{ record.status }}
                      </el-tag>
                    </el-col>
                  </el-row>
                  <el-space direction="vertical" :size="4" class="record-details">
                    <el-row>
                      <el-col :span="10" class="detail-label">检测时间:</el-col>
                      <el-col :span="14" class="detail-value">{{ record.time }}</el-col>
                    </el-row>
                    <el-row>
                      <el-col :span="10" class="detail-label">破损部位:</el-col>
                      <el-col :span="14" class="detail-value">{{ record.location }}</el-col>
                    </el-row>
                    <el-row>
                      <el-col :span="10" class="detail-label">定损金额:</el-col>
                      <el-col :span="14" class="detail-value amount">¥{{ record.amount }}</el-col>
                    </el-row>
                  </el-space>
                </div>
              </el-col>
              <el-col :span="4">
                <div class="record-action" @click="viewRecord(record.id)">
                  <el-link type="primary" :underline="false">
                    查看详情
                    <el-icon class="ml-1"><ArrowRight /></el-icon>
                  </el-link>
                </div>
              </el-col>
            </el-row>
          </el-card>
        </div>
        
        <!-- 空状态 -->
        <el-empty v-else description="暂无定损记录">
          <template #image>
            <div class="empty-illustration">
              <svg width="120" height="120" viewBox="0 0 200 200" fill="none">
                <!-- 车辆轮廓 -->
                <rect x="40" y="100" width="120" height="30" rx="5" fill="#E4E7ED"/>
                <circle cx="60" cy="130" r="10" fill="#E4E7ED"/>
                <circle cx="140" cy="130" r="10" fill="#E4E7ED"/>
                <rect x="50" y="90" width="100" height="10" rx="2" fill="#E4E7ED"/>
                <polygon points="40,100 50,90 150,90 160,100" fill="#E4E7ED"/>
                
                <!-- 文档图标 -->
                <rect x="80" y="60" width="40" height="40" rx="2" fill="#E4E7ED"/>
                <line x1="90" y1="70" x2="110" y2="70" stroke="#C0C4CC" stroke-width="2"/>
                <line x1="90" y1="80" x2="110" y2="80" stroke="#C0C4CC" stroke-width="2"/>
                <line x1="90" y1="90" x2="100" y2="90" stroke="#C0C4CC" stroke-width="2"/>
              </svg>
            </div>
          </template>
          <el-button type="primary" @click="$router.push('/detection')">
            点击AI定损开始检测
          </el-button>
        </el-empty>
      </div>
    </div>
    
    <!-- 筛选弹窗 -->
    <el-dialog 
      v-model="showFilterModal" 
      title="筛选条件" 
      direction="btt" 
      :show-close="false"
      class="filter-dialog"
      width="90%"
    >
      <template #header="{ close }">
        <div class="modal-header">
          <div class="modal-title">筛选条件</div>
          <el-button @click="close" :icon="Close" circle />
        </div>
      </template>
      
      <div class="modal-body">
        <div class="filter-section">
          <div class="filter-label">状态</div>
          <el-radio-group v-model="filters.status" class="filter-options">
            <el-radio-button value="all">全部</el-radio-button>
            <el-radio-button value="pending">待处理</el-radio-button>
            <el-radio-button value="completed">已完成</el-radio-button>
          </el-radio-group>
        </div>
        <div class="filter-section">
          <div class="filter-label">时间范围</div>
          <el-radio-group v-model="filters.timeRange" class="filter-options">
            <el-radio-button value="all">全部</el-radio-button>
            <el-radio-button value="today">今天</el-radio-button>
            <el-radio-button value="week">本周</el-radio-button>
            <el-radio-button value="month">本月</el-radio-button>
          </el-radio-group>
        </div>
      </div>
      
      <template #footer>
        <div class="modal-footer">
          <el-button @click="resetFilters">重置</el-button>
          <el-button type="primary" @click="applyFilters">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useDetectionStore } from '../store/detection'
import WechatNavBar from '../components/common/WechatNavBar.vue'
import { 
  Grid, 
  Clock, 
  CircleCheck, 
  Money,
  ArrowDown,
  ArrowRight,
  Close
} from '@element-plus/icons-vue'

const router = useRouter()
const detectionStore = useDetectionStore()
const showFilterModal = ref(false)

// 从 detectionStore 获取真实检测数据
const records = computed(() => {
  const result = detectionStore.detectionResult
  if (!result || !result.taskId) return []
  
  // 将检测数据转换为看板记录格式
  const regions = result.regions || []
  const images = result.images || []
  
  // 按部位分组生成记录
  const records = []
  regions.forEach((region, index) => {
    const partMap = {
      'damaged door': '车门',
      'damaged window': '车窗',
      'damaged headlight': '前大灯',
      'damaged mirror': '后视镜',
      'dent': '凹陷',
      'damaged hood': '引擎盖',
      'damaged bumper': '保险杠',
      'damaged wind shield': '挡风玻璃'
    }
    
    const statusMap = {
      'LOW': '已完成',
      'MINOR': '已完成',
      'MEDIUM': '待处理',
      'MODERATE': '待处理',
      'HIGH': '待处理',
      'SEVERE': '待处理',
      'CRITICAL': '待处理'
    }
    
    const statusClassMap = {
      '已完成': 'status-completed',
      '待处理': 'status-pending'
    }
    
    const severity = region.severity_level || 'MEDIUM'
    const status = statusMap[severity] || '待处理'
    
    records.push({
      id: `${result.taskId.slice(-8)}-${index + 1}`,
      image: images[0]?.image_url || '',
      boxStyle: calculateBoxStyle(region.bbox),
      time: new Date().toLocaleString('zh-CN'),
      location: partMap[region.part_code] || region.part_code || '未知部位',
      amount: calculateAmount(region.damage_type, severity),
      status: status,
      statusClass: statusClassMap[status] || 'status-pending'
    })
  })
  
  return records
})

// 计算标注框样式
const calculateBoxStyle = (bbox) => {
  if (!bbox) return { top: '20%', left: '30%', width: '40%', height: '30%' }
  
  const coords = bbox.split(',').map(Number)
  if (coords.length !== 4) return { top: '20%', left: '30%', width: '40%', height: '30%' }
  
  const [x1, y1, x2, y2] = coords
  // 假设图片尺寸为 100x100，计算百分比
  return {
    top: `${Math.min(y1, y2) / 2}%`,
    left: `${Math.min(x1, x2) / 3}%`,
    width: `${Math.abs(x2 - x1) / 3}%`,
    height: `${Math.abs(y2 - y1) / 2}%`
  }
}

// 根据损伤类型和严重程度计算金额
const calculateAmount = (damageType, severity) => {
  const baseAmount = {
    'PAINT': 500,
    'PAINT_DAMAGE': 500,
    'GLASS': 800,
    'GLASS_DAMAGE': 800,
    'METAL': 1000,
    'METAL_DAMAGE': 1000,
    'SCRATCH': 500,
    'DENT': 1000,
    'CRACK': 800,
    'BROKEN': 800
  }
  
  const severityMultiplier = {
    'LOW': 1,
    'MINOR': 1,
    'MEDIUM': 1.5,
    'MODERATE': 1.5,
    'HIGH': 2,
    'SEVERE': 2,
    'CRITICAL': 3
  }
  
  const base = baseAmount[damageType] || 500
  const multiplier = severityMultiplier[severity] || 1
  return Math.round(base * multiplier)
}

// 统计数据
const stats = computed(() => {
  const recordsList = records.value
  const total = recordsList.length
  const pending = recordsList.filter(r => r.status === '待处理').length
  const completed = recordsList.filter(r => r.status === '已完成').length
  const budget = recordsList.reduce((sum, r) => sum + r.amount, 0)
  
  return {
    total,
    pending,
    completed,
    budget
  }
})

const filters = ref({
  status: 'all',
  timeRange: 'all'
})

const openFilter = () => {
  showFilterModal.value = true
}

const closeFilterModal = () => {
  showFilterModal.value = false
}

// 获取状态标签类型
const getStatusTagType = (statusClass) => {
  const typeMap = {
    'status-completed': 'success',
    'status-pending': 'warning'
  }
  return typeMap[statusClass] || 'info'
}

const resetFilters = () => {
  filters.value = {
    status: 'all',
    timeRange: 'all'
  }
}

const applyFilters = () => {
  // 模拟筛选功能
  console.log('应用筛选条件:', filters.value)
  showFilterModal.value = false
}

const viewRecord = (id) => {
  // 跳转到定损详情页
  if (detectionStore.detectionResult?.taskId) {
    router.push(`/damage-detail/${detectionStore.detectionResult.taskId}`)
  } else {
    router.push('/damage-detail')
  }
}
</script>

<style scoped>
  /* 整体布局 */
  .wechat-dashboard {
    min-height: 100vh;
    background-color: #f5f7fa;
    position: relative;
    overflow-x: hidden;
  }

  /* 主内容区 */
  .main-content {
    padding-top: 44px;
    min-height: calc(100vh - 44px);
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  /* 统计卡片区域 */
  .stats-section {
    margin-bottom: 10px;
    padding: 0 16px;
  }

  .stats-grid .el-col {
    margin-bottom: 12px;
  }

  .stat-card {
    border-radius: 12px;
  }

  .stat-card :deep(.el-card__body) {
    padding: 16px;
  }

  .stat-content {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .stat-icon {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 12px;
    color: white;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .total-icon {
    background: linear-gradient(135deg, #4096EE, #54C5F8);
  }

  .pending-icon {
    background: linear-gradient(135deg, #E6A23C, #F7BA7E);
  }

  .completed-icon {
    background: linear-gradient(135deg, #67C23A, #85CE61);
  }

  .budget-icon {
    background: linear-gradient(135deg, #66D3A8, #4096EE);
  }

  .stat-value {
    font-size: 20px;
    font-weight: 700;
    color: #303133;
    margin-bottom: 4px;
  }

  .stat-label {
    font-size: 12px;
    color: #909399;
  }

  /* 定损记录列表 */
  .records-section {
    flex: 1;
    padding: 0 16px;
  }

  .section-header {
    margin-bottom: 16px;
  }

  .section-title {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
    margin: 0;
  }

  .record-card {
    margin-bottom: 12px;
    border-radius: 12px;
  }

  .record-card :deep(.el-card__body) {
    padding: 16px;
  }

  /* 记录列表 - 使用Element Plus组件 */
  .record-image {
    width: 80px;
    height: 80px;
    border-radius: 8px;
    overflow: hidden;
    position: relative;
    background-color: #f0f2f5;
    flex-shrink: 0;
  }

  .record-img {
    width: 100%;
    height: 100%;
  }

  .record-img :deep(.el-image__inner) {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  /* YOLO标注框 */
  .detection-box {
    position: absolute;
    border: 2px solid #4096EE;
    border-radius: 4px;
    pointer-events: none;
  }

  .record-info {
    min-width: 0;
  }

  .record-header {
    margin-bottom: 8px;
  }

  .record-id {
    font-size: 14px;
    font-weight: 600;
    color: #303133;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .record-details {
    margin-top: 8px;
  }

  .detail-label {
    color: #909399;
    font-size: 13px;
  }

  .detail-value {
    color: #303133;
    font-size: 13px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .detail-value.amount {
    font-weight: 600;
    color: #F56C6C;
  }

  .record-action {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    height: 100%;
  }

  .ml-1 {
    margin-left: 4px;
  }

  .text-right {
    text-align: right;
  }

  /* 空状态 - 使用Element Plus Empty组件 */
  .empty-illustration {
    margin-bottom: 20px;
  }

  /* 筛选弹窗 - 使用Element Plus Dialog组件 */
  .filter-dialog :deep(.el-dialog) {
    margin: 0;
    border-radius: 16px 16px 0 0;
  }

  .filter-dialog :deep(.el-dialog__header) {
    padding: 0;
    margin: 0;
  }

  .filter-dialog :deep(.el-dialog__body) {
    padding: 0;
  }

  .filter-dialog :deep(.el-dialog__footer) {
    padding: 0;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid #f0f0f0;
  }

  .modal-title {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
  }

  .modal-body {
    padding: 0px;
  }

  .filter-section {
    margin-bottom: 24px;
  }

  .filter-label {
    font-size: 14px;
    font-weight: 500;
    color: #303133;
    margin-bottom: 12px;
  }

  .filter-options {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }

  .filter-options :deep(.el-radio-button__inner) {
    border-radius: 16px;
    padding: 6px 16px;
    font-size: 14px;
  }

  .modal-footer {
    display: flex;
    padding: 16px 20px;
    border-top: 1px solid #f0f0f0;
    gap: 12px;
  }

  /* 响应式设计 - 375*812 手机竖屏 */
  @media (width: 375px) and (height: 812px) {
    .main-content {
      height: calc(812px - 44px - 40px);
      overflow-y: auto;
    }
    
    .stats-section {
      padding: 0 16px;
    }
    
    .records-section {
      padding: 0 16px;
    }
    
    .stat-card :deep(.el-card__body) {
      padding: 14px;
    }
    
    .stat-icon {
      width: 40px;
      height: 40px;
    }
    
    .stat-icon .el-icon {
      font-size: 24px;
    }
    
    .stat-value {
      font-size: 18px;
    }
    
    .record-card :deep(.el-card__body) {
      padding: 14px;
    }
    
    .record-image {
      width: 70px;
      height: 70px;
    }
  }

  /* 通用响应式设计 */
  @media (max-width: 375px) {
    .main-content {
      padding: 16px 0;
      gap: 16px;
    }
    
    .stats-section {
      padding: 0 16px;
    }
    
    .records-section {
      padding: 0 16px;
    }
    
    .stat-card :deep(.el-card__body) {
      padding: 14px;
    }
    
    .stat-icon {
      width: 40px;
      height: 40px;
    }
    
    .stat-icon .el-icon {
      font-size: 24px;
    }
    
    .stat-value {
      font-size: 18px;
    }
    
    .stat-label {
      font-size: 11px;
    }
    
    .section-title {
      font-size: 16px;
    }
    
    .record-card :deep(.el-card__body) {
      padding: 14px;
    }
    
    .record-image {
      width: 70px;
      height: 70px;
    }
    
    .record-id {
      font-size: 13px;
    }
    
    .detail-label,
    .detail-value {
      font-size: 12px;
    }
    
    .empty-illustration svg {
      width: 100px;
      height: 100px;
    }
  }
</style>