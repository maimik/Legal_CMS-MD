<template>
  <div v-if="casesStore.currentCase">
    <v-row class="mb-4">
      <v-col>
        <h1 class="text-h4">{{ casesStore.currentCase.case_number }}</h1>
        <p class="text-subtitle-1">{{ casesStore.currentCase.title }}</p>
      </v-col>
      <v-col class="text-right">
        <v-btn variant="text" to="/cases">
          <v-icon start>mdi-arrow-left</v-icon>
          Назад
        </v-btn>
        <v-btn color="primary" :to="`/cases/${$route.params.id}/edit`">
          <v-icon start>mdi-pencil</v-icon>
          Редактировать
        </v-btn>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="8">
        <v-card class="mb-4">
          <v-card-title>Информация о деле</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="6"><strong>Статус:</strong> 
                <v-chip :color="getStatusColor(casesStore.currentCase.case_status)" size="small">
                  {{ getStatusText(casesStore.currentCase.case_status) }}
                </v-chip>
              </v-col>
              <v-col cols="6"><strong>Тип дела:</strong> {{ getCaseTypeText(casesStore.currentCase.case_type) }}</v-col>
              <v-col cols="6"><strong>Истец:</strong> {{ casesStore.currentCase.plaintiff }}</v-col>
              <v-col cols="6"><strong>Ответчик:</strong> {{ casesStore.currentCase.defendant }}</v-col>
              <v-col cols="6"><strong>Суд:</strong> {{ casesStore.currentCase.court_name }}</v-col>
              <v-col cols="6"><strong>Судья:</strong> {{ casesStore.currentCase.judge_name }}</v-col>
              <v-col cols="12"><strong>Описание:</strong><br>{{ casesStore.currentCase.description }}</v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <v-card>
          <v-card-title>История дела</v-card-title>
          <v-card-text>
            <v-timeline density="compact" v-if="casesStore.timeline.length">
              <v-timeline-item v-for="event in casesStore.timeline" :key="event.id" size="small">
                <div class="d-flex">
                  <strong class="me-4">{{ formatDate(event.created_at) }}</strong>
                  <div>{{ event.action }}</div>
                </div>
              </v-timeline-item>
            </v-timeline>
            <div v-else class="text-center text-medium-emphasis">Нет событий</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card class="mb-4">
          <v-card-title>Документы</v-card-title>
          <v-list>
            <v-list-item v-for="doc in documents" :key="doc.id">
              <v-list-item-title>{{ doc.file_name }}</v-list-item-title>
            </v-list-item>
          </v-list>
          <v-card-actions>
            <v-btn block variant="text" to="/documents/upload">Добавить документ</v-btn>
          </v-card-actions>
        </v-card>

        <v-card>
          <v-card-title>События</v-card-title>
          <v-list density="compact">
            <v-list-item v-for="event in events" :key="event.id">
              <v-list-item-title>{{ event.description }}</v-list-item-title>
              <v-list-item-subtitle>{{ formatDate(event.event_date) }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>
          <v-card-actions>
            <v-btn block variant="text" to="/calendar">Добавить событие</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </div>
  <div v-else class="text-center pa-4">
    <v-progress-circular indeterminate></v-progress-circular>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useCasesStore } from '@/stores/cases'
import { format } from 'date-fns'
import api from '@/api'

const route = useRoute()
const casesStore = useCasesStore()
const documents = ref([])
const events = ref([])

function getStatusColor(status) {
  const colors = { new: 'blue', in_progress: 'orange', suspended: 'grey', completed: 'green', archived: 'purple' }
  return colors[status] || 'grey'
}

function getStatusText(status) {
  const texts = { new: 'Новое', in_progress: 'В работе', suspended: 'Приостановлено', completed: 'Завершено', archived: 'Архив' }
  return texts[status] || status
}

function getCaseTypeText(type) {
  const types = { civil: 'Гражданское', criminal: 'Уголовное', administrative: 'Административное', other: 'Другое' }
  return types[type] || type
}

function formatDate(date) {
  return format(new Date(date), 'dd.MM.yyyy HH:mm')
}

async function loadData() {
  await casesStore.fetchCase(route.params.id)
  await casesStore.fetchTimeline(route.params.id)
  const docsRes = await api.documents.getAll({ case_id: route.params.id })
  documents.value = docsRes.items
  const eventsRes = await api.events.getAll({ case_id: route.params.id })
  events.value = eventsRes.items
}

onMounted(() => loadData())
</script>
