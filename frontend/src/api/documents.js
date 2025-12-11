import apiClient from './client'

export default {
  // Получить список документов
  async getAll(params = {}) {
    const response = await apiClient.get('/api/documents', { params })
    return response.data
  },

  // Получить один документ
  async getById(id) {
    const response = await apiClient.get(`/api/documents/${id}`)
    return response.data
  },

  // Загрузить документ
  async upload(formData) {
    const response = await apiClient.post('/api/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  // Обновить метаданные документа
  async update(id, data) {
    const response = await apiClient.put(`/api/documents/${id}`, data)
    return response.data
  },

  // Удалить документ
  async delete(id) {
    const response = await apiClient.delete(`/api/documents/${id}`)
    return response.data
  },

  // Скачать документ
  getDownloadUrl(id) {
    return `${apiClient.defaults.baseURL}/api/documents/${id}/download`
  },

  // Превью документа
  getPreviewUrl(id) {
    return `${apiClient.defaults.baseURL}/api/documents/${id}/preview`
  },

  // Запустить OCR
  async runOcr(id) {
    const response = await apiClient.post(`/api/documents/${id}/ocr`)
    return response.data
  }
}
