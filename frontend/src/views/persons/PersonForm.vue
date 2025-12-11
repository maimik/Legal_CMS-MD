<template>
  <div>
    <h1 class="text-h4 mb-6">{{ isEdit ? 'Редактирование персоны' : 'Новая персона' }}</h1>
    <v-form @submit.prevent="handleSubmit">
      <v-card>
        <v-card-text>
          <v-row>
            <v-col cols="12"><v-text-field v-model="form.full_name" label="ФИО *" required></v-text-field></v-col>
            <v-col cols="12" md="6">
              <v-select v-model="form.person_type" :items="[
                { title: 'Клиент', value: 'client' },
                { title: 'Судья', value: 'judge' },
                { title: 'Адвокат', value: 'lawyer' },
                { title: 'Противник', value: 'opponent' },
                { title: 'Свидетель', value: 'witness' },
                { title: 'Другое', value: 'other' }
              ]" label="Тип персоны *" required></v-select>
            </v-col>
            <v-col cols="12" md="6"><v-text-field v-model="form.idnp" label="IDNP/IDNO" hint="13 цифр" maxlength="13"></v-text-field></v-col>
            <v-col cols="12" md="6"><v-text-field v-model="form.phone" label="Телефон"></v-text-field></v-col>
            <v-col cols="12" md="6"><v-text-field v-model="form.email" label="Email" type="email"></v-text-field></v-col>
            <v-col cols="12"><v-textarea v-model="form.address" label="Адрес" rows="2"></v-textarea></v-col>
            <v-col cols="12"><v-textarea v-model="form.notes" label="Заметки" rows="3"></v-textarea></v-col>
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
import api from '@/api'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const form = ref({ person_type: 'client' })
const isEdit = computed(() => !!route.params.id)

async function handleSubmit() {
  loading.value = true
  try {
    if (isEdit.value) {
      await api.persons.update(route.params.id, form.value)
    } else {
      await api.persons.create(form.value)
    }
    router.push('/persons')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (isEdit.value) {
    form.value = await api.persons.getById(route.params.id)
  }
})
</script>
