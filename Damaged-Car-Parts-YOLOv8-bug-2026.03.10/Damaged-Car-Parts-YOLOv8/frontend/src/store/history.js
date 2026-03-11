import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useHistoryStore = defineStore('history', () => {
  const history = ref(JSON.parse(localStorage.getItem('detectionHistory') || '[]'))

  const addToHistory = (detectionData) => {
    const newRecord = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      ...detectionData
    }
    history.value.unshift(newRecord)
    saveHistory()
  }

  const removeFromHistory = (id) => {
    history.value = history.value.filter(item => item.id !== id)
    saveHistory()
  }

  const clearHistory = () => {
    history.value = []
    saveHistory()
  }

  const saveHistory = () => {
    localStorage.setItem('detectionHistory', JSON.stringify(history.value))
  }

  return {
    history,
    addToHistory,
    removeFromHistory,
    clearHistory
  }
})
