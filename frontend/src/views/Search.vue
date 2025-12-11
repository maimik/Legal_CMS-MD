<template>
  <div>
    <h1 class="text-h4 mb-6">Глобальный поиск</h1>
    <v-card class="mb-4">
      <v-card-text>
        <v-text-field v-model="query" label="Поиск" prepend-inner-icon="mdi-magnify" @keyup.enter="search"></v-text-field>
        <v-btn color="primary" @click="search" :loading="loading" block>Найти</v-btn>
      </v-card-text>
    </v-card>
    <v-card v-if="results.cases?.length">
      <v-card-title>Дела ({{ results.cases.length }})</v-card-title>
      <v-list>
        <v-list-item v-for="item in results.cases" :key="item.id" :to="`/cases/${item.id}`">
          <v-list-item-title>{{ item.case_number }} - {{ item.title }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-card>
    <v-card v-if="results.documents?.length" class="mt-4">
      <v-card-title>Документы ({{ results.documents.length }})</v-card-title>
      <v-list>
        <v-list-item v-for="item in results.documents" :key="item.id" :to="`/documents/${item.id}`">
          <v-list-item-title>{{ item.file_name }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-card>
    <v-card v-if="results.persons?.length" class="mt-4">
      <v-card-title>Персоны ({{ results.persons.length }})</v-card-title>
      <v-list>
        <v-list-item v-for="item in results.persons" :key="item.id">
          <v-list-item-title>{{ item.full_name }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const query = ref(route.query.q || '')
const results = ref({})
const loading = ref(false)

async function search() {
  if (!query.value) return
  loading.value = true
  try {
    results.value = await api.search.global(query.value)
  } finally {
    loading.value = false
  }
}
</script>
