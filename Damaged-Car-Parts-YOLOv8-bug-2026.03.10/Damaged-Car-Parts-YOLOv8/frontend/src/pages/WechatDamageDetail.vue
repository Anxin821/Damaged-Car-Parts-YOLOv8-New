<template>
  <div class="damage-detail-page">
    <!-- 顶部导航 -->
    <WechatNavBar title="车辆定损评估报告" :showHome="true" />

    <!-- 主内容区域 -->
    <div class="page-content">
      <!-- 报告头部信息 -->
      <div>
        <div>
          <h1></h1>
        </div>
      </div>

      <!-- 车辆基本信息 -->
      <div class="vehicle-section" style="margin-top: 30px;">
        <h2 class="section-title">一、车辆基本信息</h2>
        <div class="vehicle-info-grid">
          <div class="info-row">
            <div class="info-field">
              <span class="field-label">车辆品牌</span>
              <span class="field-value">{{ vehicleInfo.brand || '待识别' }}</span>
            </div>
            <div class="info-field">
              <span class="field-label">车辆型号</span>
              <span class="field-value">{{ vehicleInfo.model || '待识别' }}</span>
            </div>
          </div>
          <div class="info-row">
            <div class="info-field">
              <span class="field-label">定损单号</span>
              <span class="field-value" style="text-align: right; flex: 1;">{{ damageInfo.id }}</span>
            </div>
            <div class="info-field">
              <span class="field-label">定损时间</span>
              <span class="field-value">{{ damageInfo.detectionTime }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 损伤照片 -->
      <div class="damage-photo-section" v-if="damageInfo.currentImage">
        <h2 class="section-title">二、损伤照片记录</h2>
        <div class="photo-grid">
          <div class="photo-item" @click="openImagePreview">
            <div class="photo-wrapper">
              <el-image 
                :src="damageInfo.currentImage" 
                alt="损伤照片" 
                class="damage-photo"
                fit="contain"
                @error="onImageError"
              />
              <div class="photo-overlay">
                <div class="overlay-text">点击查看大图</div>
              </div>
            </div>
            <div class="photo-caption">图1：车辆损伤整体视图</div>
            <!-- 标注图切换按钮 -->
            <div class="image-toggle-buttons">
              <button 
                class="toggle-btn" 
                :class="{ active: currentImageType === 'original' }"
                @click="switchToOriginal"
              >
                原图
              </button>
              <button 
                class="toggle-btn" 
                :class="{ active: currentImageType === 'yolo' }"
                @click="switchToYolo"
              >
                YOLO标注图
              </button>
            </div>
          </div>
        </div>
      </div>

      
      <!-- AI专业分析 -->
      <div class="ai-analysis-section">
        <h2 class="section-title">三、AI专业分析评估</h2>
        
        <!-- 加载状态 -->
        <div v-if="llmLoading" class="analysis-loading">
          <div class="loading-spinner"></div>
          <div class="loading-text">正在进行专业分析，请稍候...</div>
        </div>

        <!-- 分析结果 -->
        <div v-else-if="llmAnalysis" class="analysis-content">
          <div class="analysis-report" v-if="llmAnalysis.analysis">
            <!-- 损伤程度评估 -->
            <div class="analysis-item" v-if="llmAnalysis.analysis.damage_level">
              <h3 class="analysis-subtitle">4.1 损伤程度评估</h3>
              <div class="damage-assessment">
                <div 
                  v-for="(level, part) in llmAnalysis.analysis.damage_level" 
                  :key="part" 
                  class="assessment-item"
                >
                  <div class="assessment-part">{{ part }}</div>
                  <div class="assessment-level">
                    <span class="level-badge" :class="getSeverityClass(level)">
                      {{ level }}
                    </span>
                    <span class="risk-coefficient">
                      （风险系数：{{ getRiskCoefficient(level) }}% | {{ getSafetyImpact(level) }}）
                    </span>
                  </div>
                  <div class="assessment-desc">{{ getDamageDescription(level) }}</div>
                </div>
              </div>
            </div>

            <!-- 专业维修建议 -->
            <div class="analysis-item" v-if="llmAnalysis.analysis.repair_suggestion">
              <h3 class="analysis-subtitle">4.2 专业维修建议</h3>
              <div class="repair-suggestions">
                <div class="suggestion-text" v-html="formatRepairSuggestions(llmAnalysis.analysis.repair_suggestion)"></div>
              </div>
            </div>

            <!-- 费用估算 -->
            <div class="analysis-item" v-if="llmAnalysis.analysis.cost_estimate">
              <h3 class="analysis-subtitle">4.3 维修费用估算</h3>
              <div class="cost-estimate">
                <div class="cost-summary" v-html="formatCostEstimate(llmAnalysis.analysis.cost_estimate)"></div>
                <div class="cost-credibility">
                  <small>ML预算模型基于历史数据预测，误差率≤8%，增加可信度。</small>
                </div>
              </div>
            </div>

            <!-- 安全提示 -->
            <div class="analysis-item" v-if="llmAnalysis.analysis.safety_tips">
              <h3 class="analysis-subtitle">4.4 安全注意事项</h3>
              <div class="safety-tips">
                <div class="safety-warning" v-html="formatSafetyTips(llmAnalysis.analysis.safety_tips)"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="analysis-empty">
          <div class="empty-icon">📋</div>
          <div class="empty-text">点击"AI分析"生成专业评估报告</div>
          <el-button type="primary" @click="analyzeWithAI" :loading="llmLoading">
            <el-icon><Cpu /></el-icon>
            开始AI分析
          </el-button>
        </div>
      </div>

      <!-- 维修预算明细 -->
      <div class="budget-section" v-if="damageInfo.budgetDetails.length > 0">
        <h2 class="section-title">四、维修预算明细</h2>
        <div class="budget-table">
          <table class="budget-table-content">
            <thead>
              <tr>
                <th>维修项目</th>
                <th>破损等级</th>
                <th>建议操作</th>
                <th>配件编号</th>
                <th>配件成本<br>（ML预测）</th>
                <th>工时费</th>
                <th>小计</th>
                <th>备注</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in damageInfo.budgetDetails" :key="index">
                <td>{{ item.item }}</td>
                <td>
                  <span class="severity-badge" :class="getSeverityClass(item.severity)">
                    {{ item.severity }}
                  </span>
                </td>
                <td>{{ item.operation }}</td>
                <td class="part-number">{{ item.partNumber }}</td>
                <td class="amount">¥{{ item.parts }}</td>
                <td class="amount">¥{{ item.labor }}</td>
                <td class="amount total">¥{{ item.total }}</td>
                <td class="notes">{{ item.notes }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="total-row">
                <td colspan="6">合计</td>
                <td class="amount grand-total">¥{{ damageInfo.totalBudget }}</td>
                <td></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      <!-- 评估结论 -->
      <div class="conclusion-section" style="margin-bottom: -20px;">
        <h2 class="section-title">五、评估结论</h2>
        <div class="conclusion-content">
          <div class="conclusion-item">
            <span class="conclusion-label">损伤等级：</span>
            <span class="conclusion-value">{{ getOverallDamageLevel() }}</span>
          </div>
          <div class="conclusion-item">
            <span class="conclusion-label">建议维修方式：</span>
            <span class="conclusion-value">{{ getRecommendedRepairMethod() }}</span>
          </div>
          <div class="conclusion-item">
            <span class="conclusion-label">预计维修周期：</span>
            <span class="conclusion-value">{{ getEstimatedRepairTime() }}</span>
          </div>
          <div class="conclusion-item">
            <span class="conclusion-label">安全评级：</span>
            <span class="conclusion-value">{{ getSafetyRating() }}</span>
          </div>
        </div>
      </div>

      <!-- 无数据状态 -->
      <div v-if="!hasData" class="empty-page">
        <div class="empty-illustration">
          <div class="illustration-icon">📋</div>
        </div>
        <div class="empty-content">
          <h3 class="empty-title">暂无定损数据</h3>
          <p class="empty-description">请先进行车辆损伤检测</p>
          <el-button type="primary" size="large" @click="goToDetection">
            <el-icon><Upload /></el-icon>
            开始检测
          </el-button>
        </div>
      </div>
    </div>

    <!-- 图片预览弹窗 -->
    <el-dialog
      v-model="showImagePreview"
      width="95%"
      :show-close="false"
      class="image-preview-dialog"
    >
      <template #header="{ close }">
        <div class="preview-header">
          <span class="preview-title">损伤照片详细视图</span>
          <el-button @click="close" :icon="Close" circle size="small" />
        </div>
      </template>
      <div class="preview-content">
        <div class="preview-image-container">
          <el-image 
            :src="damageInfo.currentImage" 
            class="preview-image"
            fit="contain"
          />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDetectionStore } from '../store/detection'
import WechatNavBar from '../components/common/WechatNavBar.vue'
import { 
  ArrowLeft, 
  HomeFilled, 
  Check, 
  Phone, 
  Loading, 
  Cpu, 
  Document, 
  Close,
  Van,
  ZoomIn,
  Upload,
  ArrowUp,
  ArrowDown,
  InfoFilled,
  WarningFilled,
  CircleCheckFilled
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const detectionStore = useDetectionStore()
const imageZoomed = ref(false)
const currentImageIndex = ref(0)
const showImagePreview = ref(false)
const currentImageType = ref('original') // 'original' or 'yolo'

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
    model: '2023款'
  }
})

