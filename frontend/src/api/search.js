import apiClient from './client'

export default {
  async global(query, params = {}) {
    const response = await apiClient.get('/api/search', {
      params: { q: query, ...params }
    })
    return response.data
  },

  async fulltext(query) {
    const response = await apiClient.get('/api/search/fulltext', {
      params: { q: query }
    })
    return response.data
  },

  async semantic(query) {
    const response = await apiClient.post('/api/search/semantic', {
      query,
      top_k: 10
    })
    return response.data
  }
}
