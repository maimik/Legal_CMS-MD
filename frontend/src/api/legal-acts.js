import apiClient from './client'

export default {
  async getAll(params = {}) {
    const response = await apiClient.get('/api/legal-acts', { params })
    return response.data
  },

  async getById(id) {
    const response = await apiClient.get(`/api/legal-acts/${id}`)
    return response.data
  },

  async upload(formData) {
    const response = await apiClient.post('/api/legal-acts', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async delete(id) {
    const response = await apiClient.delete(`/api/legal-acts/${id}`)
    return response.data
  },

  getDownloadUrl(id) {
    return `${apiClient.defaults.baseURL}/api/legal-acts/${id}/download`
  }
}
