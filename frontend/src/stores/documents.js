import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export const useDocumentsStore = defineStore('documents', () => {
  // State
  const documents = ref([])
  const currentDocument = ref(null)
  const loading = ref(false)
  const uploadProgress = ref(0)
  const error = ref(null)
  const pagination = ref({
    page: 1,
    size: 20,
    total: 0,
    pages: 0
  })

  // Actions
  async function fetchDocuments(params = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await api.documents.getAll({
        page: pagination.value.page,
        size: pagination.value.size,
        ...params
      })

      documents.value = response.items
      pagination.value = {
        page: response.page,
        size: response.size,
        total: response.total,
        pages: response.pages
      }

      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки документов'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchDocument(id) {
    loading.value = true
    error.value = null
    try {
      const response = await api.documents.getById(id)
      currentDocument.value = response
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки документа'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function uploadDocument(formData, onProgress) {
    loading.value = true
    uploadProgress.value = 0
    error.value = null

    try {
      const response = await api.documents.upload(formData)
      documents.value.unshift(response)
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки файла'
      throw err
    } finally {
      loading.value = false
      uploadProgress.value = 0
    }
  }

  async function updateDocument(id, data) {
    loading.value = true
    error.value = null
    try {
      const response = await api.documents.update(id, data)

      const index = documents.value.findIndex(d => d.id === id)
      if (index !== -1) {
        documents.value[index] = response
      }

      if (currentDocument.value?.id === id) {
        currentDocument.value = response
      }

      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка обновления документа'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteDocument(id) {
    loading.value = true
    error.value = null
    try {
      await api.documents.delete(id)
      documents.value = documents.value.filter(d => d.id !== id)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка удаления документа'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function runOcr(id) {
    loading.value = true
    error.value = null
    try {
      const response = await api.documents.runOcr(id)

      // Обновляем документ с OCR текстом
      if (currentDocument.value?.id === id) {
        currentDocument.value.ocr_text = response.ocr_text
      }

      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка OCR'
      throw err
    } finally {
      loading.value = false
    }
  }

  function getDownloadUrl(id) {
    return api.documents.getDownloadUrl(id)
  }

  function getPreviewUrl(id) {
    return api.documents.getPreviewUrl(id)
  }

  function setPage(page) {
    pagination.value.page = page
  }

  return {
    // State
    documents,
    currentDocument,
    loading,
    uploadProgress,
    error,
    pagination,
    // Actions
    fetchDocuments,
    fetchDocument,
    uploadDocument,
    updateDocument,
    deleteDocument,
    runOcr,
    getDownloadUrl,
    getPreviewUrl,
    setPage
  }
})
