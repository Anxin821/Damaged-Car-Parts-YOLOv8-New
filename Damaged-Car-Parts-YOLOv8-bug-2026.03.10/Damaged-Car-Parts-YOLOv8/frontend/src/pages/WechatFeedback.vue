<template>
  <div class="wechat-feedback">
    <!-- 导航栏 -->
    <div class="nav-bar">
      <el-button :icon="ArrowLeft" @click="goBack" circle text />
      <div class="nav-title">意见与反馈</div>
      <el-button :icon="HomeFilled" @click="goHome" circle text />
    </div>

    <div class="content">
      <div class="card">
        <div class="field">
          <div class="label">联系方式（选填）</div>
          <el-input 
            v-model="contact" 
            placeholder="手机号 / 微信 / 邮箱"
            clearable
          />
        </div>

        <div class="field">
          <div class="label">反馈类型</div>
          <el-radio-group v-model="category">
            <el-radio value="GENERAL">产品建议</el-radio>
            <el-radio value="BUG">功能异常</el-radio>
            <el-radio value="UX">体验/交互</el-radio>
          </el-radio-group>
        </div>

        <div class="field">
          <div class="label">反馈内容</div>
          <el-input
            v-model="content"
            type="textarea"
            :rows="6"
            maxlength="1000"
            show-word-limit
            placeholder="请描述你的问题/建议（最多1000字）"
            resize="none"
          />
        </div>

        <el-button 
          type="primary" 
          :loading="submitting"
          :disabled="submitting || content.trim().length === 0" 
          @click="submit"
          class="submit"
        >
          {{ submitting ? '提交中...' : '提交反馈' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { feedbackApi } from '../api'
import {
  ArrowLeft,
  HomeFilled
} from '@element-plus/icons-vue'

const router = useRouter()

const contact = ref('')
const category = ref('GENERAL')
const content = ref('')
const submitting = ref(false)

const goBack = () => router.back()

const goHome = () => {
  router.push('/')
}

const submit = async () => {
  if (submitting.value) return
  if (!content.value.trim()) return

  submitting.value = true
  try {
    await feedbackApi.create({
      contact: contact.value || null,
      category: category.value,
      content: content.value.trim()
    })

    alert('提交成功，感谢你的反馈！')
    contact.value = ''
    category.value = 'GENERAL'
    content.value = ''
    router.back()
  } catch (e) {
    console.error(e)
    alert('提交失败，请稍后再试')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
/* 整体布局 */
.wechat-feedback {
  min-height: 100vh;
  background: #f5f7fa;
}

/* 导航栏 */
.nav-bar {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.nav-title {
  flex: 1;
  text-align: center;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

/* 主内容区 */
.content {
  padding: 16px;
  padding-top: 60px;
}

.card {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.field + .field {
  margin-top: 14px;
}

.label {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.submit {
  width: 100%;
  margin-top: 16px;
}

/* Element Plus 组件样式调整 */
:deep(.el-input__wrapper) {
  border-radius: 12px;
}

:deep(.el-textarea__inner) {
  border-radius: 12px;
  min-height: 140px;
}

:deep(.el-radio-group) {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

:deep(.el-radio) {
  margin-right: 0;
}

:deep(.el-radio__label) {
  padding: 8px 13px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fff;
  transition: all 0.2s ease;
}

:deep(.el-radio__input.is-checked + .el-radio__label) {
  border-color: #4096ee;
  background: rgba(64, 150, 238, 0.1);
  color: #4096ee;
}

:deep(.el-radio__input:not(.is-disabled) + .el-radio__label:hover) {
  border-color: #4096ee;
  background: rgba(64, 150, 238, 0.04);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-bar {
    justify-content: center;
  }
  
  .content {
    padding: 16px 12px;
    padding-top: 60px;
  }
}
</style>

