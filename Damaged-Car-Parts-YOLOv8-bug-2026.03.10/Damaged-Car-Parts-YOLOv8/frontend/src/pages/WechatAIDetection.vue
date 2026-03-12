<template>
  <div class="wechat-ai-detection">
    <!-- 导航栏 -->
    <el-row class="nav-bar" justify="space-between" align="middle">
      <el-col :span="4" class="nav-left" @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
      </el-col>
      <el-col :span="16" class="nav-title">AI 智能定损</el-col>
      <el-col :span="4" class="nav-right">
        <el-space :size="8">
          <el-icon class="nav-icon" @click="goHome"><HomeFilled /></el-icon>
          <el-icon class="nav-icon" @click="showHelp"><QuestionFilled /></el-icon>
        </el-space>
      </el-col>
    </el-row>
    
    <!-- 隐藏的文件输入 -->
    <input type="file" ref="fileInput" multiple accept="image/*" style="display: none" @change="handleFileSelect">
    
    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 上传卡片 -->
      <el-card class="upload-card" shadow="hover" @click="openUploadOptions">
        <div class="upload-content">
          <div class="upload-icon">
            <el-icon :size="48"><Picture /></el-icon>
          </div>
          <div class="upload-text">点击上传车辆破损照片</div>
          <div class="upload-subtext">单张 / 多张均可</div>
          <div class="upload-hint">检测响应≤5 秒，识别准确率≥90%</div>
        </div>
      </el-card>
      
      <!-- 照片缩略图区域 -->
      <div class="thumbnail-area" v-if="uploadedImages.length > 0">
        <el-row :gutter="8" class="thumbnail-grid">
          <el-col :span="8" v-for="(image, index) in uploadedImages" :key="index">
            <div class="thumbnail-item">
              <el-image :src="image" alt="车辆照片" class="thumbnail-img" fit="cover" />
              <div class="thumbnail-remove" @click.stop="removeImage(index)">
                <el-icon><Close /></el-icon>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <!-- 一键检测按钮 -->
      <el-button 
        type="primary" 
        size="large" 
        class="detection-button" 
        @click="startDetection" 
        :disabled="uploadedImages.length === 0 || isDetecting"
        :loading="isDetecting"
        block
      >
        {{ isDetecting ? '检测中...' : '一键检测' }}
      </el-button>
      
      <!-- 检测结果区域 -->
      <div class="result-area" v-if="showResult">
        <el-card class="result-card">
          <template #header>
            <div class="result-header">
              <h3>检测结果</h3>
            </div>
          </template>
          
          <!-- 检测结果头部 -->
          <div class="result-top-section">
            <!-- 核心数据概览 -->
            <div class="data-overview">
              <div class="overview-item">
                <div class="overview-number">{{ detectionResult?.regions?.length || 0 }}</div>
                <div class="overview-label">损伤处</div>
              </div>
              <div class="overview-item">
                <div class="overview-number">{{ getDamageTypes.length }}</div>
                <div class="overview-label">损伤类型</div>
              </div>
              <div class="overview-item">
                <div class="overview-number">{{ detectionResult?.images?.length || 0 }}</div>
                <div class="overview-label">检测图片</div>
              </div>
            </div>
          </div>
          
          <!-- 车辆信息卡片 -->
          <div class="vehicle-info-section" v-if="detectionStore.carBrand || detectionStore.carModel">
            <div class="section-title">车辆信息</div>
            <div class="vehicle-cards">
              <div class="vehicle-card" v-if="detectionStore.carBrand">
                <div class="card-icon">
                  <el-icon><Clock /></el-icon>
                </div>
                <div class="card-content">
                  <div class="card-title">品牌</div>
                  <div class="card-value">{{ detectionStore.carBrand }}</div>
                  <div class="card-subtitle">置信度 {{ (detectionStore.carBrandConfidence * 100).toFixed(1) }}%</div>
                </div>
              </div>
              
              <div class="vehicle-card" v-if="detectionStore.carModel">
                <div class="card-icon">
                  <el-icon><Van /></el-icon>
                </div>
                <div class="card-content">
                  <div class="card-title">车型</div>
                  <div class="card-value">{{ detectionStore.carModel.brand }} {{ detectionStore.carModel.series }}</div>
                  <div class="card-subtitle">{{ detectionStore.carModel.model }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 检测结果图片 -->
          <div class="detection-images-section">
            <div v-if="detectionResult?.images?.length" class="result-images">
              <el-card v-for="img in detectionResult.images" :key="img.id" class="result-image-wrap" shadow="hover">
                <el-image 
                  :src="img.annotated_image_url || img.image_url" 
                  alt="检测结果" 
                  class="result-image" 
                  fit="contain"
                  @load="(e) => onResultImageLoad(img.id, e)" 
                />
                <div v-if="!img.annotated_image_url"
                     v-for="region in getRegionsByImage(img.id)"
                     :key="region.id"
                     class="detection-box"
                     :class="getDamageClass(region.damage_type)"
                     :style="getRegionStyle(img.id, region.bbox)">
                  <div class="box-label">{{ damageTypeToText(region.damage_type) }} ({{ severityToText(region.severity_level) }})</div>
                </div>
              </el-card>
            </div>
            <el-empty v-else description="暂无检测图片" />
          </div>
          
          <!-- 损伤详情 -->
          <div class="damage-analysis-section" v-if="detectionResult">
            <div class="analysis-grid">
              <div class="analysis-card" v-if="getDamageParts.length > 0">
                <div class="analysis-icon">
                  <el-icon><Location /></el-icon>
                </div>
                <div class="analysis-content">
                  <div class="analysis-label">损伤部位</div>
                  <div class="analysis-value">{{ getDamageParts.join('、') }}</div>
                </div>
              </div>
              
              <div class="analysis-card" v-if="getDamageTypes.length > 0">
                <div class="analysis-icon">
                  <el-icon><Search /></el-icon>
                </div>
                <div class="analysis-content">
                  <div class="analysis-label">损伤类型</div>
                  <div class="analysis-value">{{ getDamageTypes.join('、') }}</div>
                </div>
              </div>
              
              <div class="analysis-card" v-if="getSeverityLevels.length > 0">
                <div class="analysis-icon">
                  <el-icon><Warning /></el-icon>
                </div>
                <div class="analysis-content">
                  <div class="analysis-label">严重程度</div>
                  <div class="analysis-value">{{ getSeverityLevels.join('、') }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 操作按钮 -->
          <div class="result-buttons">
            <el-button type="primary" size="large" @click="viewReport" class="result-button">
              查看详细定损报告
            </el-button>
            <el-button type="success" size="large" @click="preRepairAnalysis" class="result-button">
              预修车分析
            </el-button>
          </div>
        </el-card>
      </div>
    </div>
    
    <!-- 上传选项弹窗 -->
    <el-dialog 
      v-model="showUploadModal" 
      title="选择上传方式" 
      width="90%" 
      :show-close="false"
      class="upload-dialog"
    >
      <div class="modal-options">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-card class="modal-option" shadow="hover" @click="openCamera">
              <div class="option-content">
                <el-icon class="option-icon camera-icon" :size="32"><Camera /></el-icon>
                <div class="option-text">拍照</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="modal-option" shadow="hover" @click="chooseFromAlbum">
              <div class="option-content">
                <el-icon class="option-icon album-icon" :size="32"><Picture /></el-icon>
                <div class="option-text">从相册选择</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      <template #footer>
        <el-button @click="closeUploadModal" size="large" style="width: 100%">取消</el-button>
      </template>
    </el-dialog>

    <!-- 拍照预览弹窗 -->
    <el-dialog 
      v-model="showCameraModal" 
      title="拍照" 
      width="95%" 
      :show-close="false"
      class="camera-dialog"
    >
      <div class="camera-preview-wrap">
        <video ref="cameraVideo" autoplay playsinline muted class="camera-video"></video>
      </div>
      <template #footer>
        <el-space :size="12" style="width: 100%">
          <el-button @click="closeCamera" size="large" style="flex: 1">取消</el-button>
          <el-button type="primary" @click="capturePhoto" size="large" style="flex: 1">拍照</el-button>
        </el-space>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { detectionApi, repairApi } from '../api'
import { useDetectionStore } from '../store/detection'
import { 
  ArrowLeft, 
  HomeFilled, 
  QuestionFilled, 
  Picture, 
  Close, 
  Camera, 
  Clock, 
  Van, 
  Location, 
  Search, 
  Warning,
  CircleCheck
} from '@element-plus/icons-vue'

const router = useRouter()
const detectionStore = useDetectionStore()
const uploadedImages = ref([])
const showResult = ref(false)
const showUploadModal = ref(false)
const showCameraModal = ref(false)
const fileInput = ref(null)
const cameraVideo = ref(null)
const isDetecting = ref(false)
const detectionResult = ref(null)
const resultImageMeta = ref({})
let cameraStream = null

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}

const showHelp = () => {
  alert('AI智能定损使用说明：\n1. 上传车辆破损照片\n2. 系统会自动检测损伤\n3. 查看详细定损报告')
}

const openUploadOptions = () => {
  showUploadModal.value = true
}

const closeUploadModal = () => {
  showUploadModal.value = false
}

// 选择「拍照」后：只打开相机预览，不立即拍照
const openCamera = async () => {
  showUploadModal.value = false
  try {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('您的浏览器不支持相机功能')
    }
    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: 'environment',
        width: { ideal: 1280 },
        height: { ideal: 720 }
      }
    })
    showCameraModal.value = true
    await nextTick()
    if (cameraVideo.value) {
      cameraVideo.value.srcObject = cameraStream
    }
  } catch (error) {
    console.error('相机访问失败:', error)
    alert(`相机访问失败: ${error.message}`)
  }
}

