import { ref } from 'vue'
import { useImageProcess } from './useImageProcess'

/**
 * 上传逻辑hook
 */
export function useUpload() {
  const isUploading = ref(false)
  const uploadProgress = ref(0)
  const uploadError = ref(null)
  const uploadedFile = ref(null)
  
  const { validateImage, compressImage } = useImageProcess()

  /**
   * 处理文件选择
   * @param {Event} event - 文件选择事件
   * @returns {Promise<File>} 选中的文件
   */
  const handleFileSelect = async (event) => {
    const file = event.target.files[0]
    if (!file) return null

    const validation = validateImage(file)
    if (!validation.valid) {
      uploadError.value = validation.message
      return null
    }

    try {
      // 压缩图片
      const compressedBlob = await compressImage(file)
      const compressedFile = new File([compressedBlob], file.name, {
        type: 'image/jpeg'
      })

      uploadedFile.value = compressedFile
      return compressedFile
    } catch (error) {
      uploadError.value = '处理图片失败'
      return null
    }
  }

  /**
   * 处理拖拽上传
   * @param {DragEvent} event - 拖拽事件
   * @returns {Promise<File>} 拖拽的文件
   */
  const handleDragDrop = async (event) => {
    event.preventDefault()
    event.stopPropagation()

    const file = event.dataTransfer.files[0]
    if (!file) return null

    const validation = validateImage(file)
    if (!validation.valid) {
      uploadError.value = validation.message
      return null
    }

    try {
      // 压缩图片
      const compressedBlob = await compressImage(file)
      const compressedFile = new File([compressedBlob], file.name, {
        type: 'image/jpeg'
      })

      uploadedFile.value = compressedFile
      return compressedFile
    } catch (error) {
      uploadError.value = '处理图片失败'
      return null
    }
  }

  /**
   * 上传文件到服务器
   * @param {File} file - 要上传的文件
   * @returns {Promise<Object>} 上传结果
   */
  const uploadFile = async (file) => {
    if (!file) {
      uploadError.value = '请选择文件'
      return null
    }

    isUploading.value = true
    uploadProgress.value = 0
    uploadError.value = null

    try {
      // 模拟上传过程
      return new Promise((resolve) => {
        let progress = 0
        const interval = setInterval(() => {
          progress += 10
          uploadProgress.value = progress
          
          if (progress >= 100) {
            clearInterval(interval)
            setTimeout(() => {
              isUploading.value = false
              resolve({ success: true, file })
            }, 500)
          }
        }, 200)
      })

      // 实际上传代码
      // const formData = new FormData()
      // formData.append('file', file)
      // 
      // const response = await fetch('/api/upload', {
      //   method: 'POST',
      //   body: formData,
      //   onUploadProgress: (progressEvent) => {
      //     if (progressEvent.lengthComputable) {
      //       uploadProgress.value = Math.round((progressEvent.loaded / progressEvent.total) * 100)
      //     }
      //   }
      // })
      // 
      // if (!response.ok) {
      //   throw new Error('上传失败')
      // }
      // 
      // const result = await response.json()
      // uploadedFile.value = file
      // return result
    } catch (error) {
      uploadError.value = error.message || '上传失败'
      isUploading.value = false
      return null
    }
  }

  /**
   * 重置上传状态
   */
  const resetUpload = () => {
    isUploading.value = false
    uploadProgress.value = 0
    uploadError.value = null
    uploadedFile.value = null
  }

  return {
    isUploading,
    uploadProgress,
    uploadError,
    uploadedFile,
    handleFileSelect,
    handleDragDrop,
    uploadFile,
    resetUpload
  }
}