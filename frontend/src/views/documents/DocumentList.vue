<template>
  <div>
    <v-row class="mb-4">
      <v-col>
        <h1 class="text-h4">Документы</h1>
      </v-col>
      <v-col class="text-right">
        <v-btn color="primary" to="/documents/upload">
          <v-icon start>mdi-upload</v-icon>
          Загрузить документ
        </v-btn>
      </v-col>
    </v-row>

    <v-card>
      <v-card-title>
        <v-text-field
          v-model="search"
          prepend-inner-icon="mdi-magnify"
          label="Поиск по названию"
          single-line
          hide-details
          clearable
          @input="handleSearch"
        ></v-text-field>
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="documentsStore.documents"
        :loading="documentsStore.loading"
        :items-per-page="documentsStore.pagination.size"
        :page="documentsStore.pagination.page"
        :items-length="documentsStore.pagination.total"
        @update:page="handlePageChange"
      >
        <template v-slot:item.file_name="{ item }">
          <v-icon start>{{ getFileIcon(item.file_name) }}</v-icon>
          {{ item.file_name }}
        </template>
        <template v-slot:item.file_size="{ item }">
          {{ formatFileSize(item.file_size) }}
        </template>
        <template v-slot:item.created_at="{ item }">
          {{ formatDate(item.created_at) }}
        </template>
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon="mdi-eye"
            size="small"
            variant="text"
            :to="`/documents/${item.id}`"
          ></v-btn>
          <v-btn
            icon="mdi-download"
            size="small"
            variant="text"
            :href="documentsStore.getDownloadUrl(item.id)"
            target="_blank"
          ></v-btn>
          <v-btn
            v-if="!item.ocr_text"
            icon="mdi-text-recognition"
            size="small"
            variant="text"
            color="primary"
            @click="runOcr(item.id)"
            title="Запустить OCR"
          ></v-btn>
          <v-btn
            v-if="authStore.isAdmin"
            icon="mdi-delete"
            size="small"
            variant="text"
            color="error"
            @click="confirmDelete(item)"
          ></v-btn>
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-model="deleteDialog" max-width="500">
      <v-card>
        <v-card-title>Удалить документ?</v-card-title>
        <v-card-text>
          Вы действительно хотите удалить "{{ documentToDelete?.file_name }}"?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="deleteDialog = false">Отмена</v-btn>
          <v-btn color="error" @click="deleteDocument">Удалить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useDocumentsStore } from '@/stores/documents'
import { useAuthStore } from '@/stores/auth'
import { format } from 'date-fns'

const documentsStore = useDocumentsStore()
const authStore = useAuthStore()

const search = ref('')
const deleteDialog = ref(false)
const documentToDelete = ref(null)

const headers = [
  { title: 'Файл', key: 'file_name', sortable: true },
  { title: 'Размер', key: 'file_size', sortable: true },
  { title: 'Загружен', key: 'created_at', sortable: true },
  { title: 'Действия', key: 'actions', sortable: false, align: 'end' }
]

function getFileIcon(filename) {
  const ext = filename.split('.').pop().toLowerCase()
  const icons = {
    pdf: 'mdi-file-pdf-box',
    doc: 'mdi-file-word',
    docx: 'mdi-file-word',
    jpg: 'mdi-file-image',
    jpeg: 'mdi-file-image',
    png: 'mdi-file-image',
    txt: 'mdi-file-document'
  }
  return icons[ext] || 'mdi-file'
}

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

async function loadDocuments() {
  const params = {}
  if (search.value) params.search = search.value
  await documentsStore.fetchDocuments(params)
}

let searchTimeout
function handleSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadDocuments()
  }, 500)
}

function handlePageChange(page) {
  documentsStore.setPage(page)
  loadDocuments()
}

async function runOcr(id) {
  try {
    await documentsStore.runOcr(id)
    loadDocuments()
  } catch (error) {
    console.error('OCR error:', error)
  }
}

function confirmDelete(item) {
  documentToDelete.value = item
  deleteDialog.value = true
}

async function deleteDocument() {
  try {
    await documentsStore.deleteDocument(documentToDelete.value.id)
    deleteDialog.value = false
    documentToDelete.value = null
  } catch (error) {
    console.error('Delete error:', error)
  }
}

onMounted(() => {
  loadDocuments()
})
</script>
