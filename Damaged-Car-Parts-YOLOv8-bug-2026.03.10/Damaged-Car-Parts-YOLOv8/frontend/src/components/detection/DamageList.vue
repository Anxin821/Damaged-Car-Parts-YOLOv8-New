<template>
  <div class="damage-list">
    <h3 class="list-title">损伤列表</h3>
    <div class="list-content">
      <div
        v-for="(damage, index) in damages"
        :key="index"
        class="damage-item"
        :class="{ 'selected': selectedDamage === index }"
        @click="selectDamage(index)"
      >
        <div class="damage-header">
          <span class="damage-type">{{ damage.type }}</span>
          <span class="damage-cost">{{ damage.cost }}</span>
        </div>
        <div class="damage-details">
          <div class="detail-item">
            <span class="detail-label">位置：</span>
            <span class="detail-value">{{ damage.location }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">程度：</span>
            <span class="detail-value">{{ damage.severity }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">维修时间：</span>
            <span class="detail-value">{{ damage.repairTime }}</span>
          </div>
        </div>
      </div>
      <div v-if="damages.length === 0" class="empty-state">
        <p>暂无损伤记录</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  damages: {
    type: Array,
    default: () => []
  }
})

const selectedDamage = ref(-1)

const emit = defineEmits(['damageSelect'])

const selectDamage = (index) => {
  selectedDamage.value = index
  emit('damageSelect', props.damages[index])
}
</script>

<style scoped>
.damage-list {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.list-title {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.list-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.damage-item {
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.damage-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.damage-item.selected {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.damage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.damage-type {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.damage-cost {
  font-size: 14px;
  font-weight: 600;
  color: #f56c6c;
}

.damage-details {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.detail-item {
  display: flex;
  align-items: center;
}

.detail-label {
  font-size: 12px;
  color: #909399;
  width: 80px;
}

.detail-value {
  font-size: 12px;
  color: #606266;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
  background-color: #fafafa;
  border-radius: 6px;
}
</style>