import apiClient from './client'

export default {
  async getCasePdf(caseId) {
    const response = await apiClient.get(`/api/reports/case/${caseId}/pdf`, {
      responseType: 'blob'
    })
    return response
  },

  async getStatistics() {
    const response = await apiClient.get('/api/reports/statistics')
    return response.data
  },

  async exportCases(params = {}) {
    const response = await apiClient.get('/api/reports/export/cases', {
      params,
      responseType: 'blob'
    })
    return response
  }
}
