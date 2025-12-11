import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: 'cases',
        name: 'CaseList',
        component: () => import('@/views/cases/CaseList.vue')
      },
      {
        path: 'cases/new',
        name: 'CaseNew',
        component: () => import('@/views/cases/CaseForm.vue')
      },
      {
        path: 'cases/:id',
        name: 'CaseDetail',
        component: () => import('@/views/cases/CaseDetail.vue')
      },
      {
        path: 'cases/:id/edit',
        name: 'CaseEdit',
        component: () => import('@/views/cases/CaseForm.vue')
      },
      {
        path: 'documents',
        name: 'DocumentList',
        component: () => import('@/views/documents/DocumentList.vue')
      },
      {
        path: 'documents/upload',
        name: 'DocumentUpload',
        component: () => import('@/views/documents/DocumentUpload.vue')
      },
      {
        path: 'documents/:id',
        name: 'DocumentPreview',
        component: () => import('@/views/documents/DocumentPreview.vue')
      },
      {
        path: 'persons',
        name: 'PersonList',
        component: () => import('@/views/persons/PersonList.vue')
      },
      {
        path: 'persons/new',
        name: 'PersonNew',
        component: () => import('@/views/persons/PersonForm.vue')
      },
      {
        path: 'persons/:id/edit',
        name: 'PersonEdit',
        component: () => import('@/views/persons/PersonForm.vue')
      },
      {
        path: 'calendar',
        name: 'Calendar',
        component: () => import('@/views/Calendar.vue')
      },
      {
        path: 'legal-acts',
        name: 'LegalActList',
        component: () => import('@/views/legal-acts/LegalActList.vue')
      },
      {
        path: 'templates',
        name: 'TemplateList',
        component: () => import('@/views/templates/TemplateList.vue')
      },
      {
        path: 'search',
        name: 'Search',
        component: () => import('@/views/Search.vue')
      },
      {
        path: 'admin',
        name: 'Admin',
        component: () => import('@/views/admin/AdminPanel.vue'),
        meta: { requiresAdmin: true }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Navigation guard для проверки аутентификации
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)

  if (requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (requiresAdmin && authStore.user?.role !== 'admin') {
    next({ name: 'Dashboard' })
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
