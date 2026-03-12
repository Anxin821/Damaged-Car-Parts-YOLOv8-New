<template>
  <div class="wechat-pre-repair-analysis">
    <!-- 导航栏 -->
    <WechatNavBar title="预修车分析" :showHome="true" />
    
    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 基础信息卡 -->
      <el-card class="info-card" shadow="hover">
        <el-row :gutter="16">
          <el-col :span="8">
            <div class="info-item">
              <div class="info-label">车型</div>
              <div class="info-value">丰田 卡罗拉 2022款</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="info-item">
              <div class="info-label">检测时间</div>
              <div class="info-value">2026-03-02 14:30</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="info-item">
              <div class="info-label">破损总数</div>
              <div class="info-value damage-count">3 处</div>
            </div>
          </el-col>
        </el-row>
      </el-card>
      
      <!-- 优先级分析区 -->
      <div class="priority-section">
        <h3 class="section-title">优先级分析</h3>
        
        <!-- 高优先级 -->
        <el-card class="priority-group high-priority" shadow="hover">
          <template #header>
            <div class="priority-header">
              <el-tag type="danger" effect="dark">高优先级</el-tag>
              <el-tag type="info" size="small">1 项</el-tag>
            </div>
          </template>
          <div class="priority-list">
            <div class="priority-item" @click="showDamageDetail('high')">
              <el-row :gutter="12" align="middle">
                <el-col :span="16">
                  <div class="damage-info">
                    <div class="damage-location">前保险杠</div>
                    <el-tag size="small" type="warning">钣金损伤</el-tag>
                    <el-tag size="small" type="danger">重度</el-tag>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="damage-arrow">
                    <el-icon><ArrowRight /></el-icon>
                  </div>
                </el-col>
              </el-row>
              <div class="damage-impact">
                <div class="impact-title">影响说明</div>
                <div class="impact-content">前保险杠变形严重，影响车辆美观和安全性，可能导致其他部件受损</div>
              </div>
            </div>
          </div>
        </el-card>
        
        <!-- 中优先级 -->
        <el-card class="priority-group medium-priority" shadow="hover">
          <template #header>
            <div class="priority-header">
              <el-tag type="warning" effect="dark">中优先级</el-tag>
              <el-tag type="info" size="small">1 项</el-tag>
            </div>
          </template>
          <div class="priority-list">
            <div class="priority-item" @click="showDamageDetail('medium')">
              <el-row :gutter="12" align="middle">
                <el-col :span="16">
                  <div class="damage-info">
                    <div class="damage-location">左侧车门</div>
                    <el-tag size="small" type="success">车漆损伤</el-tag>
                    <el-tag size="small" type="warning">中度</el-tag>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="damage-arrow">
                    <el-icon><ArrowRight /></el-icon>
                  </div>
                </el-col>
              </el-row>
              <div class="damage-impact">
                <div class="impact-title">影响说明</div>
                <div class="impact-content">左侧车门有明显划痕，影响车辆美观，需要重新喷漆</div>
              </div>
            </div>
          </div>
        </el-card>
        
        <!-- 低优先级 -->
        <el-card class="priority-group low-priority" shadow="hover">
          <template #header>
            <div class="priority-header">
              <el-tag type="success" effect="dark">低优先级</el-tag>
              <el-tag type="info" size="small">1 项</el-tag>
            </div>
          </template>
          <div class="priority-list">
            <div class="priority-item" @click="showDamageDetail('low')">
              <el-row :gutter="12" align="middle">
                <el-col :span="16">
                  <div class="damage-info">
                    <div class="damage-location">右侧后视镜</div>
                    <el-tag size="small" type="info">轻微损伤</el-tag>
                    <el-tag size="small" type="success">轻微</el-tag>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="damage-arrow">
                    <el-icon><ArrowRight /></el-icon>
                  </div>
                </el-col>
              </el-row>
              <div class="damage-impact">
                <div class="impact-title">影响说明</div>
                <div class="impact-content">右侧后视镜有轻微划痕，不影响使用，可择期修复</div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
      
      <!-- 维修方案推荐区 -->
      <div class="repair-plan-section">
        <h3 class="section-title">维修方案推荐</h3>
        <el-card class="plan-card" shadow="hover">
          <template #header>
            <div class="plan-header">
              <div class="plan-title">推荐维修顺序</div>
              <el-tag type="info" size="small">按优先级排序</el-tag>
            </div>
          </template>
          <div class="plan-list">
            <el-timeline>
              <el-timeline-item 
                v-for="(item, index) in repairPlan" 
                :key="index"
                :type="getTimelineType(index)"
                :icon="getTimelineIcon(index)"
              >
                <div class="plan-item">
                  <div class="plan-content">
                    <div class="plan-location">{{ item.location }}</div>
                    <el-tag size="small">{{ item.type }}</el-tag>
                    <div class="plan-time">预计时间：{{ item.time }}</div>
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-card>
      </div>
      
      <!-- 生成维修预算按钮 -->
      <el-button 
        type="primary" 
        size="large" 
        class="budget-button" 
        @click="generateBudget"
        block
      >
        生成维修预算
      </el-button>
    </div>
    
    <!-- 损伤详情弹窗 -->
    <el-dialog 
      v-model="showDetailModal" 
      :title="`${currentDamage.location} - ${currentDamage.type}`" 
      width="90%" 
      :show-close="false"
      class="detail-dialog"
    >
      <template #header="{ close }">
        <div class="modal-header">
          <div class="modal-title">{{ currentDamage.location }} - {{ currentDamage.type }}</div>
          <el-button @click="close" :icon="Close" circle size="small" />
        </div>
      </template>
      
      <div class="modal-body">
        <div class="damage-image-container">
          <el-image 
            :src="currentDamage.image" 
            alt="损伤照片" 
            class="damage-image"
            fit="contain"
          />
          <!-- 模拟YOLO标注框 -->
          <div class="detection-box" :class="currentDamage.boxClass" :style="currentDamage.boxStyle">
            <div class="box-label">{{ currentDamage.type }} ({{ currentDamage.level }})</div>
          </div>
        </div>
        
        <el-descriptions :column="1" border class="damage-details">
          <el-descriptions-item label="损伤部位">{{ currentDamage.location }}</el-descriptions-item>
          <el-descriptions-item label="损伤类型">{{ currentDamage.type }}</el-descriptions-item>
          <el-descriptions-item label="损伤等级">
            <el-tag :type="getDamageTagType(currentDamage.level)">{{ currentDamage.level }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="影响说明">
            <span class="impact-text">{{ currentDamage.impact }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="推荐处理">{{ currentDamage.recommendation }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import WechatNavBar from '../components/common/WechatNavBar.vue'
import { 
  ArrowRight, 
  Close,
  Tools,
  Clock,
  Check
} from '@element-plus/icons-vue'

const router = useRouter()
const showDetailModal = ref(false)
const currentDamage = ref({
  location: '',
  type: '',
  level: '',
  impact: '',
  recommendation: '',
  image: '',
  boxClass: '',
  boxStyle: {}
})

// 维修计划数据
const repairPlan = ref([
  {
    location: '前保险杠',
    type: '钣金修复 + 喷漆',
    time: '4 小时'
  },
  {
    location: '左侧车门',
    type: '喷漆修复',
    time: '2 小时'
  },
  {
    location: '右侧后视镜',
    type: '抛光处理',
    time: '30 分钟'
  }
])

// 损伤数据
const damageData = {
  high: {
    location: '前保险杠',
    type: '钣金损伤',
    level: '重度',
    impact: '前保险杠变形严重，影响车辆美观和安全性，可能导致其他部件受损',
    recommendation: '钣金修复 + 喷漆',
    image: 'https://placehold.co/300x200/e6f7ff/409eff?text=Front+Bumper',
    boxClass: 'high-damage',
    boxStyle: { top: '30%', left: '20%', width: '60%', height: '40%' }
  },
  medium: {
    location: '左侧车门',
    type: '车漆损伤',
    level: '中度',
    impact: '左侧车门有明显划痕，影响车辆美观，需要重新喷漆',
    recommendation: '喷漆修复',
    image: 'https://placehold.co/300x200/e6f7ff/409eff?text=Left+Door',
    boxClass: 'medium-damage',
    boxStyle: { top: '40%', left: '10%', width: '40%', height: '30%' }
  },
  low: {
    location: '右侧后视镜',
    type: '轻微损伤',
    level: '轻微',
    impact: '右侧后视镜有轻微划痕，不影响使用，可择期修复',
    recommendation: '抛光处理',
    image: 'https://placehold.co/300x200/e6f7ff/409eff?text=Right+Mirror',
    boxClass: 'low-damage',
    boxStyle: { top: '20%', left: '60%', width: '30%', height: '25%' }
  }
}

const showDamageDetail = (priority) => {
  currentDamage.value = { ...damageData[priority] }
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
}

const generateBudget = () => {
  alert('维修预算生成中...\n预计总费用：¥3,500\n预计总时间：6.5小时')
}

// 获取时间线类型
const getTimelineType = (index) => {
  const types = ['danger', 'warning', 'success']
  return types[index] || 'info'
}

// 获取时间线图标
const getTimelineIcon = (index) => {
  const icons = [Tools, Tools, Check]
  return icons[index] || Clock
}

// 获取损伤标签类型
const getDamageTagType = (level) => {
  const typeMap = {
    '重度': 'danger',
    '中度': 'warning',
    '轻微': 'success'
  }
  return typeMap[level] || 'info'
}
</script>

<style scoped>
.wechat-pre-repair-analysis {
  min-height: 100vh;
  background-color: #f5f7fa;
  position: relative;
  overflow-x: hidden;
}

/* 主内容区 */
.main-content {
  padding-top: 44px;
  min-height: calc(100vh - 44px);
  padding: 64px 16px 80px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 基础信息卡 */
.info-card {
  border-radius: 16px;
  transition: all 0.3s ease;
}

.info-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.info-item {
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.info-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
  font-weight: 500;
}

.info-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.damage-count {
  color: #F56C6C;
  font-weight: 700;
  font-size: 18px;
}

/* 优先级分析区 */
.priority-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 12px 0;
  position: relative;
  padding-left: 12px;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 20px;
  background: linear-gradient(180deg, #4096EE, #54C5F8);
  border-radius: 2px;
}

.priority-group {
  border-radius: 16px;
  transition: all 0.3s ease;
  overflow: hidden;
}

.priority-group:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.priority-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.priority-list {
  padding: 0;
}

.priority-item {
  padding: 16px 0;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 1px solid #f0f0f0;
  position: relative;
}

.priority-item:hover {
  background-color: #f9f9f9;
  padding-left: 8px;
}

.priority-item:last-child {
  border-bottom: none;
}

.damage-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.damage-location {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 4px;
}

.damage-impact {
  margin-top: 12px;
  padding: 12px;
  background-color: #f8fafc;
  border-radius: 8px;
  border-left: 4px solid #4096EE;
}

.impact-title {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
  font-weight: 600;
}

.impact-content {
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
}

.damage-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 18px;
  transition: all 0.3s ease;
}

.priority-item:hover .damage-arrow {
  color: #4096EE;
  transform: translateX(4px);
}

/* 维修方案推荐区 */
.repair-plan-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.plan-card {
  border-radius: 16px;
  transition: all 0.3s ease;
  overflow: hidden;
}

.plan-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.plan-title {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
}

.plan-list {
  padding: 0;
}

.plan-item {
  padding: 16px 0;
  position: relative;
}

.plan-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.plan-location {
  font-size: 16px;
  font-weight: 700;
  color: #303133;
}

.plan-time {
  font-size: 13px;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 4px;
}

.plan-time::before {
  content: '⏱️';
  font-size: 14px;
}

/* 预算按钮 */
.budget-button {
  margin-top: 16px;
  height: 52px;
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #4096EE, #54C5F8);
  border: none;
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(64, 150, 238, 0.3);
}

.budget-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(64, 150, 238, 0.4);
}

/* 损伤详情弹窗 */
.detail-dialog :deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

.detail-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #4096EE, #54C5F8);
  color: white;
  padding: 20px 24px;
}

.detail-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

.detail-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
  font-size: 20px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
}

