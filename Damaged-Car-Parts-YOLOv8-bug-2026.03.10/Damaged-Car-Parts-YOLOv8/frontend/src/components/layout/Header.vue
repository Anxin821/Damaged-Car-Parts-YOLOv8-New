<template>
  <header class="header">
    <div class="header-container">
      <div class="header-left">
        <nav class="nav">
          <router-link to="/" class="nav-link">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
              <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
          </router-link>
        </nav>
      </div>
      <div class="header-center">
        <div class="logo">
          <h1>基于YOLO算法的车辆定损系统</h1>
        </div>
      </div>
      <div class="header-right">
      </div>
    </div>
  </header>
</template>

<script setup>
// Header 组件
</script>

<style scoped>
.header {
  background-color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  top: 0;
}

.header-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.logo h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #409eff;
  text-align: center;
}

.nav {
  display: flex;
  gap: 20px;
}

.nav-link {
  text-decoration: none;
  color: #606266;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.3s ease;
  padding: 8px 12px;
  border-radius: 4px;
  background-color: transparent !important;
}

.nav-link:hover {
  color: #409eff;
}

.nav-link.router-link-active {
  color: #409eff;
}
</style>