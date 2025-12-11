<template>
  <div>
    <h1 class="text-h4 mb-6">Главная панель</h1>
    
    <v-row>
      <v-col cols="12" md="3">
        <v-card color="primary">
          <v-card-text>
            <div class="text-h3">{{ stats.total_cases || 0 }}</div>
            <div>Всего дел</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card color="success">
          <v-card-text>
            <div class="text-h3">{{ stats.active_cases || 0 }}</div>
            <div>Активных дел</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card color="info">
          <v-card-text>
            <div class="text-h3">{{ stats.total_documents || 0 }}</div>
            <div>Документов</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card color="warning">
          <v-card-text>
            <div class="text-h3">{{ stats.upcoming_events || 0 }}</div>
            <div>Предстоящих событий</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-4">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>Последние дела</v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item
                v-for="case_item in recentCases"
                :key="case_item.id"
                :to="`/cases/${case_item.id}`"
              >
                <v-list-item-title>{{ case_item.case_number }} - {{ case_item.title }}</v-list-item-title>
                <v-list-item-subtitle>{{ case_item.case_status }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Предстоящие события</v-card-title>
          <v-card-text>
            <v-list density="compact">
              <v-list-item v-for="event in upcomingEvents" :key="event.id">
                <v-list-item-title>{{ event.description }}</v-list-item-title>
                <v-list-item-subtitle>{{ formatDate(event.event_date) }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import { format } from 'date-fns'

const stats = ref({})
const recentCases = ref([])
const upcomingEvents = ref([])

async function loadDashboard() {
  try {
    const [statsRes, casesRes, eventsRes] = await Promise.all([
      api.reports.getStatistics(),
      api.cases.getAll({ page: 1, size: 5 }),
      api.events.getUpcomingWeek()
    ])
    stats.value = statsRes
    recentCases.value = casesRes.items
    upcomingEvents.value = eventsRes
  } catch (error) {
    console.error('Dashboard load error:', error)
  }
}

function formatDate(date) {
  return format(new Date(date), 'dd.MM.yyyy HH:mm')
}

onMounted(() => {
  loadDashboard()
})
</script>
