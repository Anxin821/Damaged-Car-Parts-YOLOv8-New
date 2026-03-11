<template>
  <div class="result-display">
    <h3 class="result-title">检测结果</h3>
    <div class="result-stats">
      <div class="stat-item">
        <span class="stat-label">损伤数量</span>
        <span class="stat-value">{{ damages.length }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">总维修费用</span>
        <span class="stat-value price">{{ totalCost }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">损伤程度</span>
        <span class="stat-value">{{ damageLevel }}</span>
      </div>
    </div>
    <div class="result-details">
      <h4>损伤详情</h4>
      <div class="damage-list">
        <div
          v-for="(damage, index) in damages"
          :key="index"
          class="damage-item"
        >
          <div class="damage-info">
            <span class="damage-type">{{ damage.type }}</span>
            <span class="damage-location">{{ damage.location }}</span>
          </div>
          <div class="damage-cost">{{ damage.cost }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  damages: {
    type: Array,
    default: () => []
  }
})

const totalCost = computed(() => {
  const sum = props.damages.reduce((acc, damage) => {
    return acc + (parseFloat(damage.cost) || 0)
  }, 0)
  return `¥${sum.toFixed(2)}`
})

const damageLevel = computed(() => {
  if (props.damages.length === 0) return '无损伤'
  if (props.damages.length <= 2) return '轻微损伤'
  if (props.damages.length <= 5) return '中度损伤'
  return '严重损伤'
})
</script>

<style scoped>
.result-display {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.result-title {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.result-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.stat-value {
  display: block;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.stat-value.price {
  color: #f56c6c;
}

.result-details h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.damage-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.damage-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background-color: #fafafa;
  border-radius: 4px;
}

.damage-info {
  display: flex;
  flex-direction: column;
}

.damage-type {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.damage-location {
  font-size: 12px;
  color: #909399;
}

.damage-cost {
  font-size: 14px;
  font-weight: 600;
  color: #f56c6c;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .result-display {
    padding: 16px;
  }
  
  .result-title {
    font-size: 20px;
  }
  
  .stat-value {
    font-size: 18px;
  }
  
  .result-details h4 {
    font-size: 18px;
  }
  
  .damage-type {
    font-size: 16px;
  }
  
  .damage-location {
    font-size: 14px;
  }
  
  .damage-cost {
    font-size: 16px;
  }
}

/* 苹果14Pro max适配 */
@media (max-width: 428px) {
  .result-display {
    padding: 12px;
  }
  
  .result-title {
    font-size: 20px;
    margin-bottom: 16px;
  }
  
  .result-stats {
    flex-direction: column;
    gap: 12px;
    margin-bottom: 16px;
    padding-bottom: 16px;
  }
  
  .stat-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .stat-label {
    display: inline;
    margin-bottom: 0;
  }
  
  .stat-value {
    display: inline;
    font-size: 18px;
  }
  
  .result-details h4 {
    font-size: 18px;
    margin-bottom: 12px;
  }
  
  .damage-item {
    padding: 12px;
  }
  
  .damage-type {
    font-size: 16px;
  }
  
  .damage-location {
    font-size: 14px;
  }
  
  .damage-cost {
    font-size: 16px;
  }
}
</style>