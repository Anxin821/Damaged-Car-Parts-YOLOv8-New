<template>
  <div class="wechat-feedback">
    <!-- 导航栏 -->
    <WechatNavBar title="意见与反馈" :showHome="true" />

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
          size="large"
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
import { ElMessage } from 'element-plus'
import { feedbackApi } from '../api'
import WechatNavBar from '../components/common/WechatNavBar.vue'

const router = useRouter()

const contact = ref('')
const category = ref('GENERAL')
const content = ref('')
const submitting = ref(false)

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

    // 使用Element Plus的消息提示，不打断用户
    ElMessage({
      message: '提交成功，感谢你的反馈！',
      type: 'success',
      duration: 3000,
      showClose: true,
      customClass: 'feedback-message-center'
    })
    
    // 清空表单
    contact.value = ''
    category.value = 'GENERAL'
    content.value = ''
    
    // 延迟返回，让用户看到成功提示
    setTimeout(() => {
      router.back()
    }, 1500)
    
  } catch (e) {
    console.error(e)
    ElMessage({
      message: '提交失败，请稍后再试',
      type: 'error',
      duration: 3000,
      showClose: true
    })
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
  margin-top: 20px;
  height: 44px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
}

.submit:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.submit:active {
  transform: translateY(0);
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
  .content {
    padding: 16px 12px;
    padding-top: 60px;
  }
}
</style>

<style>
/* 全局样式：让消息提示居中显示 */
.feedback-message-center {
  position: fixed !important;
  top: 50% !important;
  left: 50% !important;
  transform: translate(-50%, -50%) !important;
  margin: 0 !important;
  z-index: 9999 !important;
}

.feedback-message-center .el-message {
  min-width: 200px;
  padding: 16px 20px;
  border-radius: 12px;
  font-size: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
}
</style>