const closeCamera = () => {
  if (cameraStream) {
    cameraStream.getTracks().forEach(track => track.stop())
    cameraStream = null
  }
  showCameraModal.value = false
}

const onResultImageLoad = (imageId, event) => {
  const el = event?.target
  if (!el) return
  resultImageMeta.value = {
    ...resultImageMeta.value,
    [imageId]: {
      naturalWidth: el.naturalWidth,
      naturalHeight: el.naturalHeight
    }
  }
}

// 用户在预览界面点击「拍照」时才截取
const capturePhoto = () => {
  if (!cameraVideo.value || !cameraVideo.value.videoWidth) return
  const canvas = document.createElement('canvas')
  canvas.width = cameraVideo.value.videoWidth
  canvas.height = cameraVideo.value.videoHeight
  const ctx = canvas.getContext('2d')
  ctx.drawImage(cameraVideo.value, 0, 0, canvas.width, canvas.height)
  const imageUrl = canvas.toDataURL('image/jpeg')
  uploadedImages.value.push(imageUrl)
  // 拍照后自动关闭相机
  closeCamera()
}

const chooseFromAlbum = () => {
  // 触发文件选择
  if (fileInput.value) {
    fileInput.value.click()
  }
  showUploadModal.value = false
}

const handleFileSelect = (event) => {
  const files = event.target.files
  if (!files || files.length === 0) return
  
  // 处理选择的文件
  Array.from(files).forEach(file => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        uploadedImages.value.push(e.target.result)
      }
      reader.readAsDataURL(file)
    }
  })
  
  // 清空文件输入，以便可以重复选择相同的文件
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const removeImage = (index) => {
  uploadedImages.value.splice(index, 1)
}

