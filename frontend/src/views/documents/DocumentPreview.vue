<template>
  <div>
    <v-row class="mb-4" v-if="document">
      <v-col>
        <h1 class="text-h4">{{ document.file_name }}</h1>
        <p class="text-subtitle-1">
          Размер: {{ formatFileSize(document.file_size) }} |
          Загружен: {{ formatDate(document.created_at) }}
        </p>
      </v-col>
      <v-col class="text-right">
        <v-btn variant="text" to="/documents">
          <v-icon start>mdi-arrow-left</v-icon>
          Назад
        </v-btn>
        <v-btn
          color="primary"
          :href="documentsStore.getDownloadUrl($route.params.id)"
          target="_blank"
        >
          <v-icon start>mdi-download</v-icon>
          Скачать
        </v-btn>
        <v-btn
          v-if="!document.ocr_text"
          color="secondary"
          @click="runOcr"
          :loading="ocrLoading"
        >
          <v-icon start>mdi-text-recognition</v-icon>
          Запустить OCR
        </v-btn>
      </v-col>
    </v-row>

    <v-row v-if="document">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>Предпросмотр</v-card-title>
          <v-card-text>
            <iframe
              v-if="isPdf"
              :src="documentsStore.getPreviewUrl($route.params.id)"
              style="width:100%;height:800px;border:none"
            ></iframe>
            <v-img
              v-else-if="isImage"
              :src="documentsStore.getPreviewUrl($route.params.id)"
              max-height="800"
              contain
            ></v-img>
            <div v-else class="text-center pa-8">
              <v-icon size="64">mdi-file</v-icon>
              <p class="mt-4">Предпросмотр недоступен для этого типа файла</p>
              <v-btn
                color="primary"
                :href="documentsStore.getDownloadUrl($route.params.id)"
                target="_blank"
                class="mt-4"
              >
                Скачать файл
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card class="mb-4">
          <v-card-title>Информация</v-card-title>
          <v-card-text>
            <v-list density="compact">
              <v-list-item>
                <v-list-item-title>Тип файла</v-list-item-title>
                <v-list-item-subtitle>{{ document.file_type }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item v-if="document.case_id">
                <v-list-item-title>Дело</v-list-item-title>
                <v-list-item-subtitle>
                  <router-link :to="`/cases/${document.case_id}`">
                    Перейти к делу
                  </router-link>
                </v-list-item-subtitle>
              </v-list-item>
              <v-list-item v-if="document.description">
                <v-list-item-title>Описание</v-list-item-title>
                <v-list-item-subtitle>{{ document.description }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>

        <v-card v-if="document.ocr_text">
          <v-card-title>Распознанный текст (OCR)</v-card-title>
          <v-card-text>
            <div class="ocr-text">{{ document.ocr_text }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <div v-else class="text-center pa-8">
      <v-progress-circular indeterminate size="64"></v-progress-circular>
      <p class="mt-4">Загрузка документа...</p>
    </div>

    <v-snackbar v-model="snackbar" :color="snackbarColor">
      {{ snackbarText }}
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useDocumentsStore } from '@/stores/documents'
import { format } from 'date-fns'

const route = useRoute()
const documentsStore = useDocumentsStore()

const document = ref(null)
const ocrLoading = ref(false)
const snackbar = ref(false)
const snackbarText = ref('')
const snackbarColor = ref('success')

const isPdf = computed(() => {
  return document.value?.file_name?.toLowerCase().endsWith('.pdf')
})

const isImage = computed(() => {
  const name = document.value?.file_name?.toLowerCase() || ''
  return name.endsWith('.jpg') || name.endsWith('.jpeg') || name.endsWith('.png')
})

function formatFileSize(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

function formatDate(date) {
  return format(new Date(date), 'dd.MM.yyyy HH:mm')
}

async function runOcr() {
  ocrLoading.value = true
  try {
    await documentsStore.runOcr(route.params.id)
    document.value = await documentsStore.fetchDocument(route.params.id)

    snackbarText.value = 'OCR завершён успешно'
    snackbarColor.value = 'success'
    snackbar.value = true
  } catch (error) {
    snackbarText.value = `Ошибка OCR: ${error.message}`
    snackbarColor.value = 'error'
    snackbar.value = true
  } finally {
    ocrLoading.value = false
  }
}

onMounted(async () => {
  document.value = await documentsStore.fetchDocument(route.params.id)
})
</script>

<style scoped>
.ocr-text {
  max-height: 400px;
  overflow-y: auto;
  white-space: pre-wrap;
  font-family: monospace;
  font-size: 0.875rem;
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
}
</style>