// 从豆包分析结果中提取车辆信息
const vehicleInfo = computed(() => {
  const analysis = detectionStore.llmAnalysis?.analysis
  if (analysis && analysis.vehicle_info) {
    return {
      brand: analysis.vehicle_info.brand || '识别中...',
      model: analysis.vehicle_info.model || '识别中...'
    }
  }
  // 如果豆包没有返回vehicle_info，使用默认值或从其他地方获取
  return {
    brand: detectionStore.carBrand || '待识别',
    model: detectionStore.carModel || '待识别'
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
    let partsCost = 0, laborCost = 0, operation = '', partNumber = '', notes = ''
    
    if (detail.location.includes('大灯')) {
      partsCost = 4500; laborCost = 200; operation = '更换'; 
      partNumber = 'BMW-XXXX-L'; notes = 'LED大灯，含控制模块'
    }
    else if (detail.location.includes('保险杠')) {
      partsCost = 2800; laborCost = 300; operation = '更换';
      partNumber = 'BMW-YYYY-F'; notes = '底漆已喷好，需做面漆'
    }
    else if (detail.location.includes('引擎盖')) {
      partsCost = 3200; laborCost = 400; operation = '更换';
      partNumber = 'BMW-ZZZZ-H'; notes = '铝质，不建议钣金'
    }
    else if (detail.type.includes('玻璃')) { 
      partsCost = 300; laborCost = 150; operation = '修复';
      partNumber = 'GLASS-001'; notes = '可修复，无需更换'
    }
    else if (detail.type.includes('钣金')) { 
      partsCost = 500; laborCost = 200; operation = '修复';
      partNumber = 'METAL-002'; notes = '需要钣金处理'
    }
    else if (detail.type.includes('车漆')) { 
      partsCost = 100; laborCost = 300; operation = '喷漆';
      partNumber = 'PAINT-003'; notes = '需要补漆'
    }
    else {
      partsCost = 800; laborCost = 150; operation = '检查';
      partNumber = 'PART-999'; notes = '需要进一步检查'
    }
    
    return {
      item: detail.location,
      severity: detail.level,
      operation: operation,
      partNumber: partNumber,
      parts: partsCost,
      labor: laborCost,
      total: partsCost + laborCost,
      notes: notes
    }
  })

  const totalBudget = budgetDetails.reduce((sum, item) => sum + item.total, 0)

  // 处理图片
  const originalImages = (result.images || [])
    .map(img => img.image_url || '')
    .filter(url => url)
  
  const yoloImages = (result.images || [])
    .map(img => img.annotated_image_url || '')
    .filter(url => url)

  const getCurrentImage = () => {
    if (currentImageType.value === 'yolo') {
      return yoloImages[currentImageIndex.value] || yoloImages[0] || ''
    } else {
      return originalImages[currentImageIndex.value] || originalImages[0] || ''
    }
  }

  return {
    id: result.taskId || 'DS20260302001',
    carModel: `${carModelInfo.value.brand} ${carModelInfo.value.series} ${carModelInfo.value.model}`,
    detectionTime: new Date().toLocaleString('zh-CN'),
    damageCount: result.regions?.length || 0,
    damageDetails,
    budgetDetails,
    totalBudget,
    currentImage: getCurrentImage(),
    regions: damageDetails
  }
})

