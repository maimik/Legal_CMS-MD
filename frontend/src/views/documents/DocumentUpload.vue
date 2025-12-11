<template>
  <div>
    <h1 class="text-h4 mb-6">Загрузка документа</h1>

    <v-card>
      <v-card-text>
        <v-file-input
          v-model="files"
          label="Выберите файлы"
          multiple
          chips
          show-size
          accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.txt"
          prepend-icon="mdi-paperclip"
        ></v-file-input>

        <div
          class="drop-zone mt-4"
          @drop.prevent="handleDrop"
          @dragover.prevent
          @dragenter.prevent="dragActive = true"
          @dragleave.prevent="dragActive = false"
          :class="{ 'drag-active': dragActive }"
        >
          <v-icon size="64" color="primary">mdi-cloud-upload</v-icon>
          <p class="text-h6 mt-2">Перетащите файлы сюда</p>
          <p class="text-caption">или используйте кнопку выбора выше</p>
        </div>

        <v-select
          v-model="caseId"
          :items="cases"
          item-title="case_number"
          item-value="id"
          label="Связать с делом (опционально)"
          clearable
          class="mt-4"
        ></v-select>

        <v-textarea
          v-model="description"
          label="Описание"
          rows="3"
        ></v-textarea>

        <v-checkbox
          v-model="runOcrAfterUpload"
          label="Запустить OCR автоматически (для PDF)"
        ></v-checkbox>
      </v-card-text>

      <v-card-actions>
        <v-btn variant="text" @click="$router.back()">Отмена</v-btn>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          @click="uploadFiles"
          :loading="uploading"
          :disabled="!files || files.length === 0"
        >
          Загрузить ({{ files ? files.length : 0 }})
        </v-btn>
      </v-card-actions>
    </v-card>

    <v-snackbar v-model="snackbar" :color="snackbarColor">
      {{ snackbarText }}
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDocumentsStore } from '@/stores/documents'
import api from '@/api'

const router = useRouter()
const documentsStore = useDocumentsStore()

const files = ref([])
const caseId = ref(null)
const description = ref('')
const runOcrAfterUpload = ref(true)
const uploading = ref(false)
const dragActive = ref(false)
const cases = ref([])

const snackbar = ref(false)
const snackbarText = ref('')
const snackbarColor = ref('success')

function handleDrop(event) {
  dragActive.value = false
  const droppedFiles = Array.from(event.dataTransfer.files)
  files.value = [...(files.value || []), ...droppedFiles]
}

async function uploadFiles() {
  if (!files.value || files.value.length === 0) return

  uploading.value = true
  let successCount = 0

  try {
    for (const file of files.value) {
      const formData = new FormData()
      formData.append('file', file)
      if (caseId.value) formData.append('case_id', caseId.value)
      if (description.value) formData.append('description', description.value)
      if (runOcrAfterUpload.value) formData.append('run_ocr', 'true')

      await documentsStore.uploadDocument(formData)
      successCount++
    }

    snackbarText.value = `Успешно загружено: ${successCount} файл(ов)`
    snackbarColor.value = 'success'
    snackbar.value = true

    setTimeout(() => {
      router.push('/documents')
    }, 1500)
  } catch (error) {
    snackbarText.value = `Ошибка загрузки: ${error.message}`
    snackbarColor.value = 'error'
    snackbar.value = true
  } finally {
    uploading.value = false
  }
}

onMounted(async () => {
  try {
    const res = await api.cases.getAll({ size: 100 })
    cases.value = res.items
  } catch (error) {
    console.error('Failed to load cases:', error)
  }
})
</script>

<style scoped>
.drop-zone {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 60px 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.drop-zone:hover {
  border-color: #1976D2;
  background-color: #f5f5f5;
}

.drop-zone.drag-active {
  border-color: #1976D2;
  background-color: #e3f2fd;
}
</style>
