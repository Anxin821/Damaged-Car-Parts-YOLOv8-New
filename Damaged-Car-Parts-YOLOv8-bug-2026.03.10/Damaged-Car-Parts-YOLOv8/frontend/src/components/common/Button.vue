<template>
  <button
    class="btn"
    :class="[
      `btn-${type}`,
      { 'btn-disabled': disabled }
    ]"
    :disabled="disabled"
    @click="$emit('click')"
  >
    <slot></slot>
  </button>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'primary'
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

defineEmits(['click'])
</script>

<style scoped>
.btn {
  display: inline-block;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: #409eff;
  color: white;
}

.btn-success {
  background-color: #67c23a;
  color: white;
}

.btn-warning {
  background-color: #e6a23c;
  color: white;
}

.btn-danger {
  background-color: #f56c6c;
  color: white;
}

.btn-disabled {
  background-color: #c0c4cc;
  color: #fff;
  cursor: not-allowed;
}
</style>