<template>
  <div class="progress">
    <div class="progress-bar" :style="{ width: `${percentage}%` }"></div>
  </div>
</template>

<script setup>
defineProps({
  percentage: {
    type: Number,
    default: 0,
    validator: (value) => value >= 0 && value <= 100
  }
})
</script>

<style scoped>
.progress {
  width: 100%;
  height: 8px;
  background-color: #f0f2f5;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background-color: #409eff;
  transition: width 0.3s ease;
  border-radius: 4px;
}
</style>