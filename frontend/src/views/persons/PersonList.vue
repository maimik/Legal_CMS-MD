<template>
  <div>
    <v-row class="mb-4">
      <v-col><h1 class="text-h4">Персоны</h1></v-col>
      <v-col class="text-right">
        <v-btn color="primary" to="/persons/new"><v-icon start>mdi-plus</v-icon>Добавить персону</v-btn>
      </v-col>
    </v-row>
    <v-card>
      <v-card-title>
        <v-text-field v-model="search" prepend-inner-icon="mdi-magnify" label="Поиск" single-line hide-details clearable @input="handleSearch"></v-text-field>
      </v-card-title>
      <v-data-table :headers="[
        { title: 'ФИО', key: 'full_name' },
        { title: 'Тип', key: 'person_type' },
        { title: 'IDNP/IDNO', key: 'idnp' },
        { title: 'Телефон', key: 'phone' },
        { title: 'Действия', key: 'actions', sortable: false }
      ]" :items="persons" :loading="loading">
        <template v-slot:item.person_type="{ item }">
          <v-chip size="small">{{ getPersonTypeText(item.person_type) }}</v-chip>
        </template>
        <template v-slot:item.actions="{ item }">
          <v-btn icon="mdi-pencil" size="small" variant="text" :to="`/persons/${item.id}/edit`"></v-btn>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const persons = ref([])
const loading = ref(false)
const search = ref('')

function getPersonTypeText(type) {
  const types = { client: 'Клиент', judge: 'Судья', lawyer: 'Адвокат', opponent: 'Противник', witness: 'Свидетель', other: 'Другое' }
  return types[type] || type
}

async function loadPersons() {
  loading.value = true
  try {
    const res = await api.persons.getAll({ search: search.value })
    persons.value = res.items
  } finally {
    loading.value = false
  }
}

let searchTimeout
function handleSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(loadPersons, 500)
}

onMounted(loadPersons)
</script>
