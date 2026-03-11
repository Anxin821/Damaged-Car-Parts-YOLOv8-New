<template>
  <span class="badge" :class="`badge-${type}`">
    <slot></slot>
  </span>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'default'
  }
})
</script>

<style scoped>
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.badge-default {
  background-color: #f0f2f5;
  color: #606266;
}

.badge-primary {
  background-color: #ecf5ff;
  color: #409eff;
}

.badge-success {
  background-color: #f0f9eb;
  color: #67c23a;
}

.badge-warning {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.badge-danger {
  background-color: #fef0f0;
  color: #f56c6c;
}
</style>