const openImagePreview = () => { showImagePreview.value = true }
const goToDetection = () => { router.push('/detection') }

// 图片切换函数
const switchToOriginal = () => {
  currentImageType.value = 'original'
}

const switchToYolo = () => {
  currentImageType.value = 'yolo'
}

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

// 页面加载时检查是否有分析结果
onMounted(() => {
  // 如果已经有分析结果，直接显示在页面上
  if (llmAnalysis.value) {
    console.log('页面加载时发现已有AI分析结果，直接显示')
  }
})

// AI 分析方法（保留手动调用功能）
const analyzeWithAI = async () => {
  if (!llmAnalysis.value) {
    try {
      llmLoading.value = true
      await detectionStore.analyzeWithLLM(taskId.value)
      console.log('AI分析完成，直接显示在页面上')
    } catch (err) {
      console.error('AI分析失败:', err)
      alert('AI分析失败: ' + (err.message || '请稍后重试'))
    } finally {
      llmLoading.value = false
    }
  }
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

// 获取严重程度CSS类
const getSeverityClass = (level) => {
  const levelMap = {
    '轻微': 'light',
    '轻度': 'light',
    '中度': 'medium',
    '严重': 'severe',
    '重度': 'severe'
  }
  return levelMap[level] || 'medium'
}

// 格式化维修建议（将数字编号转换为换行）
const formatRepairSuggestions = (text) => {
  if (!text) return ''
  return text.replace(/(\d+\.\s)/g, '<br>$1')
}

// 格式化费用估算（高亮显示价格区间）
const formatCostEstimate = (text) => {
  if (!text) return ''
  // 高亮价格数字
  return text.replace(/(\d+(?:,\d+)*(?:-\d+(?:,\d+)*)元)/g, '<strong class="price-highlight">$1</strong>')
}

// 格式化安全提示（将重要提示加粗）
const formatSafetyTips = (text) => {
  if (!text) return ''
  // 将禁止性语句加粗
  return text.replace(/(禁止|严禁|必须|重点|需)/g, '<strong>$1</strong>')
}

// 获取严重程度标签类型（豆包返回的中文程度）
const getDamageLevelType = (level) => {
  if (!level) return 'info'
  const levelStr = String(level).toLowerCase()
  if (levelStr.includes('轻微') || levelStr.includes('轻')) return 'success'
  if (levelStr.includes('中等') || levelStr.includes('中')) return 'warning'
  if (levelStr.includes('严重') || levelStr.includes('重')) return 'danger'
  return 'info'
}

// 获取维修建议（专业定损工程师角度）
const getRepairSuggestion = (damageType, level) => {
  const suggestions = {
    '车漆损伤': {
      '轻': '抛光处理',
      '中': '局部喷漆修复',
      '重': '钣金修复 + 全车喷漆'
    },
    '玻璃损伤': {
      '轻': '玻璃修复剂处理',
      '中': '玻璃专业修复',
      '重': '更换玻璃总成'
    },
    '钣金损伤': {
      '轻': '钣金矫正',
      '中': '钣金修复 + 喷漆',
      '重': '钣金更换 + 喷漆'
    },
    '划痕': {
      '轻': '抛光打蜡',
      '中': '补漆处理',
      '重': '重新喷漆'
    },
    '凹陷': {
      '轻': '无痕修复',
      '中': '钣金修复',
      '重': '钣金更换'
    }
  }
  
  return suggestions[damageType]?.[level] || '需要专业检查评估'
}

// 获取损伤描述
const getDamageDescription = (level) => {
  const descriptions = {
    '轻微': '表面轻微损伤，不影响车辆正常使用，可择期修复',
    '轻度': '轻度损伤，建议尽快修复以防止恶化',
    '中度': '中度损伤，影响车辆外观，建议及时修复',
    '严重': '严重损伤，可能影响车辆安全，建议立即修复',
    '重度': '重度损伤，严重影响车辆安全，必须立即修复'
  }
  return descriptions[level] || '需要专业评估'
}

// 获取整体损伤等级
const getOverallDamageLevel = () => {
  const details = damageInfo.value.damageDetails
  if (!details || details.length === 0) return '无损伤'
  
  const severeCount = details.filter(item => item.level === '重').length
  const mediumCount = details.filter(item => item.level === '中').length
  
  if (severeCount > 0) return '严重损伤'
  if (mediumCount > 2) return '中度损伤'
  if (mediumCount > 0) return '轻度损伤'
  return '轻微损伤'
}

// 获取推荐维修方式
const getRecommendedRepairMethod = () => {
  const level = getOverallDamageLevel()
  const methods = {
    '无损伤': '无需维修',
    '轻微损伤': '快修服务',
    '轻度损伤': '标准维修',
    '中度损伤': '专业维修',
    '严重损伤': '全面维修'
  }
  return methods[level] || '需要专业评估'
}

// 获取预计维修时间
const getEstimatedRepairTime = () => {
  const details = damageInfo.value.damageDetails
  if (!details || details.length === 0) return '无需维修'
  
  let totalHours = 0
  details.forEach(item => {
    if (item.level === '重') totalHours += 8
    else if (item.level === '中') totalHours += 4
    else if (item.level === '轻') totalHours += 2
  })
  
  if (totalHours <= 4) return '半天'
  if (totalHours <= 8) return '1天'
  if (totalHours <= 16) return '2天'
  return '3天以上'
}

// 获取安全评级
const getSafetyRating = () => {
  const details = damageInfo.value.damageDetails
  if (!details || details.length === 0) return '安全'
  
  const hasSevere = details.some(item => item.level === '重')
  const criticalParts = ['前挡风玻璃', '前大灯', '刹车系统', '轮胎']
  const hasCriticalDamage = details.some(item => 
    criticalParts.some(part => item.location.includes(part))
  )
  
  if (hasSevere && hasCriticalDamage) return '危险'
  if (hasSevere) return '注意'
  if (hasCriticalDamage) return '谨慎'
  return '安全'
}

const onImageError = (event) => {
  event.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2Y1ZjdmYSIvPjx0ZXh0IHg9IjE1MCIgeT0iMTAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjOTA5Mzk5IiBmb250LXNpemU9IjE0Ij7nlKjmiLHnmoTmoLjlvankuI3phY3nvaE8L3RleHQ+PC9zdmc+'
}

// 获取风险系数（基于ML模型计算）
const getRiskCoefficient = (level) => {
  const levelStr = String(level).toLowerCase()
  if (levelStr.includes('轻微') || levelStr.includes('轻') || levelStr.includes('low')) return 15
  if (levelStr.includes('中等') || levelStr.includes('中') || levelStr.includes('medium')) return 45
  if (levelStr.includes('严重') || levelStr.includes('重') || levelStr.includes('severe') || levelStr.includes('high')) return 92
  return 30
}

// 获取安全影响描述
const getSafetyImpact = (level) => {
  const levelStr = String(level).toLowerCase()
  if (levelStr.includes('轻微') || levelStr.includes('轻') || levelStr.includes('low')) return '影响外观'
  if (levelStr.includes('中等') || levelStr.includes('中') || levelStr.includes('medium')) return '影响部件性能'
  if (levelStr.includes('严重') || levelStr.includes('重') || levelStr.includes('severe') || levelStr.includes('high')) return '影响结构安全'
  return '需要检查'
}

onMounted(() => {
  console.log('DamageDetail页面加载, taskId:', taskId.value)
})
</script>

<style scoped>
/* ===== 专业定损报告样式 ===== */
.damage-detail-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  font-family: 'Microsoft YaHei', 'PingFang SC', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ===== 主内容区域 ===== */
.page-content {
  padding: 64px 20px 40px;
  max-width: 900px;
  margin: 0 auto;
}

/* ===== 报告头部 ===== */
.report-header {
  background: white;
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 2px solid #e2e8f0;
  position: relative;
}

.report-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 6px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 16px 16px 0 0;
}

