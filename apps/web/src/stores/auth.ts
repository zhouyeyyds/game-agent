import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import * as authApi from '@/api/auth'
import type { User } from '@/api/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)
  const hasCheckedSession = ref(false)

  const isAuthenticated = computed(() => user.value !== null)

  async function fetchMe() {
    loading.value = true
    try {
      user.value = await authApi.fetchMe()
    } catch {
      user.value = null
    } finally {
      hasCheckedSession.value = true
      loading.value = false
    }
  }

  async function login(payload: authApi.AuthCredentials) {
    loading.value = true
    try {
      user.value = await authApi.login(payload)
      hasCheckedSession.value = true
    } finally {
      loading.value = false
    }
  }

  async function register(payload: authApi.RegisterPayload) {
    loading.value = true
    try {
      user.value = await authApi.register(payload)
      hasCheckedSession.value = true
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    loading.value = true
    try {
      await authApi.logout()
      user.value = null
      hasCheckedSession.value = true
    } finally {
      loading.value = false
    }
  }

  return {
    user,
    loading,
    hasCheckedSession,
    isAuthenticated,
    fetchMe,
    login,
    register,
    logout,
  }
})
