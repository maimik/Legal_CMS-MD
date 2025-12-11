import apiClient from './client'

export default {
  async getAll(params = {}) {
    const response = await apiClient.get('/api/persons', { params })
    return response.data
  },

  async getById(id) {
    const response = await apiClient.get(`/api/persons/${id}`)
    return response.data
  },

  async create(personData) {
    const response = await apiClient.post('/api/persons', personData)
    return response.data
  },

  async update(id, personData) {
    const response = await apiClient.put(`/api/persons/${id}`, personData)
    return response.data
  },

  async delete(id) {
    const response = await apiClient.delete(`/api/persons/${id}`)
    return response.data
  },

  async getCases(id) {
    const response = await apiClient.get(`/api/persons/${id}/cases`)
    return response.data
  }
}
