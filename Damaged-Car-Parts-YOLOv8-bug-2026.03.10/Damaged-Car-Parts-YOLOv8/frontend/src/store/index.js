import { createPinia } from 'pinia'
import { useDetectionStore } from './detection'
import { useUserStore } from './user'
import { useThemeStore } from './theme'
import { useHistoryStore } from './history'

const pinia = createPinia()

export {
  pinia,
  useDetectionStore,
  useUserStore,
  useThemeStore,
  useHistoryStore
}
