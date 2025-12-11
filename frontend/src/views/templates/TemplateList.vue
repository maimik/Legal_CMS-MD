<template>
  <div>
    <h1 class="text-h4 mb-6">Шаблоны документов</h1>
    <v-card>
      <v-list>
        <v-list-item v-for="template in templates" :key="template.id">
          <v-list-item-title>{{ template.name }}</v-list-item-title>
          <v-list-item-subtitle>{{ template.description }}</v-list-item-subtitle>
          <template v-slot:append>
            <v-btn color="primary" @click="generateDocument(template.id)">Генерировать</v-btn>
          </template>
        </v-list-item>
      </v-list>
    </v-card>
    <v-dialog v-model="generateDialog" max-width="400">
      <v-card>
        <v-card-title>Выберите дело</v-card-title>
        <v-card-text>
          <v-select v-model="selectedCase" :items="cases" item-title="case_number" item-value="id" label="Дело"></v-select>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="generateDialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="confirmGenerate" :loading="generating">Генерировать</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const templates = ref([])
const cases = ref([])
const generateDialog = ref(false)
const selectedTemplate = ref(null)
const selectedCase = ref(null)
const generating = ref(false)

async function generateDocument(templateId) {
  selectedTemplate.value = templateId
  generateDialog.value = true
  const res = await api.cases.getAll({ size: 100 })
  cases.value = res.items
}

async function confirmGenerate() {
  if (!selectedCase.value) return
  generating.value = true
  try {
    const response = await api.templates.generate(selectedTemplate.value, selectedCase.value)
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'document.docx')
    document.body.appendChild(link)
    link.click()
    generateDialog.value = false
  } finally {
    generating.value = false
  }
}

onMounted(async () => {
  const res = await api.templates.getAll()
  templates.value = res.items
})
</script>
