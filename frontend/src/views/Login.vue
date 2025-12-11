<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark>
            <v-toolbar-title>Legal CMS - Вход</v-toolbar-title>
          </v-toolbar>
          <v-card-text>
            <v-form @submit.prevent="handleLogin">
              <v-text-field
                v-model="username"
                label="Логин"
                prepend-icon="mdi-account"
                type="text"
                :disabled="loading"
                :error-messages="errors.username"
                required
              ></v-text-field>

              <v-text-field
                v-model="password"
                label="Пароль"
                prepend-icon="mdi-lock"
                :type="showPassword ? 'text' : 'password'"
                :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append="showPassword = !showPassword"
                :disabled="loading"
                :error-messages="errors.password"
                required
              ></v-text-field>

              <v-alert
                v-if="authStore.error"
                type="error"
                variant="tonal"
                class="mb-4"
              >
                {{ authStore.error }}
              </v-alert>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              variant="elevated"
              :loading="loading"
              @click="handleLogin"
              block
            >
              Войти
            </v-btn>
          </v-card-actions>
        </v-card>

        <v-card class="mt-4" variant="outlined">
          <v-card-text class="text-center">
            <p class="text-body-2 text-medium-emphasis">
              Система электронного документооборота<br>
              для юридической практики
            </p>
            <p class="text-caption text-medium-emphasis mt-2">
              Version 1.0.0-beta
            </p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errors = ref({})

async function handleLogin() {
  if (!username.value || !password.value) {
    errors.value = {
      username: !username.value ? ['Введите логин'] : [],
      password: !password.value ? ['Введите пароль'] : []
    }
    return
  }

  errors.value = {}
  loading.value = true

  try {
    await authStore.login({
      username: username.value,
      password: password.value
    })

    // Перенаправляем на страницу, с которой пришли, или на Dashboard
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (error) {
    console.error('Login error:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>
