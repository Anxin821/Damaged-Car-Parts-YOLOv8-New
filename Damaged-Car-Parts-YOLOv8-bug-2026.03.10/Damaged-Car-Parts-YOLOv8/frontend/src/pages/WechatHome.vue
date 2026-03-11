<template>
  <div class="wechat-home">
    <!-- 系统标题 -->
    <div class="system-header">
      <div class="system-title">基于YOLO算法的车辆定损系统</div>
    </div>
    
    <!-- 顶部背景区域 -->
    <div class="top-banner">
      <div class="banner-content">
        <!-- 插画区域 -->
        <div class="illustration">
          <svg width="200" height="150" viewBox="0 0 200 150" fill="none">
            <!-- 背景装饰圆圈 -->
            <circle cx="100" cy="75" r="65" fill="rgba(255,255,255,0.1)"/>
            <circle cx="100" cy="75" r="50" fill="rgba(255,255,255,0.15)"/>
            
            <!-- 现代化车辆 -->
            <g transform="translate(50, 60)">
              <!-- 车身主体 -->
              <path d="M10 25 Q10 15 20 15 L70 15 Q80 15 85 20 L90 30 Q90 35 85 35 L15 35 Q10 35 10 30 Z" 
                    fill="rgba(255,255,255,0.9)" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>
              <!-- 车顶 -->
              <path d="M25 15 L35 5 L55 5 L65 15 Z" 
                    fill="rgba(255,255,255,0.85)" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>
              <!-- 车窗 -->
              <path d="M30 12 L38 8 L52 8 L60 12 Z" 
                    fill="rgba(64, 150, 238, 0.3)" stroke="rgba(255,255,255,0.5)" stroke-width="1"/>
              <!-- 车轮 -->
              <circle cx="25" cy="38" r="6" fill="rgba(100,100,100,0.8)"/>
              <circle cx="25" cy="38" r="3" fill="rgba(255,255,255,0.6)"/>
              <circle cx="75" cy="38" r="6" fill="rgba(100,100,100,0.8)"/>
              <circle cx="75" cy="38" r="3" fill="rgba(255,255,255,0.6)"/>
              <!-- 车灯 -->
              <circle cx="88" cy="25" r="3" fill="rgba(255,223,0,0.8)"/>
              <circle cx="12" cy="25" r="2" fill="rgba(255,100,100,0.6)"/>
            </g>
            
            <!-- AI检测扫描效果 -->
            <g transform="translate(100, 75)">
              <!-- 扫描线 -->
              <line x1="-40" y1="0" x2="40" y2="0" stroke="rgba(64, 150, 238, 0.6)" stroke-width="2">
                <animate attributeName="opacity" values="0;1;0" dur="2s" repeatCount="indefinite"/>
              </line>
              <line x1="0" y1="-30" x2="0" y2="30" stroke="rgba(64, 150, 238, 0.6)" stroke-width="2">
                <animate attributeName="opacity" values="0;1;0" dur="2s" begin="0.5s" repeatCount="indefinite"/>
              </line>
              <!-- 中心点 -->
              <circle cx="0" cy="0" r="4" fill="rgba(64, 150, 238, 0.8)">
                <animate attributeName="r" values="4;6;4" dur="2s" repeatCount="indefinite"/>
              </circle>
            </g>
            
            <!-- 数据点 -->
            <circle cx="40" cy="40" r="2" fill="rgba(102, 211, 168, 0.8)">
              <animate attributeName="opacity" values="0;1;0" dur="3s" repeatCount="indefinite"/>
            </circle>
            <circle cx="160" cy="50" r="2" fill="rgba(102, 211, 168, 0.8)">
              <animate attributeName="opacity" values="0;1;0" dur="3s" begin="1s" repeatCount="indefinite"/>
            </circle>
            <circle cx="150" cy="100" r="2" fill="rgba(102, 211, 168, 0.8)">
              <animate attributeName="opacity" values="0;1;0" dur="3s" begin="2s" repeatCount="indefinite"/>
            </circle>
            
            <!-- 连接线 -->
            <path d="M40 40 Q100 60 160 50" stroke="rgba(102, 211, 168, 0.4)" stroke-width="1" fill="none" stroke-dasharray="2,2">
              <animate attributeName="stroke-dashoffset" values="0;4" dur="2s" repeatCount="indefinite"/>
            </path>
            <path d="M100 75 Q150 85 150 100" stroke="rgba(102, 211, 168, 0.4)" stroke-width="1" fill="none" stroke-dasharray="2,2">
              <animate attributeName="stroke-dashoffset" values="0;4" dur="2s" begin="1s" repeatCount="indefinite"/>
            </path>
          </svg>
        </div>
        
        <!-- 标题区域 -->
        <h1 class="main-title">安心定损<br>1.0 全新升级</h1>
        <p class="sub-title">YOLO-AI 智能检测 | 精准定损 | 预算一键生成</p>
      </div>
    </div>
    
    <!-- 核心功能区 -->
    <div class="feature-section">
      <div class="feature-cards-container">
        <!-- AI 智能定损卡片 -->
        <el-card class="feature-card" shadow="hover" @click="navigateTo('ai')">
          <div class="card-icon ai-icon">
            <el-icon size="24"><Edit /></el-icon>
          </div>
          <h3 class="card-title">AI 智能定损</h3>
          <p class="card-description">上传车辆照片，AI 自动检测损伤</p>
        </el-card>
        
        <!-- 预修车分析卡片 -->
        <el-card class="feature-card" shadow="hover" @click="navigateTo('analysis')">
          <div class="card-icon analysis-icon">
            <el-icon size="24"><TrendCharts /></el-icon>
          </div>
          <h3 class="card-title">预修车分析</h3>
          <p class="card-description">预估维修费用和时间</p>
        </el-card>
        
        <!-- 定损看板卡片 -->
        <el-card class="feature-card" shadow="hover" @click="navigateTo('dashboard')">
          <div class="card-icon dashboard-icon">
            <el-icon size="24"><DataBoard /></el-icon>
          </div>
          <h3 class="card-title">定损看板</h3>
          <p class="card-description">查看历史记录和状态</p>
        </el-card>
      </div>
    </div>
    
    <!-- 底部客服区域 -->
    <div class="bottom-section">
      <el-button 
        class="customer-service" 
        text 
        @click="navigateTo('feedback')"
      >
        <el-icon><ChatDotRound /></el-icon>
        <span>意见与反馈</span>
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import {
  Edit,
  TrendCharts,
  DataBoard,
  ChatDotRound
} from '@element-plus/icons-vue'