const startDetection = async () => {
  if (uploadedImages.value.length === 0) return
  if (isDetecting.value) return
  
  try {
    isDetecting.value = true
    
    // 准备FormData
    const formData = new FormData()
    for (let index = 0; index < uploadedImages.value.length; index++) {
      const imageData = uploadedImages.value[index]
      // 将base64转换为blob
      const response = await fetch(imageData)
      const blob = await response.blob()
      formData.append('files', blob, `image_${index}.jpg`)
    }
    
    // 调用后端检测API
    const result = await detectionApi.detect(formData)
    
    // 轮询获取检测结果
    const detectionData = await detectionApi.getDetectionResult(result.taskId, {
      timeout: 180000,
      onProgress: (progress) => {
        console.log(`检测进度: ${progress}%`)
      }
    })
    
    // 规范化图片URL：后端可能返回相对路径（如 media/assessment_x/img_0.jpg）
    const normalized = {
      ...detectionData,
      images: (detectionData?.images || []).map(img => {
        const image_url = normalizeMediaUrl(img.image_url)
        const annotated = img.thumb_url ? normalizeMediaUrl(img.thumb_url) : null
        return {
          ...img,
          image_url,
          annotated_image_url: annotated
        }
      })
    }

    // Store results in detection store
    detectionStore.detectionResult = normalized
    detectionStore.carBrand = detectionData?.brand || ''
    detectionStore.carBrandConfidence = detectionData?.brand_confidence || 0
    
    detectionResult.value = normalized
    showResult.value = true
    
  } catch (error) {
    console.error('检测失败:', error)
    const detail =
      error?.response?.data?.detail ||
      error?.response?.data?.message ||
      error?.message ||
      '检测失败，请重试'
    alert(detail)
  } finally {
    isDetecting.value = false
  }
}

