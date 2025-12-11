<template>
  <v-app>
    <router-view />
  </v-app>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  // Проверяем токен при загрузке приложения
  if (authStore.token) {
    authStore.checkAuth()
  }
})
</script>

<style>
/* Global styles в main.css */
</style>
