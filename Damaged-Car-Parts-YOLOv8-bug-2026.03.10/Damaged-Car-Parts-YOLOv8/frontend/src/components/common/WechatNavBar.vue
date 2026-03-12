<template>
  <el-row class="nav-bar" justify="space-between" align="middle">
    <el-col :span="4" class="nav-left" @click="goBack">
      <el-icon><ArrowLeft /></el-icon>
    </el-col>
    <el-col :span="16" class="nav-title">{{ title }}</el-col>
    <el-col :span="4" class="nav-right">
      <el-icon v-if="showHome" class="nav-icon" @click="goHome"><HomeFilled /></el-icon>
      <slot name="right"></slot>
    </el-col>
  </el-row>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ArrowLeft, HomeFilled } from '@element-plus/icons-vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  showHome: {
    type: Boolean,
    default: true
  }
})

const router = useRouter()

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
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
  cursor: pointer;
}

.nav-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}

.nav-icon {
  width: 44px;
  height: 44px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
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
</style>
