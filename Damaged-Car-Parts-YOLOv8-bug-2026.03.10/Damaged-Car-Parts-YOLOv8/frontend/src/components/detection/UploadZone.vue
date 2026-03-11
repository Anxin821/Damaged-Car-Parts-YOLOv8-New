<template>
  <div class="upload-zone" :class="{ 'dragover': isDragover }" @dragover="handleDragOver" @dragleave="handleDragLeave" @drop="handleDrop" @click="fileInput.click()">
    <input
      type="file"
      ref="fileInput"
      class="file-input"
      accept="image/*"
      @change="handleFileChange"
    />
    <div class="upload-content">
      <div class="upload-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="7 10 12 15 17 10"></polyline>
          <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
      </div>
      <h3 class="upload-title">点击或拖拽图片到此处上传</h3>
      <p class="upload-hint">支持 JPG、PNG 格式，最大 10MB</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const fileInput = ref(null)
const isDragover = ref(false)

const emit = defineEmits(['fileUpload'])

const handleFileChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    emit('fileUpload', file)
  }
}

const handleDragOver = (e) => {
  e.preventDefault()
  isDragover.value = true
}

const handleDragLeave = () => {
  isDragover.value = false
}

const handleDrop = (e) => {
  e.preventDefault()
  isDragover.value = false
  const file = e.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    emit('fileUpload', file)
  }
}
</script>

<style scoped>
.upload-zone {
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #fafafa;
}

.upload-zone:hover {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.upload-zone.dragover {
  border-color: #67c23a;
  background-color: #f0f9eb;
}

.file-input {
  display: none;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.upload-icon {
  color: #909399;
  transition: color 0.3s ease;
}

.upload-zone:hover .upload-icon {
  color: #409eff;
}

.upload-title {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.upload-hint {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .upload-zone {
    padding: 32px;
  }
  
  .upload-title {
    font-size: 18px;
  }
  
  .upload-hint {
    font-size: 16px;
  }
}

/* 苹果14Pro max适配 */
@media (max-width: 428px) {
  .upload-zone {
    padding: 24px;
    height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .upload-content {
    gap: 12px;
  }
  
  .upload-icon svg {
    width: 40px;
    height: 40px;
  }
  
  .upload-title {
    font-size: 18px;
    text-align: center;
  }
  
  .upload-hint {
    font-size: 14px;
    text-align: center;
  }
}
</style>