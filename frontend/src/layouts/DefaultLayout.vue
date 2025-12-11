<template>
  <v-layout>
    <!-- App Bar -->
    <v-app-bar color="primary" prominent>
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>

      <v-toolbar-title>Legal CMS-MD</v-toolbar-title>

      <v-spacer></v-spacer>

      <!-- Search -->
      <v-text-field
        v-model="searchQuery"
        hide-details
        placeholder="Поиск..."
        prepend-inner-icon="mdi-magnify"
        variant="solo"
        density="compact"
        class="mr-4"
        style="max-width: 400px"
        @keyup.enter="goToSearch"
      ></v-text-field>

      <!-- User menu -->
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn icon v-bind="props">
            <v-icon>mdi-account-circle</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item>
            <v-list-item-title>{{ authStore.user?.full_name || authStore.user?.username }}</v-list-item-title>
            <v-list-item-subtitle>{{ authStore.user?.role === 'admin' ? 'Администратор' : 'Помощник' }}</v-list-item-subtitle>
          </v-list-item>
          <v-divider></v-divider>
          <v-list-item @click="handleLogout">
            <v-list-item-title>
              <v-icon start>mdi-logout</v-icon>
              Выход
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <!-- Navigation drawer -->
    <v-navigation-drawer v-model="drawer" temporary>
      <v-list>
        <v-list-item
          prepend-icon="mdi-view-dashboard"
          title="Главная"
          to="/"
        ></v-list-item>

        <v-list-item
          prepend-icon="mdi-briefcase"
          title="Дела"
          to="/cases"
        ></v-list-item>

        <v-list-item
          prepend-icon="mdi-file-document-multiple"
          title="Документы"
          to="/documents"
        ></v-list-item>

        <v-list-item
          prepend-icon="mdi-account-multiple"
          title="Персоны"
          to="/persons"
        ></v-list-item>

        <v-list-item
          prepend-icon="mdi-calendar"
          title="Календарь"
          to="/calendar"
        ></v-list-item>

        <v-list-item
          prepend-icon="mdi-gavel"
          title="Законодательство"
          to="/legal-acts"
        ></v-list-item>

        <v-list-item
          prepend-icon="mdi-file-document-edit"
          title="Шаблоны"
          to="/templates"
        ></v-list-item>

        <v-divider class="my-2"></v-divider>

        <v-list-item
          v-if="authStore.isAdmin"
          prepend-icon="mdi-cog"
          title="Администрирование"
          to="/admin"
        ></v-list-item>
      </v-list>
    </v-navigation-drawer>

    <!-- Main content -->
    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>
  </v-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const drawer = ref(false)
const searchQuery = ref('')

function goToSearch() {
  if (searchQuery.value.trim()) {
    router.push({ name: 'Search', query: { q: searchQuery.value } })
  }
}

async function handleLogout() {
  await authStore.logout()
  router.push({ name: 'Login' })
}
</script>
