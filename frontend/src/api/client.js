import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Создаём экземпляр axios
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 30000
})

// Request interceptor - добавляем токен к каждому запросу
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - обрабатываем ошибки
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // Если 401 и не запрос на refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const authStore = useAuthStore()

      // Пытаемся обновить токен
      if (authStore.refreshToken && originalRequest.url !== '/api/auth/refresh') {
        try {
          await authStore.refreshAccessToken()
          // Повторяем оригинальный запрос с новым токеном
          return apiClient(originalRequest)
        } catch (refreshError) {
          // Если refresh не удался - выходим
          authStore.logout()
          router.push({ name: 'Login' })
          return Promise.reject(refreshError)
        }
      } else {
        // Нет refresh токена - выходим
        authStore.logout()
        router.push({ name: 'Login' })
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