.modal-body {
  padding: 20px 0;
}

.damage-image-container {
  position: relative;
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.damage-image {
  width: 100%;
  max-height: 320px;
  border-radius: 12px;
}

.detection-box {
  position: absolute;
  border: 3px solid #409EFF;
  border-radius: 6px;
  background: rgba(64, 150, 238, 0.15);
  box-shadow: 0 2px 8px rgba(64, 150, 238, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 2px 8px rgba(64, 150, 238, 0.3);
  }
  50% {
    box-shadow: 0 2px 16px rgba(64, 150, 238, 0.6);
  }
  100% {
    box-shadow: 0 2px 8px rgba(64, 150, 238, 0.3);
  }
}

.high-damage {
  border-color: #F56C6C;
  background: rgba(245, 108, 108, 0.15);
  box-shadow: 0 2px 8px rgba(245, 108, 108, 0.3);
}

.medium-damage {
  border-color: #E6A23C;
  background: rgba(230, 162, 60, 0.15);
  box-shadow: 0 2px 8px rgba(230, 162, 60, 0.3);
}

.low-damage {
  border-color: #67C23A;
  background: rgba(103, 194, 58, 0.15);
  box-shadow: 0 2px 8px rgba(103, 194, 58, 0.3);
}

.box-label {
  position: absolute;
  top: -28px;
  left: 0;
  background: #409EFF;
  color: white;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(64, 150, 238, 0.3);
}

.high-damage .box-label {
  background: #F56C6C;
  box-shadow: 0 2px 8px rgba(245, 108, 108, 0.3);
}

.medium-damage .box-label {
  background: #E6A23C;
  box-shadow: 0 2px 8px rgba(230, 162, 60, 0.3);
}

.low-damage .box-label {
  background: #67C23A;
  box-shadow: 0 2px 8px rgba(103, 194, 58, 0.3);
}

.damage-details {
  margin-top: 20px;
}

.impact-text {
  line-height: 1.8;
  font-size: 15px;
  color: #303133;
}

/* 时间线样式优化 */
.el-timeline :deep(.el-timeline-item__node) {
  background-color: #4096EE;
  border: 3px solid white;
  box-shadow: 0 2px 8px rgba(64, 150, 238, 0.3);
}

.el-timeline :deep(.el-timeline-item__node--danger) {
  background-color: #F56C6C;
  box-shadow: 0 2px 8px rgba(245, 108, 108, 0.3);
}

.el-timeline :deep(.el-timeline-item__node--warning) {
  background-color: #E6A23C;
  box-shadow: 0 2px 8px rgba(230, 162, 60, 0.3);
}

.el-timeline :deep(.el-timeline-item__node--success) {
  background-color: #67C23A;
  box-shadow: 0 2px 8px rgba(103, 194, 58, 0.3);
}

.el-timeline :deep(.el-timeline-item__tail) {
  border-left: 2px solid #e4e7ed;
}

.el-timeline :deep(.el-timeline-item__wrapper) {
  padding-left: 40px;
}

/* 标签间距优化 */
.el-tag + .el-tag {
  margin-left: 8px;
}

/* 响应式设计 */
@media (max-width: 375px) {
  .main-content {
    padding: 60px 12px 80px;
    gap: 12px;
  }
  
  .section-title {
    font-size: 18px;
    margin-bottom: 10px;
  }
  
  .damage-location {
    font-size: 16px;
  }
  
  .impact-content {
    font-size: 13px;
  }
  
  .plan-location {
    font-size: 15px;
  }
  
  .budget-button {
    height: 48px;
    font-size: 16px;
  }
  
  .damage-image {
    max-height: 240px;
  }
  
  .impact-text {
    font-size: 14px;
  }
  
  .priority-item {
    padding: 14px 0;
  }
  
  .plan-item {
    padding: 14px 0;
  }
  
  .damage-impact {
    padding: 10px;
    margin-top: 10px;
  }
}
</style>