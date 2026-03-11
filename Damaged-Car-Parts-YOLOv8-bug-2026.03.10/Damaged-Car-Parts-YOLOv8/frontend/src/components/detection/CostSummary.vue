<template>
  <div class="cost-summary">
    <h3 class="summary-title">费用汇总</h3>
    <div class="summary-content">
      <div class="cost-item">
        <span class="cost-label">损伤维修费用</span>
        <span class="cost-value">{{ repairCost }}</span>
      </div>
      <div class="cost-item">
        <span class="cost-label">人工费用</span>
        <span class="cost-value">{{ laborCost }}</span>
      </div>
      <div class="cost-item">
        <span class="cost-label">配件费用</span>
        <span class="cost-value">{{ partsCost }}</span>
      </div>
      <div class="cost-item total">
        <span class="cost-label">总计</span>
        <span class="cost-value total-value">{{ totalCost }}</span>
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

const repairCost = computed(() => {
  const sum = props.damages.reduce((acc, damage) => {
    return acc + (parseFloat(damage.cost) || 0)
  }, 0)
  return `¥${sum.toFixed(2)}`
})

const laborCost = computed(() => {
  const sum = props.damages.reduce((acc, damage) => {
    return acc + ((parseFloat(damage.cost) || 0) * 0.3)
  }, 0)
  return `¥${sum.toFixed(2)}`
})

const partsCost = computed(() => {
  const sum = props.damages.reduce((acc, damage) => {
    return acc + ((parseFloat(damage.cost) || 0) * 0.7)
  }, 0)
  return `¥${sum.toFixed(2)}`
})

const totalCost = computed(() => {
  const sum = props.damages.reduce((acc, damage) => {
    return acc + (parseFloat(damage.cost) || 0)
  }, 0)
  return `¥${sum.toFixed(2)}`
})
</script>

<style scoped>
.cost-summary {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.summary-title {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cost-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.cost-item.total {
  border-bottom: none;
  border-top: 2px solid #ebeef5;
  padding-top: 12px;
  margin-top: 8px;
}

.cost-label {
  font-size: 14px;
  color: #606266;
}

.cost-value {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.cost-value.total-value {
  font-size: 18px;
  font-weight: 600;
  color: #f56c6c;
}
</style>