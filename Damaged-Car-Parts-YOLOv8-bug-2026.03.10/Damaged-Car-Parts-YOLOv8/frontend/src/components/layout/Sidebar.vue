<template>
  <aside class="sidebar">
    <div class="sidebar-content">
      <div class="sidebar-section">
        <h3 class="section-title">功能导航</h3>
        <ul class="nav-list">
          <li class="nav-item">
            <router-link to="/detection" class="nav-link">
              <span class="nav-icon">📷</span>
              <span class="nav-text">损伤检测</span>
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/history" class="nav-link">
              <span class="nav-icon">📋</span>
              <span class="nav-text">历史记录</span>
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/about" class="nav-link">
              <span class="nav-icon">ℹ️</span>
              <span class="nav-text">关于系统</span>
            </router-link>
          </li>
        </ul>
      </div>
      <div class="sidebar-section">
        <h3 class="section-title">快速操作</h3>
        <ul class="nav-list">
          <li class="nav-item">
            <a href="#" class="nav-link" @click.prevent="handleQuickAction('upload')">
              <span class="nav-icon">📤</span>
              <span class="nav-text">上传图片</span>
            </a>
          </li>
          <li class="nav-item">
            <a href="#" class="nav-link" @click.prevent="handleQuickAction('export')">
              <span class="nav-icon">📄</span>
              <span class="nav-text">导出报告</span>
            </a>
          </li>
        </ul>
      </div>
    </div>
  </aside>
</template>

<script setup>
const emit = defineEmits(['quickAction'])

const handleQuickAction = (action) => {
  emit('quickAction', action)
}
</script>

<style scoped>
.sidebar {
  background-color: white;
  border-right: 1px solid #ebeef5;
  width: 200px;
  height: calc(100vh - 60px);
  position: fixed;
  top: 60px;
  left: 0;
  overflow-y: auto;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
}

.sidebar-content {
  padding: 20px;
}

.sidebar-section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #909399;
  margin: 0 0 15px 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin-bottom: 8px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  text-decoration: none;
  color: #606266;
  border-radius: 6px;
  transition: all 0.3s ease;
  font-size: 14px;
}

.nav-link:hover {
  background-color: #ecf5ff;
  color: #409eff;
}

.nav-link.router-link-active {
  background-color: #ecf5ff;
  color: #409eff;
  font-weight: 500;
}

.nav-icon {
  font-size: 16px;
  width: 20px;
  text-align: center;
}
</style>