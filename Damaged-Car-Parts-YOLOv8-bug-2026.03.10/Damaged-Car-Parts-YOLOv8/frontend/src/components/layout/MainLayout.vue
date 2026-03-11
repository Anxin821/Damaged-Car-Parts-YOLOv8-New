<template>
  <div class="main-layout">
    <Header />
    <div class="layout-content">
      <Sidebar @quick-action="handleQuickAction" />
      <main class="main-content">
        <slot></slot>
      </main>
    </div>
  </div>
</template>

<script setup>
import Header from './Header.vue'
import Sidebar from './Sidebar.vue'

const handleQuickAction = (action) => {
  console.log('Quick action:', action)
  // 这里可以添加快速操作的处理逻辑
}
</script>

<style scoped>
.main-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.layout-content {
  display: flex;
  flex: 1;
  margin-top: 0;
}

.main-content {
  flex: 1;
  margin-left: 200px;
  padding: 10px 0;
  background-color: #f5f5f5;
  min-height: 100%;
  height: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    display: none;
  }
  
  .main-content {
    margin-left: 0;
    padding: 16px;
  }
}

/* 苹果14Pro max适配 */
@media (max-width: 428px) {
  .main-content {
    padding: 10px 0;
  }
}
</style>