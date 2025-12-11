# Frontend Completion Guide

## ✅ Что уже создано (70% Frontend готово)

### Инфраструктура (100%)
- ✅ package.json - зависимости
- ✅ vite.config.js - конфигурация Vite
- ✅ index.html - главный HTML
- ✅ src/main.js - точка входа
- ✅ src/App.vue - главный компонент
- ✅ src/assets/main.css - стили
- ✅ src/plugins/vuetify.js - Vuetify 3

### Router (100%)
- ✅ src/router/index.js - все маршруты настроены

### API Client (100%)
- ✅ src/api/client.js - axios с interceptors
- ✅ src/api/auth.js
- ✅ src/api/cases.js
- ✅ src/api/documents.js
- ✅ src/api/persons.js
- ✅ src/api/events.js
- ✅ src/api/legal-acts.js
- ✅ src/api/templates.js
- ✅ src/api/search.js
- ✅ src/api/reports.js
- ✅ src/api/admin.js
- ✅ src/api/index.js

### Pinia Stores (100%)
- ✅ src/stores/auth.js - аутентификация
- ✅ src/stores/cases.js - дела
- ✅ src/stores/documents.js - документы

### Layouts (100%)
- ✅ src/layouts/DefaultLayout.vue - основной layout с навигацией

### Views - Базовые (100%)
- ✅ src/views/Login.vue - страница входа
- ✅ src/views/Dashboard.vue - главная панель
- ✅ src/views/NotFound.vue - 404

## ⏳ Что осталось создать (30% Frontend)

### Views - Дела
- ⏳ src/views/cases/CaseList.vue
- ⏳ src/views/cases/CaseDetail.vue
- ⏳ src/views/cases/CaseForm.vue

### Views - Документы
- ⏳ src/views/documents/DocumentList.vue
- ⏳ src/views/documents/DocumentUpload.vue
- ⏳ src/views/documents/DocumentPreview.vue

### Views - Персоны
- ⏳ src/views/persons/PersonList.vue
- ⏳ src/views/persons/PersonForm.vue

### Views - Остальное
- ⏳ src/views/Calendar.vue
- ⏳ src/views/Search.vue
- ⏳ src/views/legal-acts/LegalActList.vue
- ⏳ src/views/templates/TemplateList.vue
- ⏳ src/views/admin/AdminPanel.vue

## 🚀 Как завершить Frontend

### Шаг 1: Установка зависимостей
```bash
cd frontend
npm install
```

### Шаг 2: Создание недостающих компонентов

Все недостающие компоненты следуют одному паттерну:

**Список (List):**
```vue
<template>
  <div>
    <v-data-table
      :headers="headers"
      :items="items"
      :loading="loading"
      @click:row="viewItem"
    >
    </v-data-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const items = ref([])
const loading = ref(false)

async function loadItems() {
  loading.value = true
  try {
    const response = await api.MODULE.getAll()
    items.value = response.items
  } finally {
    loading.value = false
  }
}

onMounted(() => loadItems())
</script>
```

**Форма (Form):**
```vue
<template>
  <v-form @submit.prevent="handleSubmit">
    <v-text-field v-model="form.field" label="Field"></v-text-field>
    <v-btn type="submit" :loading="loading">Сохранить</v-btn>
  </v-form>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()
const form = ref({})
const loading = ref(false)

async function handleSubmit() {
  loading.value = true
  try {
    await api.MODULE.create(form.value)
    router.push({ name: 'ModuleList' })
  } finally {
    loading.value = false
  }
}
</script>
```

### Шаг 3: Копирование паттернов

Для быстрого завершения:

1. **CaseList.vue** - копировать структуру из Dashboard, использовать `useCasesStore`
2. **CaseDetail.vue** - показать детали дела, использовать `fetchCase(id)`
3. **CaseForm.vue** - форма создания/редактирования дела
4. **DocumentList.vue** - таблица документов
5. **DocumentUpload.vue** - drag-and-drop загрузка с `useDocumentsStore`
6. **DocumentPreview.vue** - показать PDF через `getPreviewUrl()`
7. **PersonList.vue** - таблица персон
8. **PersonForm.vue** - форма персоны с валидацией IDNP
9. **Calendar.vue** - календарь событий
10. **Search.vue** - глобальный поиск с результатами
11. **LegalActList.vue** - список законов
12. **TemplateList.vue** - список шаблонов
13. **AdminPanel.vue** - управление пользователями

### Шаг 4: Запуск
```bash
npm run dev
```

Откроется http://localhost:3000

### Шаг 5: Тестирование

1. Проверить вход (Login)
2. Проверить навигацию
3. Проверить CRUD операции для каждого модуля

## 📋 Чеклист завершения

- [ ] Установить npm зависимости
- [ ] Создать views/cases/*.vue (3 файла)
- [ ] Создать views/documents/*.vue (3 файла)
- [ ] Создать views/persons/*.vue (2 файла)
- [ ] Создать views/Calendar.vue
- [ ] Создать views/Search.vue
- [ ] Создать views/legal-acts/*.vue
- [ ] Создать views/templates/*.vue
- [ ] Создать views/admin/*.vue
- [ ] Запустить `npm run dev`
- [ ] Протестировать все страницы
- [ ] Исправить ошибки

## 🎯 Оценка времени

- Создание views компонентов: 4-6 часов
- Тестирование и исправление: 2 часа
- **ИТОГО**: 6-8 часов до завершения Frontend

## 💡 Полезные команды

```bash
# Запуск dev сервера
npm run dev

# Сборка для production
npm run build

# Предпросмотр production сборки
npm run preview

# Lint
npm run lint
```

## 🐛 Типичные проблемы

1. **Ошибка "Cannot find module"** - проверить импорты в src/api/index.js
2. **401 Unauthorized** - проверить что backend запущен на :8000
3. **CORS ошибки** - проверить proxy в vite.config.js
4. **Vuetify компоненты не отображаются** - проверить vuetify plugin

---

**Статус:** Frontend 70% готов (инфраструктура и API полностью)
**Осталось:** Создать 13-15 view компонентов
**Время:** 6-8 часов работы
