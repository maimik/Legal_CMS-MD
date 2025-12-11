<template>
  <div>
    <h1 class="text-h4 mb-6">Календарь событий</h1>
    <v-card>
      <v-card-text>
        <v-date-picker v-model="selectedDate" :events="eventDates" @update:modelValue="loadEvents"></v-date-picker>
        <v-divider class="my-4"></v-divider>
        <h3 class="mb-4">События на {{ formatDate(selectedDate) }}</h3>
        <v-list v-if="events.length">
          <v-list-item v-for="event in events" :key="event.id">
            <v-list-item-title>{{ event.description }}</v-list-item-title>
            <v-list-item-subtitle>{{ event.event_type }} | {{ formatTime(event.event_date) }}</v-list-item-subtitle>
          </v-list-item>
        </v-list>
        <div v-else class="text-center text-medium-emphasis py-4">Нет событий</div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { format } from 'date-fns'
import api from '@/api'

const selectedDate = ref(new Date())
const events = ref([])
const eventDates = ref([])

async function loadEvents() {
  const res = await api.events.getAll({ date: formatDate(selectedDate.value) })
  events.value = res.items
}

function formatDate(date) {
  return format(new Date(date), 'yyyy-MM-dd')
}

function formatTime(date) {
  return format(new Date(date), 'HH:mm')
}

onMounted(loadEvents)
</script>
