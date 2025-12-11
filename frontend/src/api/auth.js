import apiClient from './client'

export default {
  // Вход
  async login(credentials) {
    const formData = new URLSearchParams()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    const response = await apiClient.post('/api/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    return response.data
  },

  // Выход
  async logout() {
    const response = await apiClient.post('/api/auth/logout')
    return response.data
  },

  // Обновление токена
  async refresh(refreshToken) {
    const response = await apiClient.post('/api/auth/refresh', { refresh_token: refreshToken })
    return response.data
  },

  // Получение текущего пользователя
  async me() {
    const response = await apiClient.get('/api/auth/me')
    return response.data
  },

  // Регистрация (если нужна)
  async register(userData) {
    const response = await apiClient.post('/api/auth/register', userData)
    return response.data
  }
}