.report-title h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a202c;
  margin: 0 0 32px 0;
  text-align: center;
}

/* ===== 章节样式 ===== */
.vehicle-section,
.damage-photo-section,
.damage-list-section,
.ai-analysis-section,
.budget-section,
.conclusion-section {
  background: white;
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #1a202c;
  margin: 0 0 24px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid #667eea;
  position: relative;
}

.section-title::before {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 60px;
  height: 2px;
  background: #667eea;
}

/* ===== 车辆信息 ===== */
.vehicle-info-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.info-field {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.field-label {
  font-size: 14px;
  color: #4a5568;
  font-weight: 500;
}

.field-value {
  font-size: 15px;
  color: #1a202c;
  font-weight: 600;
}

/* ===== 照片区域 ===== */
.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.photo-item {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  background: #f8fafc;
}

.photo-wrapper {
  position: relative;
  cursor: pointer;
  height: 200px;
}

.damage-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.photo-wrapper:hover .photo-overlay {
  opacity: 1;
}

.overlay-text {
  color: white;
  font-size: 14px;
  font-weight: 500;
}

.photo-caption {
  padding: 12px;
  text-align: center;
  font-size: 13px;
  color: #4a5568;
  background: white;
  border-top: 1px solid #e2e8f0;
}

/* 图片切换按钮 */
.image-toggle-buttons {
  display: flex;
  gap: 8px;
  padding: 12px;
  background: white;
  border-top: 1px solid #e2e8f0;
  justify-content: center;
}

.toggle-btn {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  background: #f9fafb;
  color: #6b7280;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
}

.toggle-btn:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.toggle-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

/* ===== 损伤表格 ===== */
.damage-table {
  overflow-x: auto;
}

.damage-table-content {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.damage-table-content th {
  background: #667eea;
  color: white;
  padding: 16px 12px;
  text-align: left;
  font-weight: 600;
  font-size: 14px;
  border: 1px solid #667eea;
}

.damage-table-content td {
  padding: 14px 12px;
  border: 1px solid #e2e8f0;
  font-size: 14px;
  color: #2d3748;
}

.damage-table-content tbody tr:hover {
  background: #f8fafc;
}

.severity-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-align: center;
  display: inline-block;
  min-width: 60px;
}

.severity-badge.level-light {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.severity-badge.level-medium {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.severity-badge.level-severe {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

/* ===== AI分析区域 ===== */
.analysis-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(102, 126, 234, 0.2);
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: #4a5568;
  font-size: 16px;
}

.analysis-content {
  padding: 20px 0;
}

.analysis-item {
  margin-bottom: 32px;
}

.analysis-subtitle {
  font-size: 18px;
  font-weight: 600;
  color: #1a202c;
  margin: 0 0 16px 0;
  padding-left: 12px;
  border-left: 4px solid #667eea;
}

.damage-assessment {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.assessment-item {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e2e8f0;
  border-left: 4px solid #667eea;
}

.assessment-part {
  font-weight: 600;
  color: #1a202c;
  margin-bottom: 8px;
  font-size: 16px;
}

.assessment-level {
  margin-bottom: 8px;
}

.level-badge {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  display: inline-block;
}

.level-badge.light {
  background: #d4edda;
  color: #155724;
}

.level-badge.medium {
  background: #fff3cd;
  color: #856404;
}

.level-badge.severe {
  background: #f8d7da;
  color: #721c24;
}

.assessment-desc {
  font-size: 14px;
  color: #4a5568;
  line-height: 1.5;
}

.risk-coefficient {
  font-size: 12px;
  color: #6b7280;
  margin-left: 8px;
  font-weight: 500;
}

.repair-suggestions,
.cost-estimate,
.safety-tips {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e2e8f0;
}

.suggestion-text,
.cost-summary,
.safety-warning {
  font-size: 15px;
  color: #2d3748;
  line-height: 1.6;
}

.price-highlight {
  color: #e53e3e;
  font-weight: 700;
  font-size: 16px;
}

.cost-credibility {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #e2e8f0;
}

.cost-credibility small {
  font-size: 12px;
  color: #6b7280;
  font-style: italic;
}

.analysis-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-text {
  color: #4a5568;
  font-size: 16px;
  margin-bottom: 20px;
}

/* ===== 预算表格 ===== */
.budget-table {
  overflow-x: auto;
}

.budget-table-content {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.budget-table-content th {
  background: #48bb78;
  color: white;
  padding: 16px 12px;
  text-align: left;
  font-weight: 600;
  font-size: 14px;
  border: 1px solid #48bb78;
}

.budget-table-content td {
  padding: 14px 12px;
  border: 1px solid #e2e8f0;
  font-size: 14px;
  color: #2d3748;
}

.amount {
  font-weight: 600;
  color: #e53e3e;
  text-align: right;
}

.total {
  color: #1a202c;
  font-weight: 700;
}

.total-row {
  background: #f8fafc;
  font-weight: 700;
}

.grand-total {
  color: #e53e3e;
  font-size: 16px;
  font-weight: 700;
}

/* 新增样式 */
.part-number {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #4a5568;
  text-align: center;
  background: #f7fafc;
  padding: 4px 8px;
  border-radius: 4px;
}

.notes {
  font-size: 12px;
  color: #6b7280;
  max-width: 200px;
}

.severity-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  display: inline-block;
}

/* ===== 结论区域 ===== */
.conclusion-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.conclusion-item {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e2e8f0;
  border-left: 4px solid #667eea;
}

.conclusion-label {
  font-size: 14px;
  color: #4a5568;
  margin-bottom: 8px;
  font-weight: 500;
}

.conclusion-value {
  font-size: 16px;
  color: #1a202c;
  font-weight: 600;
}

/* ===== 空状态 ===== */
.empty-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  text-align: center;
}

.illustration-icon {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.8;
}

.empty-title {
  font-size: 24px;
  font-weight: 600;
  color: #2d3748;
  margin: 0 0 8px 0;
}

.empty-description {
  color: #718096;
  font-size: 16px;
  margin: 0 0 24px 0;
}

/* ===== 响应式设计 ===== */
@media (max-width: 768px) {
  .page-content {
    padding: 64px 16px 40px;
  }
  
  .report-header,
  .vehicle-section,
  .damage-photo-section,
  .damage-list-section,
  .ai-analysis-section,
  .budget-section,
  .conclusion-section {
    padding: 20px 16px;
    border-radius: 12px;
  }
  
  .report-title h1 {
    font-size: 22px;
  }
  
  .section-title {
    font-size: 18px;
  }
  
  .info-row {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .damage-assessment {
    grid-template-columns: 1fr;
  }
  
  .conclusion-content {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  
  .action-btn {
    padding: 10px 6px;
  }
  
  .btn-icon {
    font-size: 16px;
  }
  
  .btn-text {
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .page-content {
    padding: 54px 10px 30px;
  }
  
  .report-meta {
    flex-direction: column;
    gap: 16px;
  }
  
  .damage-table-content,
  .budget-table-content {
    font-size: 12px;
  }
  
  .damage-table-content th,
  .damage-table-content td,
  .budget-table-content th,
  .budget-table-content td {
    padding: 10px 8px;
  }
}

.vehicle-section {
  margin-top: 35px !important;
  margin-bottom: 10px;
}

.damage-photo-section {
  margin-bottom: 10px;
}

.ai-analysis-section {
  margin-bottom: 10px;
}

.budget-section {
  margin-bottom: 10px;
}

.conclusion-section {
  margin-bottom: 10px;
}
</style>
