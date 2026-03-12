<template>
  <div class="wechat-damage-detail">
    <!-- 导航栏 -->
    <el-row class="nav-bar" justify="space-between" align="middle">
      <el-col :span="4" class="nav-left" @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
      </el-col>
      <el-col :span="16" class="nav-title">定损详情报告</el-col>
      <el-col :span="4" class="nav-right">
        <el-icon class="nav-icon" @click="goHome"><HomeFilled /></el-icon>
      </el-col>
    </el-row>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 基础信息卡 -->
      <el-card class="info-card" shadow="hover">
        <template #header>
          <div class="info-header">
            <div class="info-title">基础信息</div>
            <div class="info-id">编号: {{ damageInfo.id }}</div>
          </div>
        </template>
        <el-row :gutter="16" class="info-grid">
          <el-col :span="12">
            <div class="info-item">
              <div class="info-label">车辆品牌</div>
              <div class="info-value">{{ detectionStore.carBrand || '未知' }}</div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="info-item">
              <div class="info-label">车型</div>
              <div class="info-value">{{ damageInfo.carModel }}</div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="info-item">
              <div class="info-label">检测时间</div>
              <div class="info-value">{{ damageInfo.detectionTime }}</div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="info-item">
              <div class="info-label">破损数量</div>
              <div class="info-value">{{ damageInfo.damageCount }} 处</div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 破损照片 -->
      <div class="damage-image-container" v-if="damageInfo.currentImage">
        <h3 class="section-title">破损照片</h3>
        <el-card class="damage-image-card" shadow="hover" @click="openImagePreview">
          <el-image 
            :src="damageInfo.currentImage" 
            alt="破损照片" 
            class="damage-image"
            fit="contain"
            @error="onImageError"
          />
        </el-card>
        <div class="image-hint">点击放大查看（带破损标注）</div>
      </div>

      <!-- 破损详情表 -->
      <div class="damage-table-container" v-if="damageInfo.damageDetails.length > 0">
        <h3 class="section-title">破损详情</h3>
        <el-card class="table-card" shadow="hover">
          <el-table :data="damageInfo.damageDetails" stripe class="damage-table">
            <el-table-column type="index" label="序号" width="60" align="center" />
            <el-table-column prop="location" label="破损部位" align="center" />
            <el-table-column prop="type" label="损伤类型" align="center" />
            <el-table-column prop="level" label="损伤等级" align="center">
              <template #default="{ row }">
                <el-tag :type="getSeverityTagType(row.levelClass)" effect="dark">
                  {{ row.level }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>

      <!-- 维修预算区 -->
      <div class="budget-section" v-if="damageInfo.budgetDetails.length > 0">
        <h3 class="section-title">维修预算</h3>
        <el-card class="budget-card" shadow="hover">
          <el-table :data="damageInfo.budgetDetails" stripe class="budget-table" show-summary>
            <el-table-column prop="item" label="维修项目" align="center" />
            <el-table-column prop="parts" label="配件费" align="center">
              <template #default="{ row }">
                ¥{{ row.parts }}
              </template>
            </el-table-column>
            <el-table-column prop="labor" label="工时费" align="center">
              <template #default="{ row }">
                ¥{{ row.labor }}
              </template>
            </el-table-column>
            <el-table-column prop="total" label="小计" align="center">
              <template #default="{ row }">
                ¥{{ row.total }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>

      <!-- 无数据提示 -->
      <el-empty v-if="!hasData" description="暂无检测数据，请先上传图片进行检测">
        <el-button type="primary" @click="goBack">返回检测页面</el-button>
      </el-empty>
    </div>

    <!-- 底部功能按钮 -->
    <div class="bottom-buttons">
      <el-row :gutter="12">
        <el-col :span="6">
          <el-card class="button-card" shadow="hover" @click="confirmDamage">
            <div class="button-content">
              <el-icon class="button-icon" color="#67C23A"><Check /></el-icon>
              <div class="button-text">确认定损</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="button-card" shadow="hover" @click="contactWorkshop">
            <div class="button-content">
              <el-icon class="button-icon" color="#409EFF"><Phone /></el-icon>
              <div class="button-text">联系维修厂</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="button-card" shadow="hover" @click="analyzeWithAI" :class="{ 'loading': llmLoading }">
            <div class="button-content">
              <el-icon class="button-icon" color="#E6A23C"><Loading v-if="llmLoading" /><Robot v-else /></el-icon>
              <div class="button-text">{{ llmLoading ? 'AI分析中...' : '查看详细定损报告' }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="button-card" shadow="hover" @click="saveReport">
            <div class="button-content">
              <el-icon class="button-icon" color="#909399"><Document /></el-icon>
              <div class="button-text">保存报告</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- AI分析结果弹窗 -->
    <el-dialog 
      v-model="showAIAnalysis" 
      title="AI定损分析报告" 
      width="90%" 
      :show-close="false"
      class="ai-analysis-dialog"
    >
      <template #header="{ close }">
        <div class="ai-analysis-header">
          <div class="ai-analysis-title">
            <el-icon><Cpu /></el-icon>
            AI定损分析报告
          </div>
          <el-button @click="close" :icon="Close" circle size="small" />
        </div>
      </template>
      
      <div class="ai-analysis-body">
        <div v-if="llmLoading" class="ai-analysis-loading">
          <el-icon class="loading-spinner" :size="32"><Loading /></el-icon>
          <div class="loading-text">AI正在分析车辆损伤，请稍候...</div>
        </div>
        <div v-else-if="llmAnalysis" class="ai-analysis-result">
          <el-descriptions :column="1" border class="ai-analysis-meta">
            <el-descriptions-item label="模型">{{ llmAnalysis.model }}</el-descriptions-item>
            <el-descriptions-item label="分析时间">{{ formatTime(llmAnalysis.timestamp) }}</el-descriptions-item>
          </el-descriptions>
          <div class="ai-analysis-text" v-html="formatAnalysis(llmAnalysis.analysis)"></div>
        </div>
        <el-empty v-else description="点击'查看详细定损报告'按钮生成智能定损报告" />
      </div>
    </el-dialog>

    <!-- 图片放大预览弹窗（带破损标注） -->
    <el-dialog
      v-model="showImagePreview"
      width="95%"
      :show-close="false"
      class="image-preview-dialog"
    >
      <template #header="{ close }">
        <div class="preview-header">
          <span>破损部位标注图</span>
          <el-button @click="close" :icon="Close" circle size="small" />
        </div>
      </template>
      
      <div class="preview-body" v-if="damageInfo.currentImage">
        <div class="preview-image-container">
          <el-image
            :src="damageInfo.currentImage"
            fit="contain"
            class="preview-image"
          />
          <!-- 破损标注框 -->
          <div 
            v-for="(region, index) in damageInfo.regions" 
            :key="index"
            class="damage-highlight-box"
            :style="getBoxStyle(region.bbox)"
          >
            <div class="highlight-label">{{ region.location }} ({{ region.level }})</div>
          </div>
        </div>
        
        <!-- 图例说明 -->
        <div class="preview-legend">
          <div class="legend-title">破损部位列表</div>
          <div class="legend-list">
            <div v-for="(region, index) in damageInfo.regions" :key="index" class="legend-item">
              <div class="legend-color" :style="{ background: getBoxColor(index) }"></div>
              <span class="legend-text">{{ index + 1 }}. {{ region.location }} - {{ region.type }} ({{ region.level }})</span>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDetectionStore } from '../store/detection'
import { 
  ArrowLeft, 
  HomeFilled, 
  Check, 
  Phone, 
  Loading, 
  Cpu, 
  Document, 
  Close 
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const detectionStore = useDetectionStore()
const imageZoomed = ref(false)
const currentImageIndex = ref(0)
const showAIAnalysis = ref(false)
const showImagePreview = ref(false)

// 从 store 获取 LLM 分析状态
const llmLoading = computed(() => detectionStore.llmLoading)
const llmAnalysis = computed(() => detectionStore.llmAnalysis)

// 获取路由参数中的taskId
const taskId = computed(() => route.params.taskId)

// 检查是否有数据
const hasData = computed(() => {
  return detectionStore.detectionResult && detectionStore.detectionResult.taskId === taskId.value
})

// 从store获取车型数据
const carModelInfo = computed(() => {
  return detectionStore.carModel || {
    brand: '本田',
    series: '雅阁',
    model: '2023款 260TURBO 豪华版'
  }
})

// 定损详情数据
const damageInfo = computed(() => {
  const result = detectionStore.detectionResult
  if (!result || result.taskId !== taskId.value) {
    return {
      id: taskId.value || 'DS20260302001',
      carModel: `${carModelInfo.value.brand} ${carModelInfo.value.series} ${carModelInfo.value.model}`,
      detectionTime: new Date().toLocaleString('zh-CN'),
      damageCount: 0,
      damageDetails: [],
      budgetDetails: [],
      totalBudget: 0,
      currentImage: ''
    }
  }

  // 部位映射
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

  // 类型映射
  const damageTypeToText = (damageType) => {
    const t = String(damageType || '').toUpperCase()
    const map = {
      PAINT: '车漆损伤',
      GLASS: '玻璃损伤',
      METAL: '钣金损伤',
      SCRATCH: '车漆损伤',
      DENT: '钣金损伤',
      CRACK: '玻璃损伤',
      BROKEN: '玻璃损伤'
    }
    return map[t] || '未知损伤'
  }

  // 严重程度映射
  const severityToText = (severity) => {
    const s = String(severity || '').toUpperCase()
    if (['LOW', 'MINOR'].includes(s)) return '轻'
    if (['MEDIUM', 'MODERATE'].includes(s)) return '中'
    if (['HIGH', 'SEVERE', 'CRITICAL'].includes(s)) return '重'
    return '中'
  }

  const severityToClass = (severity) => {
    const s = String(severity || '').toUpperCase()
    if (['LOW', 'MINOR'].includes(s)) return 'level-light'
    if (['MEDIUM', 'MODERATE'].includes(s)) return 'level-medium'
    if (['HIGH', 'SEVERE', 'CRITICAL'].includes(s)) return 'level-severe'
    return 'level-medium'
  }

  // 处理损伤详情
  const damageDetails = (result.regions || []).map(region => ({
    location: partMap[region.part_code] || region.part_code || '未知部位',
    type: damageTypeToText(region.damage_type),
    level: severityToText(region.severity_level),
    levelClass: severityToClass(region.severity_level),
    bbox: region.bbox
  }))

  // 处理预算
  const budgetDetails = damageDetails.map(detail => {
    let partsCost = 0, laborCost = 0
    if (detail.type.includes('玻璃')) { partsCost = 300; laborCost = 150 }
    else if (detail.type.includes('钣金')) { partsCost = 500; laborCost = 200 }
    else if (detail.type.includes('车漆')) { partsCost = 100; laborCost = 300 }
    return {
      item: `${detail.location}${detail.type}`,
      parts: partsCost,
      labor: laborCost,
      total: partsCost + laborCost
    }
  })

  const totalBudget = budgetDetails.reduce((sum, item) => sum + item.total, 0)

  // 处理图片
  const allImages = (result.images || [])
    .map(img => img.annotated_image_url || img.image_url || '')
    .filter(url => url)

  return {
    id: result.taskId || 'DS20260302001',
    carModel: `${carModelInfo.value.brand} ${carModelInfo.value.series} ${carModelInfo.value.model}`,
    detectionTime: new Date().toLocaleString('zh-CN'),
    damageCount: result.regions?.length || 0,
    damageDetails,
    budgetDetails,
    totalBudget,
    currentImage: allImages[currentImageIndex.value] || allImages[0] || '',
    regions: damageDetails
  }
})

const openImagePreview = () => { showImagePreview.value = true }
const goBack = () => { router.push('/wechat-detection') }
const goHome = () => { router.push('/') }
const confirmDamage = () => { alert('确认定损') }
const contactWorkshop = () => { alert('联系维修厂') }
const saveReport = () => { alert('保存报告') }

// 计算标注框样式
const getBoxStyle = (bbox) => {
  if (!bbox) return {}
  const coords = bbox.split(',').map(Number)
  if (coords.length !== 4) return {}
  
  const [x1, y1, x2, y2] = coords
  return {
    left: `${Math.min(x1, x2) / 3}%`,
    top: `${Math.min(y1, y2) / 2}%`,
    width: `${Math.abs(x2 - x1) / 3}%`,
    height: `${Math.abs(y2 - y1) / 2}%`
  }
}

// 获取标注框颜色
const getBoxColor = (index) => {
  const colors = ['#F56C6C', '#E6A23C', '#67C23A', '#409EFF', '#909399', '#6B4C9A']
  return colors[index % colors.length]
}

// 页面加载时检查是否有分析结果，如果有则自动显示
onMounted(() => {
  // 如果已经有分析结果，自动显示AI分析弹窗
  if (llmAnalysis.value) {
    showAIAnalysis.value = true
  }
})

// AI 分析方法（保留手动调用功能）
const analyzeWithAI = async () => {
  showAIAnalysis.value = true
  if (!llmAnalysis.value) {
    try {
      await detectionStore.analyzeWithLLM(taskId.value)
    } catch (err) {
      console.error('AI分析失败:', err)
      alert('AI分析失败: ' + (err.message || '请稍后重试'))
    }
  }
}

const closeAIAnalysis = () => {
  showAIAnalysis.value = false
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

// 格式化分析结果（将换行符转为 <br>）
const formatAnalysis = (text) => {
  if (!text) return ''
  return text.replace(/\n/g, '<br>')
}

// 获取严重程度标签类型
const getSeverityTagType = (levelClass) => {
  const typeMap = {
    'level-light': 'success',
    'level-medium': 'warning',
    'level-severe': 'danger'
  }
  return typeMap[levelClass] || 'info'
}

const onImageError = (event) => {
  event.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2Y1ZjdmYSIvPjx0ZXh0IHg9IjE1MCIgeT0iMTAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjOTA5Mzk5IiBmb250LXNpemU9IjE0Ij7nlKjmiLHnmoTmoLjlvankuI3phY3nvaE8L3RleHQ+PC9zdmc+'
}

onMounted(() => {
  console.log('DamageDetail页面加载, taskId:', taskId.value)
})
</script>

<style scoped>
.wechat-damage-detail {
  min-height: 100vh;
  background-color: #f5f7fa;
  position: relative;
}

/* 导航栏 */
.nav-bar {
  background: linear-gradient(90deg, #4096EE, #54C5F8, #66D3A8);
  height: 44px;
  padding: 0 16px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.nav-left {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
}

.nav-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.nav-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  border-radius: 50%;
  transition: background-color 0.3s ease;
}

.nav-icon:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-title {
  text-align: center;
  font-size: 16px;
  font-weight: 600;
  color: white;
  margin: 0;
}

@media (max-width: 768px) {
  .nav-bar {
    justify-content: center;
  }

  .nav-left {
    position: absolute;
    left: 0;
  }

  .nav-right {
    position: absolute;
    right: 0;
  }

  .nav-title {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    width: 60%;
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
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
  border-radius: 12px;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.info-id {
  font-size: 14px;
  color: #909399;
}

.info-item {
  padding: 12px 0;
}

.info-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
}

.info-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 破损照片 */
.damage-image-container {
  margin-bottom: 16px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
}

.damage-image-card {
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.damage-image-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.damage-image {
  width: 100%;
  max-height: 300px;
  border-radius: 8px;
}

.image-hint {
  text-align: center;
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

/* 表格样式 */
.table-card,
.budget-card {
  border-radius: 12px;
}

.damage-table :deep(.el-table__header),
.budget-table :deep(.el-table__header) {
  background-color: #f8fafc;
}

.damage-table :deep(.el-table__body),
.budget-table :deep(.el-table__body) {
  background-color: white;
}

/* 底部按钮 */
.bottom-buttons {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  padding: 12px 16px;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.button-card {
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.button-card:hover {
  transform: translateY(-2px);
}

.button-card.loading {
  opacity: 0.7;
}

.button-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.button-icon {
  font-size: 20px;
}

.button-text {
  font-size: 12px;
  color: #303133;
  font-weight: 500;
}

/* AI分析弹窗 */
.ai-analysis-dialog :deep(.el-dialog) {
  border-radius: 12px;
}

.ai-analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ai-analysis-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.ai-analysis-body {
  max-height: 60vh;
  overflow-y: auto;
}

.ai-analysis-loading {
  text-align: center;
  padding: 40px 20px;
}

.loading-spinner {
  color: #4096EE;
  margin-bottom: 16px;
}

.loading-text {
  color: #606266;
  font-size: 14px;
}

.ai-analysis-result {
  padding: 20px 0;
}

.ai-analysis-meta {
  margin-bottom: 20px;
}

.ai-analysis-text {
  line-height: 1.6;
  color: #303133;
  font-size: 14px;
}

/* 图片放大预览弹窗 */
.image-preview-dialog :deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.preview-body {
  padding: 0;
}

.preview-image-container {
  position: relative;
  height: 400px;
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

/* 破损标注框 */
.damage-highlight-box {
  position: absolute;
  border: 3px solid #F56C6C;
  border-radius: 4px;
  pointer-events: none;
  background: rgba(245, 108, 108, 0.15);
  box-shadow: 0 0 12px rgba(245, 108, 108, 0.6);
}

.highlight-label {
  position: absolute;
  top: -30px;
  left: 0;
  background: #F56C6C;
  color: white;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(245, 108, 108, 0.4);
}

/* 图例说明 */
.preview-legend {
  padding: 16px;
  background: #fff;
}

.legend-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.legend-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.legend-text {
  font-size: 14px;
  color: #606266;
}

/* 响应式设计 */
@media (max-width: 375px) {
  .main-content {
    padding: 60px 12px 80px;
    gap: 12px;
  }
  
  .button-card {
    height: 50px;
  }
  
  .button-icon {
    font-size: 18px;
  }
  
  .button-text {
    font-size: 11px;
  }
  
  .preview-image-container {
    height: 300px;
  }
  
  .highlight-label {
    font-size: 12px;
    top: -26px;
  }
}
</style>
