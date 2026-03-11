import { ref, computed } from 'vue'

/**
 * 检测相关逻辑hook
 */
export function useDetection() {
  const isDetecting = ref(false)
  const detectionResult = ref(null)
  const detectionError = ref(null)

  /**
   * 执行损伤检测
   * @param {File} imageFile - 图片文件
   * @returns {Promise<Object>} 检测结果
   */
  const detectDamage = async (imageFile) => {
    isDetecting.value = true
    detectionError.value = null

    try {
      // 这里应该调用后端API进行实际检测
      // 模拟检测过程
      await new Promise(resolve => setTimeout(resolve, 2000))

      // 模拟检测结果
      detectionResult.value = {
        imageUrl: URL.createObjectURL(imageFile),
        damages: [
          {
            type: '划痕',
            location: '左侧车门',
            severity: '轻微',
            cost: '500',
            repairTime: '2小时',
            x: 20,
            y: 40,
            width: 30,
            height: 15
          },
          {
            type: '凹陷',
            location: '前保险杠',
            severity: '中度',
            cost: '1200',
            repairTime: '4小时',
            x: 10,
            y: 60,
            width: 25,
            height: 20
          },
          {
            type: '漆面损伤',
            location: '右侧后视镜',
            severity: '轻微',
            cost: '300',
            repairTime: '1小时',
            x: 60,
            y: 35,
            width: 15,
            height: 10
          }
        ],
        totalCost: '2000',
        totalRepairTime: '7小时'
      }

      return detectionResult.value
    } catch (error) {
      detectionError.value = error.message
      throw error
    } finally {
      isDetecting.value = false
    }
  }

  /**
   * 计算总费用
   */
  const totalCost = computed(() => {
    if (!detectionResult.value?.damages) return '0'
    return detectionResult.value.damages.reduce((sum, damage) => {
      return sum + parseInt(damage.cost)
    }, 0).toString()
  })

  /**
   * 计算总维修时间
   */
  const totalRepairTime = computed(() => {
    if (!detectionResult.value?.damages) return '0小时'
    return detectionResult.value.damages.reduce((sum, damage) => {
      return sum + parseInt(damage.repairTime)
    }, 0) + '小时'
  })

  /**
   * 重置检测状态
   */
  const resetDetection = () => {
    isDetecting.value = false
    detectionResult.value = null
    detectionError.value = null
  }

  return {
    isDetecting,
    detectionResult,
    detectionError,
    detectDamage,
    totalCost,
    totalRepairTime,
    resetDetection
  }
}