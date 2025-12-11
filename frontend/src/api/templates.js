import apiClient from './client'

export default {
  async getAll() {
    const response = await apiClient.get('/api/templates')
    return response.data
  },

  async upload(formData) {
    const response = await apiClient.post('/api/templates', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async generate(templateId, caseId) {
    const response = await apiClient.post(`/api/templates/${templateId}/generate`, {
      case_id: caseId
    }, {
      responseType: 'blob'
    })
    return response
  },

  async delete(id) {
    const response = await apiClient.delete(`/api/templates/${id}`)
    return response.data
  }
}
