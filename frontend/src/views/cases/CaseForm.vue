<template>
  <div>
    <h1 class="text-h4 mb-6">{{ isEdit ? 'Редактирование дела' : 'Новое дело' }}</h1>
    
    <v-form @submit.prevent="handleSubmit">
      <v-card>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field v-model="form.case_number" label="Номер дела *" required></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-select v-model="form.case_type" :items="caseTypes" label="Тип дела *" required></v-select>
            </v-col>
            <v-col cols="12">
              <v-text-field v-model="form.title" label="Название *" required></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field v-model="form.plaintiff" label="Истец"></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field v-model="form.defendant" label="Ответчик"></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field v-model="form.court_name" label="Суд"></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field v-model="form.judge_name" label="Судья"></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-select v-model="form.case_status" :items="statusOptions" label="Статус *" required></v-select>
            </v-col>
            <v-col cols="12">
              <v-textarea v-model="form.description" label="Описание" rows="4"></v-textarea>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-btn variant="text" @click="$router.back()">Отмена</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="primary" type="submit" :loading="loading">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCasesStore } from '@/stores/cases'

const route = useRoute()
const router = useRouter()
const casesStore = useCasesStore()

const loading = ref(false)
const form = ref({ case_status: 'new', case_type: 'civil' })

const isEdit = computed(() => !!route.params.id)

const caseTypes = [
  { title: 'Гражданское', value: 'civil' },
  { title: 'Уголовное', value: 'criminal' },
  { title: 'Административное', value: 'administrative' },
  { title: 'Другое', value: 'other' }
]

const statusOptions = [
  { title: 'Новое', value: 'new' },
  { title: 'В работе', value: 'in_progress' },
  { title: 'Приостановлено', value: 'suspended' },
  { title: 'Завершено', value: 'completed' },
  { title: 'Архив', value: 'archived' }
]

async function handleSubmit() {
  loading.value = true
  try {
    if (isEdit.value) {
      await casesStore.updateCase(route.params.id, form.value)
    } else {
      await casesStore.createCase(form.value)
    }
    router.push('/cases')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (isEdit.value) {
    await casesStore.fetchCase(route.params.id)
    form.value = { ...casesStore.currentCase }
  }
})
</script>
