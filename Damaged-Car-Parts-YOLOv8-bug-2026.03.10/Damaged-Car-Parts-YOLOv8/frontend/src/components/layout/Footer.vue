<template>
  <footer class="footer">
    <div class="footer-container">
      <div class="footer-content">
        <div class="footer-section">
          <h3 class="footer-title">车辆损伤检测系统</h3>
          <p class="footer-description">基于人工智能技术的智能定损系统</p>
        </div>
        <div class="footer-section">
          <h4 class="footer-subtitle">快速链接</h4>
          <ul class="footer-links">
            <li><router-link to="/">首页</router-link></li>
            <li><router-link to="/detection">检测</router-link></li>
            <li><router-link to="/history">历史</router-link></li>
            <li><router-link to="/about">关于</router-link></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p class="footer-copyright">© 2024 车辆损伤检测系统. 保留所有权利.</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
// Footer 组件
</script>

<style scoped>
.footer {
  background-color: #303133;
  color: white;
  padding: 40px 0;
  margin-top: 40px;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 40px;
  margin-bottom: 40px;
}

.footer-section {
  flex: 1;
  min-width: 200px;
}

.footer-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 15px 0;
  color: #409eff;
}

.footer-description {
  font-size: 14px;
  color: #c0c4cc;
  margin: 0;
}

.footer-subtitle {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 15px 0;
  color: #e4e7ed;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: 10px;
}

.footer-links a {
  color: #c0c4cc;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.3s ease;
}

.footer-links a:hover {
  color: #409eff;
}

.footer-contact {
  font-size: 14px;
  color: #c0c4cc;
  margin: 0 0 10px 0;
}

.footer-bottom {
  border-top: 1px solid #4e4e4e;
  padding-top: 20px;
  text-align: center;
}

.footer-copyright {
  font-size: 12px;
  color: #909399;
  margin: 0;
}
</style>