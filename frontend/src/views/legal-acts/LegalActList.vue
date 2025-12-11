<template>
  <div>
    <h1 class="text-h4 mb-6">Законодательная база РМ</h1>
    <v-card>
      <v-card-title>
        <v-text-field v-model="search" prepend-inner-icon="mdi-magnify" label="Поиск" @input="handleSearch"></v-text-field>
      </v-card-title>
      <v-data-table :headers="[
        { title: 'Название', key: 'title' },
        { title: 'Тип', key: 'act_type' },
        { title: 'Номер', key: 'act_number' },
        { title: 'Дата', key: 'act_date' },
        { title: 'Действия', key: 'actions', sortable: false }
      ]" :items="acts" :loading="loading">
        <template v-slot:item.actions="{ item }">
          <v-btn icon="mdi-download" size="small" variant="text" :href="`/api/legal-acts/${item.id}/download`" target="_blank"></v-btn>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const acts = ref([])
const loading = ref(false)
const search = ref('')

async function loadActs() {
  loading.value = true
  try {
    const res = await api.legalActs.getAll({ search: search.value })
    acts.value = res.items
  } finally {
    loading.value = false
  }
}

let searchTimeout
function handleSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(loadActs, 500)
}

onMounted(loadActs)
</script>
