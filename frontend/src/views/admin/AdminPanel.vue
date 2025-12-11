<template>
  <div>
    <h1 class="text-h4 mb-6">Администрирование</h1>
    
    <v-tabs v-model="tab">
      <v-tab value="users">Пользователи</v-tab>
      <v-tab value="system">Система</v-tab>
      <v-tab value="audit">Аудит</v-tab>
    </v-tabs>

    <v-window v-model="tab" class="mt-4">
      <v-window-item value="users">
        <v-card>
          <v-card-title>Пользователи</v-card-title>
          <v-data-table :headers="[
            { title: 'Имя пользователя', key: 'username' },
            { title: 'ФИО', key: 'full_name' },
            { title: 'Email', key: 'email' },
            { title: 'Роль', key: 'role' },
            { title: 'Активен', key: 'is_active' }
          ]" :items="users" :loading="loadingUsers">
            <template v-slot:item.role="{ item }">
              <v-chip>{{ item.role === 'admin' ? 'Администратор' : 'Помощник' }}</v-chip>
            </template>
            <template v-slot:item.is_active="{ item }">
              <v-icon :color="item.is_active ? 'success' : 'error'">
                {{ item.is_active ? 'mdi-check' : 'mdi-close' }}
              </v-icon>
            </template>
          </v-data-table>
        </v-card>
      </v-window-item>

      <v-window-item value="system">
        <v-row>
          <v-col cols="12" md="6">
            <v-card>
              <v-card-title>Системная информация</v-card-title>
              <v-card-text v-if="systemInfo">
                <v-list density="compact">
                  <v-list-item><v-list-item-title>Всего дел:</v-list-item-title><v-list-item-subtitle>{{ systemInfo.total_cases }}</v-list-item-subtitle></v-list-item>
                  <v-list-item><v-list-item-title>Всего документов:</v-list-item-title><v-list-item-subtitle>{{ systemInfo.total_documents }}</v-list-item-subtitle></v-list-item>
                  <v-list-item><v-list-item-title>Ollama статус:</v-list-item-title><v-list-item-subtitle>{{ systemInfo.ollama_status }}</v-list-item-subtitle></v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="6">
            <v-card>
              <v-card-title>Резервное копирование</v-card-title>
              <v-card-text>
                <p class="mb-4">Создать резервную копию базы данных</p>
                <v-btn color="primary" @click="createBackup" :loading="backupLoading" block>
                  <v-icon start>mdi-database-export</v-icon>
                  Создать backup
                </v-btn>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-window-item>

      <v-window-item value="audit">
        <v-card>
          <v-card-title>Журнал аудита</v-card-title>
          <v-data-table :headers="[
            { title: 'Дата', key: 'created_at' },
            { title: 'Пользователь', key: 'user_id' },
            { title: 'Действие', key: 'action' },
            { title: 'Таблица', key: 'table_name' }
          ]" :items="auditLog" :loading="loadingAudit">
            <template v-slot:item.created_at="{ item }">{{ formatDate(item.created_at) }}</template>
          </v-data-table>
        </v-card>
      </v-window-item>
    </v-window>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { format } from 'date-fns'
import api from '@/api'

const tab = ref('users')
const users = ref([])
const loadingUsers = ref(false)
const systemInfo = ref(null)
const backupLoading = ref(false)
const auditLog = ref([])
const loadingAudit = ref(false)

async function loadUsers() {
  loadingUsers.value = true
  try {
    const res = await api.admin.getUsers()
    users.value = res.items
  } finally {
    loadingUsers.value = false
  }
}

async function loadSystemInfo() {
  systemInfo.value = await api.admin.getSystemInfo()
}

async function createBackup() {
  backupLoading.value = true
  try {
    await api.admin.createBackup()
    alert('Backup создан успешно')
  } finally {
    backupLoading.value = false
  }
}

async function loadAuditLog() {
  loadingAudit.value = true
  try {
    const res = await api.admin.getAuditLog({ size: 50 })
    auditLog.value = res.items
  } finally {
    loadingAudit.value = false
  }
}

function formatDate(date) {
  return format(new Date(date), 'dd.MM.yyyy HH:mm')
}

onMounted(() => {
  loadUsers()
  loadSystemInfo()
  loadAuditLog()
})
</script>
