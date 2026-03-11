<template>
  <div class="image-annotation">
    <div class="image-container" ref="imageContainer">
      <img :src="imageUrl" alt="车辆图片" ref="image" />
      <div
        v-for="(damage, index) in damages"
        :key="index"
        class="damage-annotation"
        :style="{
          left: `${damage.x}%`,
          top: `${damage.y}%`,
          width: `${damage.width}%`,
          height: `${damage.height}%`
        }"
      >
        <div class="damage-label">{{ damage.type }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

const props = defineProps({
  imageUrl: {
    type: String,
    default: ''
  },
  damages: {
    type: Array,
    default: () => []
  }
})

const imageContainer = ref(null)
const image = ref(null)

const emit = defineEmits(['annotationClick'])

const handleAnnotationClick = (damage, event) => {
  event.stopPropagation()
  emit('annotationClick', damage)
}
</script>

<style scoped>
.image-annotation {
  position: relative;
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.image-container {
  position: relative;
  width: 100%;
  overflow: hidden;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

img {
  width: 100%;
  height: auto;
  display: block;
}

.damage-annotation {
  position: absolute;
  border: 2px solid #f56c6c;
  border-radius: 4px;
  background-color: rgba(245, 108, 108, 0.2);
  cursor: pointer;
  transition: all 0.3s ease;
}

.damage-annotation:hover {
  border-color: #f78989;
  background-color: rgba(245, 108, 108, 0.3);
}

.damage-label {
  position: absolute;
  top: -20px;
  left: 0;
  background-color: #f56c6c;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}
</style>