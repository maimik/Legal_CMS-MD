import apiClient from './client'

export default {
  // Получить список дел
  async getAll(params = {}) {
    const response = await apiClient.get('/api/cases', { params })
    return response.data
  },

  // Получить одно дело
  async getById(id) {
    const response = await apiClient.get(`/api/cases/${id}`)
    return response.data
  },

  // Создать дело
  async create(caseData) {
    const response = await apiClient.post('/api/cases', caseData)
    return response.data
  },

  // Обновить дело
  async update(id, caseData) {
    const response = await apiClient.put(`/api/cases/${id}`, caseData)
    return response.data
  },

  // Удалить дело
  async delete(id) {
    const response = await apiClient.delete(`/api/cases/${id}`)
    return response.data
  },

  // Получить timeline дела
  async getTimeline(id) {
    const response = await apiClient.get(`/api/cases/${id}/timeline`)
    return response.data
  }
}
