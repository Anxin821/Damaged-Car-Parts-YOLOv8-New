<template>
  <PhoneShell v-if="isMobile" :scrollable="!isMobileHome">
    <router-view />
  </PhoneShell>

  <router-view v-else />
</template>

<script setup>
import PhoneShell from './components/common/PhoneShell.vue'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const isMobile = ref(false)
let mq = null

const route = useRoute()
const isMobileHome = computed(() => route.path === '/')

const setupMQ = () => {
  mq = window.matchMedia('(max-width: 500px)')
  isMobile.value = mq.matches

  const handler = (e) => {
    isMobile.value = e.matches
  }

  if (mq.addEventListener) {
    mq.addEventListener('change', handler)
  } else {
    mq.addListener(handler)
  }

  return () => {
    if (!mq) return
    if (mq.removeEventListener) {
      mq.removeEventListener('change', handler)
    } else {
      mq.removeListener(handler)
    }
  }
}

let cleanup = null

onMounted(() => {
  cleanup = setupMQ()
})

onBeforeUnmount(() => {
  if (cleanup) cleanup()
})
// App 根组件
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Arial, sans-serif;
  background-color: #f5f5f5;
}
</style>