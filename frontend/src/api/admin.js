import apiClient from './client'

export default {
  // Пользователи
  async getUsers(params = {}) {
    const response = await apiClient.get('/api/admin/users', { params })
    return response.data
  },

  async createUser(userData) {
    const response = await apiClient.post('/api/admin/users', userData)
    return response.data
  },

  async updateUser(id, userData) {
    const response = await apiClient.put(`/api/admin/users/${id}`, userData)
    return response.data
  },

  async deleteUser(id) {
    const response = await apiClient.delete(`/api/admin/users/${id}`)
    return response.data
  },

  // Настройки
  async getSettings() {
    const response = await apiClient.get('/api/admin/settings')
    return response.data
  },

  async updateSetting(key, value, description = null) {
    const response = await apiClient.put(`/api/admin/settings/${key}`, {
      value,
      description
    })
    return response.data
  },

  // Аудит
  async getAuditLog(params = {}) {
    const response = await apiClient.get('/api/admin/audit-log', { params })
    return response.data
  },

  // Backup
  async createBackup() {
    const response = await apiClient.post('/api/admin/backup')
    return response.data
  },

  // Системная информация
  async getSystemInfo() {
    const response = await apiClient.get('/api/admin/system-info')
    return response.data
  }
}
