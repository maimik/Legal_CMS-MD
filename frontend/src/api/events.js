import apiClient from './client'

export default {
  async getAll(params = {}) {
    const response = await apiClient.get('/api/events', { params })
    return response.data
  },

  async getById(id) {
    const response = await apiClient.get(`/api/events/${id}`)
    return response.data
  },

  async create(eventData) {
    const response = await apiClient.post('/api/events', eventData)
    return response.data
  },

  async update(id, eventData) {
    const response = await apiClient.put(`/api/events/${id}`, eventData)
    return response.data
  },

  async delete(id) {
    const response = await apiClient.delete(`/api/events/${id}`)
    return response.data
  },

  async getCalendar(year, month) {
    const response = await apiClient.get(`/api/events/calendar/${year}/${month}`)
    return response.data
  },

  async getUpcomingWeek() {
    const response = await apiClient.get('/api/events/upcoming/week')
    return response.data
  }
}