const viewReport = async () => {
  if (detectionResult.value) {
    try {
      // 先调用豆包API进行分析
      console.log('开始调用豆包API进行分析...')
      await detectionStore.analyzeWithLLM(detectionResult.value.taskId)
      console.log('豆包分析完成，跳转到详情页面')
      // 分析完成后再跳转到详情页面
      router.push(`/damage-detail/${detectionResult.value.taskId}`)
    } catch (err) {
      console.error('豆包分析失败:', err)
      alert('AI分析失败: ' + (err.message || '请稍后重试'))
      // 即使分析失败，也跳转到详情页面，让用户看到基本检测信息
      router.push(`/damage-detail/${detectionResult.value.taskId}`)
    }
  } else {
    alert('暂无检测结果')
  }
}

const preRepairAnalysis = async () => {
  if (detectionResult.value) {
    try {
      // 调用预修车分析API
      const analysis = await repairApi.getPriorityAnalysis(detectionResult.value.assessmentId)
      // 跳转到预修车分析页面并传递数据
      router.push({
        path: '/pre-repair',
        query: { 
          assessmentId: detectionResult.value.assessmentId,
          taskId: detectionResult.value.taskId 
        }
      })
    } catch (error) {
      console.error('获取预修车分析失败:', error)
      alert('获取预修车分析失败，请重试')
    }
  } else {
    alert('暂无检测结果')
  }
}

const normalizeMediaUrl = (url) => {
  if (!url) return url
  const raw = String(url)
  if (
    raw.startsWith('http://') ||
    raw.startsWith('https://') ||
    raw.startsWith('data:') ||
    raw.startsWith('blob:')
  ) {
    return raw
  }

  const path = raw.replace(/\\/g, '/').replace(/^\/+/, '')
  // 后端挂载了 /media
  if (path.startsWith('media/')) {
    return `/media/${path.slice('media/'.length)}`
  }
  if (path.startsWith('assessment_')) {
    return `/media/${path}`
  }
  return `/${path}`
}

const damageTypeToText = (damageType) => {
  const t = String(damageType || '').toUpperCase()
  console.log('damageTypeToText called with:', damageType, '->', t)
  const map = {
    PAINT: '车漆',
    PAINT_DAMAGE: '车漆',
    GLASS: '玻璃',
    GLASS_DAMAGE: '玻璃',
    METAL: '钣金',
    METAL_DAMAGE: '钣金',
    SCRATCH: '车漆',
    DENT: '钣金',
    CRACK: '玻璃',
    BROKEN: '玻璃',
    CORROSION: '钣金'
  }
  const result = map[t] ? `${map[t]}损伤` : '未知损伤'
  console.log('damageTypeToText result:', result)
  return result
}

