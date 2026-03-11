import { ref, onMounted, watch } from 'vue'

/**
 * 主题切换逻辑hook
 */
export function useTheme() {
  const theme = ref('light')
  const isDarkMode = ref(false)

  /**
   * 切换主题
   * @param {string} newTheme - 新主题 ('light' | 'dark')
   */
  const setTheme = (newTheme) => {
    theme.value = newTheme
    isDarkMode.value = newTheme === 'dark'
    updateThemeClass()
    saveThemeToStorage()
  }

  /**
   * 切换到深色模式
   */
  const toggleDarkMode = () => {
    const newTheme = isDarkMode.value ? 'light' : 'dark'
    setTheme(newTheme)
  }

  /**
   * 更新文档根元素的主题类
   */
  const updateThemeClass = () => {
    const root = document.documentElement
    if (isDarkMode.value) {
      root.classList.add('dark-mode')
      root.classList.remove('light-mode')
    } else {
      root.classList.add('light-mode')
      root.classList.remove('dark-mode')
    }
  }

  /**
   * 保存主题到本地存储
   */
  const saveThemeToStorage = () => {
    try {
      localStorage.setItem('theme', theme.value)
    } catch (error) {
      console.error('保存主题失败:', error)
    }
  }

  /**
   * 从本地存储加载主题
   */
  const loadThemeFromStorage = () => {
    try {
      const savedTheme = localStorage.getItem('theme')
      if (savedTheme) {
        setTheme(savedTheme)
      } else {
        // 检测系统偏好
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
        setTheme(prefersDark ? 'dark' : 'light')
      }
    } catch (error) {
      console.error('加载主题失败:', error)
      setTheme('light')
    }
  }

  /**
   * 监听系统主题变化
   */
  const setupSystemThemeListener = () => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    
    const handleChange = (e) => {
      // 只有当用户没有手动设置主题时，才跟随系统变化
      try {
        const savedTheme = localStorage.getItem('theme')
        if (!savedTheme) {
          setTheme(e.matches ? 'dark' : 'light')
        }
      } catch (error) {
        console.error('监听系统主题失败:', error)
      }
    }

    mediaQuery.addEventListener('change', handleChange)
    
    // 清理函数
    return () => {
      mediaQuery.removeEventListener('change', handleChange)
    }
  }

  onMounted(() => {
    loadThemeFromStorage()
    setupSystemThemeListener()
  })

  return {
    theme,
    isDarkMode,
    setTheme,
    toggleDarkMode
  }
}