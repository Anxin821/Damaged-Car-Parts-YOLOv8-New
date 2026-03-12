<template>
  <div class="phone-shell">
    <div class="phone-frame">
      <div class="phone-screen">
        <div class="phone-notch" aria-hidden="true">
          <div class="phone-speaker"></div>
          <div class="phone-camera"></div>
        </div>

        <div class="phone-statusbar">
          <div class="status-left">{{ timeText }}</div>
          <div class="status-right" aria-hidden="true">
            <div class="battery-container">
              <div class="battery-text">{{ batteryLevel }}%</div>
              <div class="battery">
                <div class="battery-level" :style="{ width: batteryLevel + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="phone-content" :class="{ 'is-fixed': !scrollable }">
          <slot />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  batteryLevel: {
    type: Number,
    default: null
  },
  scrollable: {
    type: Boolean,
    default: true
  },
  timeFormat: {
    type: String,
    default: 'HH:mm'
  }
})

const now = ref(new Date())
const batteryLevel = ref(props.batteryLevel)
let timerId = null
let batteryWatchId = null

const pad2 = (n) => String(n).padStart(2, '0')

const timeText = computed(() => {
  const d = now.value
  const HH = pad2(d.getHours())
  const mm = pad2(d.getMinutes())

  if (props.timeFormat === 'H:mm') return `${d.getHours()}:${mm}`
  return `${HH}:${mm}`
})

// 获取电池电量
const getBatteryLevel = async () => {
  console.log('开始获取电池电量...')
  if ('getBattery' in navigator) {
    try {
      const battery = await navigator.getBattery()
      batteryLevel.value = Math.round(battery.level * 100)
      console.log('获取到电池电量:', batteryLevel.value + '%')
      
      // 监听电量变化
      const updateBatteryLevel = () => {
        batteryLevel.value = Math.round(battery.level * 100)
        console.log('电池电量更新:', batteryLevel.value + '%')
      }
      
      battery.addEventListener('levelchange', updateBatteryLevel)
      batteryWatchId = () => {
        battery.removeEventListener('levelchange', updateBatteryLevel)
      }
    } catch (error) {
      console.log('无法获取电池电量:', error)
      batteryLevel.value = props.batteryLevel || 76
      console.log('使用默认电量:', batteryLevel.value + '%')
    }
  } else {
    // 浏览器不支持 Battery API
    console.log('浏览器不支持 Battery API')
    batteryLevel.value = props.batteryLevel || 76
    console.log('使用默认电量:', batteryLevel.value + '%')
  }
}

onMounted(() => {
  timerId = window.setInterval(() => {
    now.value = new Date()
  }, 1000)
  
  // 获取电池电量
  getBatteryLevel()
})

onBeforeUnmount(() => {
  if (timerId != null) window.clearInterval(timerId)
  if (batteryWatchId) batteryWatchId()
})
</script>

<style scoped>
.phone-shell {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 18px;
  background: radial-gradient(1200px 600px at 20% 10%, #eef4ff 0%, transparent 60%),
    radial-gradient(1200px 600px at 80% 30%, #ffeef5 0%, transparent 55%),
    #f5f5f5;
}

.phone-frame {
  width: 390px;
  max-width: calc(100vw - 36px);
  height: 844px;
  max-height: calc(100vh - 36px);
  border-radius: 42px;
  background: linear-gradient(180deg, #1a1a1a 0%, #0f0f0f 100%);
  padding: 6px;
  box-shadow: 0 30px 70px rgba(0, 0, 0, 0.25);
  position: relative;
  --phone-safe-top: 36px;
  --phone-safe-bottom: 8px;
}

.phone-frame::before {
  content: '';
  position: absolute;
  inset: 6px;
  border-radius: 36px;
  background: rgba(255, 255, 255, 0.06);
  pointer-events: none;
}

.phone-notch {
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  width: 172px;
  height: 30px;
  border-bottom-left-radius: 16px;
  border-bottom-right-radius: 16px;
  border-top-left-radius: 18px;
  border-top-right-radius: 18px;
  background: #0b0b0b;
  z-index: 6;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.phone-speaker {
  width: 56px;
  height: 6px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.15);
}

.phone-camera {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: radial-gradient(circle at 30% 30%, #6dd5ff 0%, #1a3b5a 40%, #0b0b0b 70%);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.06);
}

.phone-statusbar {
  position: absolute;
  top: 8px;
  left: 0;
  right: 0;
  height: 28px;
  padding: 0 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 5;
  color: rgba(255, 255, 255, 0.92);
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 0.2px;
}

.status-left {
  width: 90px;
}

.status-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.battery-container {
  display: flex;
  align-items: center;
  gap: 4px;
}

.battery {
  width: 24px;
  height: 12px;
  border-radius: 3px;
  border: 2px solid rgba(255, 255, 255, 0.9);
  position: relative;
  overflow: hidden;
}

.battery::after {
  content: '';
  position: absolute;
  right: -4px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 6px;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.9);
}

.battery-level {
  height: 100%;
  background: linear-gradient(90deg, #65f59b 0%, #3ddc84 100%);
}

.battery-text {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  white-space: nowrap;
}

.phone-screen {
  position: absolute;
  inset: 6px;
  border-radius: 36px;
  background: #ffffff;
  overflow: hidden;
  transform: translateZ(0);
}

.phone-screen::before {
  content: '';
  position: absolute;
  top: -1px;
  left: 0;
  right: 0;
  height: calc(var(--phone-safe-top) + 6px);
  background: linear-gradient(135deg, #4096EE, #54C5F8, #66D3A8);
  border-top-left-radius: 36px;
  border-top-right-radius: 36px;
  z-index: 4;
  pointer-events: none;
}

.phone-content {
  position: relative;
  z-index: 2;
  background: #f5f7fa;
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
  padding-top: 0;
  padding-bottom: var(--phone-safe-bottom);
}

.phone-content.is-fixed {
  overflow: hidden;
  overscroll-behavior: none;
}

.phone-content :deep(.wechat-home),
.phone-content :deep(.wechat-ai-detection),
.phone-content :deep(.wechat-dashboard),
.phone-content :deep(.wechat-feedback),
.phone-content :deep(.wechat-pre-repair-analysis),
.phone-content :deep(.wechat-damage-detail) {
  min-height: 100%;
}

.phone-content :deep(.wechat-home) {
  padding-top: calc(44px + var(--phone-safe-top));
  padding-bottom: calc(76px + var(--phone-safe-bottom));
}

.phone-content :deep(.main-content) {
  padding-top: calc(44px + var(--phone-safe-top));
  min-height: auto;
}

.phone-content :deep(.nav-bar),
.phone-content :deep(.system-header) {
  top: var(--phone-safe-top);
}

.phone-content :deep(.wechat-feedback) .content {
  padding-top: calc(60px + var(--phone-safe-top));
}

.phone-content :deep(.bottom-section) {
  bottom: var(--phone-safe-bottom);
}

@media (max-height: 760px) {
  .phone-frame {
    height: 760px;
  }
}
</style>
