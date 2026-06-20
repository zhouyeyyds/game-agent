import { createRouter, createWebHistory } from 'vue-router'

import CreatePage from '@/pages/CreatePage.vue'
import HomePage from '@/pages/HomePage.vue'
import LoginPage from '@/pages/LoginPage.vue'
import PlayPage from '@/pages/PlayPage.vue'
import RegisterPage from '@/pages/RegisterPage.vue'
import { useAuthStore } from '@/stores/auth'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomePage },
    { path: '/login', name: 'login', component: LoginPage, meta: { hideHeader: true } },
    { path: '/register', name: 'register', component: RegisterPage, meta: { hideHeader: true } },
    { path: '/create', name: 'create', component: CreatePage, meta: { requiresAuth: true } },
    { path: '/play/:gameId', name: 'play', component: PlayPage, props: true },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (!auth.hasCheckedSession) {
    await auth.fetchMe()
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  return true
})
