import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export const useCasesStore = defineStore('cases', () => {
  // State
  const cases = ref([])
  const currentCase = ref(null)
  const timeline = ref([])
  const loading = ref(false)
  const error = ref(null)
  const pagination = ref({
    page: 1,
    size: 20,
    total: 0,
    pages: 0
  })

  // Actions
  async function fetchCases(params = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await api.cases.getAll({
        page: pagination.value.page,
        size: pagination.value.size,
        ...params
      })

      cases.value = response.items
      pagination.value = {
        page: response.page,
        size: response.size,
        total: response.total,
        pages: response.pages
      }

      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки дел'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchCase(id) {
    loading.value = true
    error.value = null
    try {
      const response = await api.cases.getById(id)
      currentCase.value = response
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки дела'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createCase(caseData) {
    loading.value = true
    error.value = null
    try {
      const response = await api.cases.create(caseData)
      cases.value.unshift(response)
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка создания дела'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateCase(id, caseData) {
    loading.value = true
    error.value = null
    try {
      const response = await api.cases.update(id, caseData)

      const index = cases.value.findIndex(c => c.id === id)
      if (index !== -1) {
        cases.value[index] = response
      }

      if (currentCase.value?.id === id) {
        currentCase.value = response
      }

      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка обновления дела'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteCase(id) {
    loading.value = true
    error.value = null
    try {
      await api.cases.delete(id)
      cases.value = cases.value.filter(c => c.id !== id)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка удаления дела'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchTimeline(id) {
    loading.value = true
    error.value = null
    try {
      const response = await api.cases.getTimeline(id)
      timeline.value = response
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки истории'
      throw err
    } finally {
      loading.value = false
    }
  }

  function setPage(page) {
    pagination.value.page = page
  }

  return {
    // State
    cases,
    currentCase,
    timeline,
    loading,
    error,
    pagination,
    // Actions
    fetchCases,
    fetchCase,
    createCase,
    updateCase,
    deleteCase,
    fetchTimeline,
    setPage
  }
})