const severityToText = (severity) => {
  const s = String(severity || '').toUpperCase()
  if (['LOW', 'MINOR'].includes(s)) return '轻'
  if (['MEDIUM', 'MODERATE'].includes(s)) return '中'
  if (['HIGH', 'SEVERE', 'CRITICAL'].includes(s)) return '重'
  return '中'
}

const getDamageClass = (damageType) => {
  const t = String(damageType || '').toUpperCase()
  if (t.includes('GLASS') || ['CRACK', 'BROKEN'].includes(t)) return 'glass-damage'
  if (t.includes('METAL') || ['DENT', 'CORROSION'].includes(t)) return 'metal-damage'
  return 'paint-damage'
}

const getRegionsByImage = (imageId) => {
  if (!detectionResult.value?.regions?.length) return []
  return detectionResult.value.regions.filter(r => r.image_id === imageId)
}

const getRegionStyle = (imageId, bbox) => {
  if (!bbox) return {}
  const parts = String(bbox)
    .split(',')
    .map(v => Number(v))
    .filter(v => Number.isFinite(v))
  if (parts.length < 4) return {}

  const [x1, y1, x2, y2] = parts
  const w = Math.max(0, x2 - x1)
  const h = Math.max(0, y2 - y1)

  const meta = resultImageMeta.value?.[imageId]

  // 后端 bbox 为像素坐标时，转换成百分比以适配响应式缩放
  if (meta?.naturalWidth && meta?.naturalHeight && x2 > 1 && y2 > 1) {
    return {
      left: `${(x1 / meta.naturalWidth) * 100}%`,
      top: `${(y1 / meta.naturalHeight) * 100}%`,
      width: `${(w / meta.naturalWidth) * 100}%`,
      height: `${(h / meta.naturalHeight) * 100}%`
    }
  }

  // fallback：如果是 0-1 归一化坐标则直接用百分比
  const toCss = (n) => {
    if (n >= 0 && n <= 1) return `${n * 100}%`
    return `${n}px`
  }

  return {
    left: toCss(x1),
    top: toCss(y1),
    width: toCss(w),
    height: toCss(h)
  }
}

const summaryText = computed(() => {
  const regions = detectionResult.value?.regions || []
  if (!regions.length) return ''

  const groups = new Map()
  for (const r of regions) {
    const key = `${damageTypeToText(r.damage_type)}-${severityToText(r.severity_level)}`
    groups.set(key, (groups.get(key) || 0) + 1)
  }

  const parts = Array.from(groups.entries()).map(([k, v]) => {
    const [dt, sv] = k.split('-')
    return `${v}处${dt}（${sv}）`
  })
  return `检测到 ${regions.length} 处损伤：${parts.join('、')}`
})

const totalBudgetText = computed(() => {
  const budget =
    detectionResult.value?.budget?.total_budget ??
    detectionResult.value?.total_budget ??
    detectionResult.value?.assessment?.total_budget
  if (budget === undefined || budget === null) return '0'
  const num = Number(budget)
  if (!Number.isFinite(num)) return '0'
  return num.toLocaleString('zh-CN')
})

// 过滤掉image_url中的base64数据
const filteredImageData = computed(() => {
  if (!detectionResult.value) return null
  
  const result = { ...detectionResult.value }
  
  // 处理images数组，过滤掉image_url中的base64数据
  if (result.images && Array.isArray(result.images)) {
    result.images = result.images.map(img => {
      const filteredImg = { ...img }
      if (filteredImg.image_url && filteredImg.image_url.startsWith('data:image/')) {
        filteredImg.image_url = '[Base64图片数据已隐藏]'
      }
      if (filteredImg.annotated_image_url && filteredImg.annotated_image_url.startsWith('data:image/')) {
        filteredImg.annotated_image_url = '[Base64图片数据已隐藏]'
      }
      return filteredImg
    })
  }
  
  return result
})

// 提取损伤部位
const getDamageParts = computed(() => {
  if (!detectionResult.value?.regions) return []
  const parts = new Set()
  detectionResult.value.regions.forEach(region => {
    if (region.part_code) {
      // 将英文转换为中文
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
      const part = partMap[region.part_code] || region.part_code
      parts.add(part)
    }
  })
  return Array.from(parts)
})

