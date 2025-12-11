import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  // Actions
  async function login(credentials) {
    loading.value = true
    error.value = null
    try {
      const response = await api.auth.login(credentials)

      token.value = response.access_token
      refreshToken.value = response.refresh_token

      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)

      await checkAuth()

      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка входа'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    loading.value = true
    try {
      await api.auth.logout()
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      token.value = null
      refreshToken.value = null
      user.value = null

      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')

      loading.value = false
    }
  }

  async function refreshAccessToken() {
    if (!refreshToken.value) {
      throw new Error('No refresh token')
    }

    try {
      const response = await api.auth.refresh(refreshToken.value)

      token.value = response.access_token
      localStorage.setItem('access_token', response.access_token)

      return response
    } catch (err) {
      // Если refresh не удался - выходим
      await logout()
      throw err
    }
  }

  async function checkAuth() {
    if (!token.value) {
      return false
    }

    loading.value = true
    try {
      const response = await api.auth.me()
      user.value = response
      return true
    } catch (err) {
      // Токен невалиден
      await logout()
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    token,
    refreshToken,
    user,
    loading,
    error,
    // Getters
    isAuthenticated,
    isAdmin,
    // Actions
    login,
    logout,
    refreshAccessToken,
    checkAuth
  }
})
