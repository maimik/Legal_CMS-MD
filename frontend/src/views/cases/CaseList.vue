<template>
  <div>
    <v-row class="mb-4">
      <v-col>
        <h1 class="text-h4">Дела</h1>
      </v-col>
      <v-col class="text-right">
        <v-btn color="primary" to="/cases/new">
          <v-icon start>mdi-plus</v-icon>
          Новое дело
        </v-btn>
      </v-col>
    </v-row>

    <v-card>
      <v-card-title>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="search"
              prepend-inner-icon="mdi-magnify"
              label="Поиск"
              single-line
              hide-details
              clearable
              @input="handleSearch"
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="statusFilter"
              :items="statusOptions"
              label="Статус"
              clearable
              hide-details
              @update:modelValue="loadCases"
            ></v-select>
          </v-col>
        </v-row>
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="casesStore.cases"
        :loading="casesStore.loading"
        :items-per-page="casesStore.pagination.size"
        :page="casesStore.pagination.page"
        :items-length="casesStore.pagination.total"
        @update:page="handlePageChange"
        @click:row="viewCase"
        class="cursor-pointer"
      >
        <template v-slot:item.case_status="{ item }">
          <v-chip :color="getStatusColor(item.case_status)" size="small">
            {{ getStatusText(item.case_status) }}
          </v-chip>
        </template>
        <template v-slot:item.created_at="{ item }">
          {{ formatDate(item.created_at) }}
        </template>
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon="mdi-pencil"
            size="small"
            variant="text"
            @click.stop="editCase(item.id)"
          ></v-btn>
          <v-btn
            v-if="authStore.isAdmin"
            icon="mdi-delete"
            size="small"
            variant="text"
            color="error"
            @click.stop="confirmDelete(item)"
          ></v-btn>
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-model="deleteDialog" max-width="500">
      <v-card>
        <v-card-title>Удалить дело?</v-card-title>
        <v-card-text>
          Вы действительно хотите удалить дело "{{ caseToDelete?.case_number }}"?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="deleteDialog = false">Отмена</v-btn>
          <v-btn color="error" @click="deleteCase">Удалить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCasesStore } from '@/stores/cases'
import { useAuthStore } from '@/stores/auth'
import { format } from 'date-fns'

const router = useRouter()
const casesStore = useCasesStore()
const authStore = useAuthStore()

const search = ref('')
const statusFilter = ref(null)
const deleteDialog = ref(false)
const caseToDelete = ref(null)

const headers = [
  { title: 'Номер дела', key: 'case_number', sortable: true },
  { title: 'Название', key: 'title', sortable: true },
  { title: 'Статус', key: 'case_status', sortable: true },
  { title: 'Создано', key: 'created_at', sortable: true },
  { title: 'Действия', key: 'actions', sortable: false, align: 'end' }
]

const statusOptions = [
  { title: 'Новое', value: 'new' },
  { title: 'В работе', value: 'in_progress' },
  { title: 'Приостановлено', value: 'suspended' },
  { title: 'Завершено', value: 'completed' },
  { title: 'Архив', value: 'archived' }
]

function getStatusColor(status) {
  const colors = {
    new: 'blue',
    in_progress: 'orange',
    suspended: 'grey',
    completed: 'green',
    archived: 'purple'
  }
  return colors[status] || 'grey'
}

function getStatusText(status) {
  const texts = {
    new: 'Новое',
    in_progress: 'В работе',
    suspended: 'Приостановлено',
    completed: 'Завершено',
    archived: 'Архив'
  }
  return texts[status] || status
}

function formatDate(date) {
  return format(new Date(date), 'dd.MM.yyyy')
}

async function loadCases() {
  const params = {}
  if (search.value) params.search = search.value
  if (statusFilter.value) params.case_status = statusFilter.value
  await casesStore.fetchCases(params)
}

let searchTimeout
function handleSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadCases()
  }, 500)
}

function handlePageChange(page) {
  casesStore.setPage(page)
  loadCases()
}

function viewCase(event, { item }) {
  router.push(`/cases/${item.id}`)
}

function editCase(id) {
  router.push(`/cases/${id}/edit`)
}

function confirmDelete(item) {
  caseToDelete.value = item
  deleteDialog.value = true
}

async function deleteCase() {
  try {
    await casesStore.deleteCase(caseToDelete.value.id)
    deleteDialog.value = false
    caseToDelete.value = null
  } catch (error) {
    console.error('Delete error:', error)
  }
}

onMounted(() => {
  loadCases()
})
</script>

<style scoped>
.cursor-pointer >>> tbody tr {
  cursor: pointer;
}
</style>