// 提取损伤类型
const getDamageTypes = computed(() => {
  if (!detectionResult.value?.regions) return []
  const types = new Set()
  detectionResult.value.regions.forEach(region => {
    if (region.damage_type) {
      types.add(damageTypeToText(region.damage_type))
    }
  })
  return Array.from(types)
})

// 提取严重程度
const getSeverityLevels = computed(() => {
  if (!detectionResult.value?.regions) return []
  const levels = new Set()
  detectionResult.value.regions.forEach(region => {
    if (region.severity_level) {
      levels.add(severityToText(region.severity_level))
    }
  })
  return Array.from(levels)
})

</script>

<style scoped>
.wechat-ai-detection {
  min-height: 100vh;
  background-color: #f5f7fa;
  position: relative;
  overflow-x: hidden;
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
}

.nav-left {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  color: white;
}

.nav-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.nav-icon {
  width: 44px;
  height: 44px;
  color: white;
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

/* 主内容区 */
.main-content {
  padding-top: 44px;
  min-height: calc(100vh - 44px);
  padding: 64px 16px 0px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 上传卡片 */
.upload-card {
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.upload-card :deep(.el-card__body) {
  padding: 40px 20px;
}

.result-card :deep(.el-card) {
  --el-card-padding: 8px;
}

.upload-content {
  text-align: center;
}

.upload-icon {
  color: #4096EE;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.upload-subtext {
  font-size: 14px;
  color: #606266;
  margin-bottom: 12px;
}

.upload-hint {
  font-size: 12px;
  color: #909399;
}

/* 缩略图区域 */
.thumbnail-area {
  margin-bottom: 16px;
}

.thumbnail-grid {
  width: 100%;
}

.thumbnail-item {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  aspect-ratio: 1;
}

.thumbnail-img {
  width: 100%;
  height: 100%;
}

.thumbnail-remove {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.thumbnail-remove:hover {
  background: rgba(245, 108, 108, 0.8);
}

/* 检测按钮 */
.detection-button {
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
}

/* 结果区域 */
.result-area {
  flex: 1;
  padding: 0px;
}

.result-area :deep(.el-card__body) {
  padding: 0px;
}

.result-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.result-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin: -16px;
  padding: 10px;
  border-radius: 16px 16px 0 0;
}

.result-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

/* 检测结果顶部区域 */
.result-top-section {
  padding: 0px;
  text-align: center;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 0px;
}

.data-overview {
  display: flex;
  justify-content: center;
  gap: 32px;
}

.overview-item {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.overview-number {
  font-size: 28px;
  font-weight: 700;
  color: #4096ee;
  display: flex;
  align-items: center;
  justify-content: center;
}

.overview-label {
  font-size: 14px;
  color: #909399;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
}

/* 节标题 */
.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 10px 0;
  padding-left: 8px;
  border-left: 3px solid #4096ee;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 车辆信息区域 */
.vehicle-info-section {
  margin-bottom: 16px;
}

.vehicle-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.vehicle-card {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.3s ease;
}

.vehicle-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.card-icon {
  width: 40px;
  height: 40px;
  background: #4096ee;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.card-title {
  font-size: 12px;
  color: #909399;
  margin-bottom: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-subtitle {
  font-size: 12px;
  color: #606266;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 检测结果图片区域 */
.detection-images-section {
  margin-bottom: 16px;
}

.result-images {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-image-wrap {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  max-height: 350px;
  z-index: 1;
}

.result-image-wrap:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
}

.result-image {
  width: 100%;
  height: 300px;
  max-height: 350px;
  border-radius: 12px;
  object-fit: contain;
  background: #f8f9fa;
}

/* 损伤分析区域 */
.damage-analysis-section {
  margin-bottom: 16px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.analysis-card {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}

.analysis-card:hover {
  background: #e2e8f0;
  border-left-color: #4096ee;
  transform: translateX(4px);
}

.analysis-icon {
  width: 36px;
  height: 36px;
  background: #4096ee;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
}

.analysis-content {
  flex: 1;
}

.analysis-label {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.analysis-value {
  font-size: 16px;
  color: #4096ee;
  font-weight: 600;
}

/* 操作按钮 */
.result-buttons {
  margin-top: 0px;
  padding: 0px 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
}

.result-buttons .el-button {
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  transition: all 0.3s ease;
  flex: 1;
  min-width: 0;
}

.result-button {
  flex: 1;
  min-width: 0;
}

.result-buttons .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

/* 检测框样式 */
.detection-box {
  position: absolute;
  border: 2px solid;
  border-radius: 4px;
  pointer-events: none;
}

.glass-damage {
  border-color: #409EFF;
  background: rgba(64, 158, 255, 0.1);
}

.metal-damage {
  border-color: #E6A23C;
  background: rgba(230, 162, 60, 0.1);
}

.paint-damage {
  border-color: #67C23A;
  background: rgba(103, 194, 58, 0.1);
}

.box-label {
  position: absolute;
  top: -24px;
  left: 0;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
}

/* 响应式设计 */
@media (max-width: 375px) {
  .main-content {
    padding: 60px 12px 20px;
    gap: 12px;
    padding: 16px;
    gap: 16px;
  }
  
  .upload-card {
    padding: 24px;
  }
  
  .upload-icon {
    width: 64px;
    height: 64px;
  }
  
  .upload-icon svg {
    width: 32px;
    height: 32px;
  }
  
  .upload-text {
    font-size: 15px;
  }
  
  .upload-subtext {
    font-size: 13px;
  }
  
  .upload-hint {
    font-size: 11px;
  }
  
  .detection-button {
    padding: 14px;
    font-size: 15px;
  }
  
  /* 优化后的UI响应式 */
  .data-overview {
    gap: 20px;
  }
  
  .overview-number {
    font-size: 24px;
  }
  
  .overview-label {
    font-size: 12px;
  }
  
  .vehicle-cards {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .vehicle-card {
    padding: 12px;
  }
  
  .card-icon {
    width: 36px;
    height: 36px;
    font-size: 16px;
  }
  
  .card-value {
    font-size: 14px;
  }
  
  .result-image {
    max-height: 250px;
  }
  
  .analysis-card {
    padding: 12px;
  }
  
  .analysis-icon {
    width: 32px;
    height: 32px;
    font-size: 14px;
  }
  
  .analysis-value {
    font-size: 13px;
  }
  
  .result-buttons .el-button {
    height: 44px;
    font-size: 14px;
  }
}

/* 弹窗样式 */
.upload-dialog :deep(.el-dialog) {
  border-radius: 12px;
}

.upload-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.modal-options {
  margin: 20px 0;
}

.modal-option {
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-option :deep(.el-card__body) {
  padding: 20px;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.modal-option:hover {
  transform: translateY(-2px);
}

.option-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.option-icon {
  color: #4096EE;
}

.option-text {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.camera-dialog :deep(.el-dialog) {
  border-radius: 12px;
}

.camera-preview-wrap {
  position: relative;
  width: 100%;
  max-height: 400px;
  border-radius: 8px;
  overflow: hidden;
  background: #000;
}

.camera-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 响应式设计 */
@media (max-width: 375px) {
  .main-content {
    padding: 60px 12px 20px;
    gap: 12px;
    padding: 16px;
    gap: 16px;
  }
  
  .upload-card {
    padding: 24px;
  }
  
  .upload-icon {
    width: 64px;
    height: 64px;
  }
  
  .upload-icon svg {
    width: 32px;
    height: 32px;
  }
  
  .upload-text {
    font-size: 15px;
  }
  
  .upload-subtext {
    font-size: 13px;
  }
  
  .upload-hint {
    font-size: 11px;
  }
  
  .detection-button {
    padding: 14px;
    font-size: 15px;
  }
  
  .result-area {
    padding: 20px;
  }
  
  .result-header h3 {
    font-size: 16px;
  }
  
  .result-button {
    padding: 10px;
    font-size: 13px;
  }
}
</style>