const router = useRouter()

const navigateTo = (path) => {
  switch (path) {
    case 'ai':
      router.push('/detection')
      break
    case 'analysis':
      router.push('/pre-repair')
      break
    case 'dashboard':
      router.push('/wechat-dashboard')
      break
    case 'feedback':
      router.push('/feedback')
      break
    default:
      break
  }
}
</script>

<style scoped>
/* 整体布局 */
.wechat-home {
  min-height: 100vh;
  background-color: #f5f7fa;
  position: relative;
  overflow-x: hidden;
}

/* 系统标题 */
.system-header {
  background: linear-gradient(90deg, #4096EE, #54C5F8, #66D3A8);
  padding: 12px 20px;
  text-align: center;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.system-title {
  font-size: 21px;
  font-weight: 600;
  color: white;
  margin: 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* 顶部背景区域 */
.top-banner {
  background: linear-gradient(135deg, #4096EE, #54C5F8, #66D3A8);
  height: 35vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.banner-content {
  text-align: center;
  z-index: 1;
  padding: 0 20px;
}

/* 插画区域 */
.illustration {
  margin-bottom: 32px;
  display: flex;
  justify-content: center;
  transform: translateY(-10px);
}

/* 标题样式 */
.main-title {
  font-size: 28px;
  font-weight: 700;
  color: white;
  margin: -50px 0 8px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

@media (min-width: 769px) {
  .top-banner {
    height: 45vh;
    min-height: 260px;
    padding: 60px 0 40px;
    box-sizing: border-box;
  }

  .banner-content {
    transform: translateY(0px);
  }

  .main-title {
    margin: -44px 0 8px 0;
  }
}

.sub-title {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* 核心功能区 */
.feature-section {
  padding: 0 20px;
  margin-top: 20px;
  margin-bottom: 30px;
  padding-top: 5px;
}

.feature-cards-container {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 10px;
  -webkit-overflow-scrolling: touch;
}

/* Element Plus 卡片样式调整 */
:deep(.feature-card) {
  flex: 1;
  min-width: 100px;
  text-align: center;
  cursor: pointer;
  border-radius: 16px;
  border: 1px solid #f0f0f0;
}

:deep(.feature-card:hover) {
  transform: translateY(-2px);
}

/* 卡片图标 */
.card-icon {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: white;
  font-size: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.ai-icon {
  background: linear-gradient(135deg, #4096EE, #54C5F8);
}

.analysis-icon {
  background: linear-gradient(135deg, #54C5F8, #66D3A8);
}

.dashboard-icon {
  background: linear-gradient(135deg, #66D3A8, #4096EE);
}

/* 卡片标题和描述 */
.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.card-description {
  font-size: 14px;
  color: #909399;
  margin: 0;
  line-height: 1.4;
}

/* 底部客服区域 */
.bottom-section {
  background-color: #f5f7fa;
  padding: 0px;
  border-top: 1px solid #e4e7ed;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 16px;
}

/* Element Plus 按钮样式调整 */
:deep(.customer-service) {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #4096EE;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.3s ease;
  width: 100%;
}

:deep(.customer-service:hover) {
  color: #66D3A8;
}

/* 响应式设计 - 375*812 手机竖屏 */
@media (width: 375px) and (height: 812px) {
  .system-header {
    padding: 10px 16px;
  }
  
  .system-title {
    font-size: 15px;
  }
  
  .top-banner {
    height: calc(812px * 0.35);
  }

  .banner-content {
    transform: translateY(-60px);
  }
  
  .feature-section {
    height: calc(812px * 0.5);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  
  .bottom-section {
    height: calc(812px * 0.15);
    display: flex;
    align-items: center;
  }
  
  .main-title {
    font-size: 24px;
  }
  
  .sub-title {
    font-size: 12px;
  }
  
  .card-title {
    font-size: 16px;
  }
  
  .card-description {
    font-size: 13px;
  }
}

/* 通用响应式设计 */
@media (max-width: 768px) {
  .system-header {
    padding: 10px 16px;
  }
  
  .system-title {
    font-size: 18px;
  }
  
  .top-banner {
    height: auto;
    align-items: center;
    justify-content: center;
    padding: 56px 0 16px;
    box-sizing: border-box;
  }

  .banner-content {
    transform: none;
  }
  
  .main-title {
    font-size: 30px;
  }
  
  .sub-title {
    font-size: 15px;
  }
  
  .feature-section {
    padding: 0;
  }
  
  .card-icon {
    width: 60px;
    height: 60px;
  }
  
  .card-title {
    font-size: 16px;
  }
  
  .card-description {
    font-size: 13px;
  }
  
  .bottom-section {
    padding: 16px;
  }
}
</style>