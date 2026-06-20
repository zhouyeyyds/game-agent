import { defineStore } from 'pinia'
import { ref } from 'vue'

import {
  createGenerationTask,
  fetchTask,
  fetchTaskLogs,
  publishTask,
  type AgentLogResponse,
  type CreateTaskPayload,
  type GenerationTaskResponse,
} from '@/api/tasks'

export const useCreateTaskStore = defineStore('createTask', () => {
  const currentTask = ref<GenerationTaskResponse | null>(null)
  const logs = ref<AgentLogResponse[]>([])
  const loading = ref(false)
  const publishing = ref(false)
  const error = ref<string | null>(null)
  const pollTimer = ref<number | null>(null)

  function stopPolling() {
    if (pollTimer.value !== null) {
      window.clearInterval(pollTimer.value)
      pollTimer.value = null
    }
  }

  async function refreshLogs(taskId: string) {
    logs.value = await fetchTaskLogs(taskId)
  }

  async function refreshTask(taskId: string) {
    currentTask.value = await fetchTask(taskId)
    await refreshLogs(taskId)
    if (currentTask.value.status === 'succeeded' || currentTask.value.status === 'failed') {
      stopPolling()
    }
  }

  function pollTask(taskId: string) {
    stopPolling()
    pollTimer.value = window.setInterval(() => {
      refreshTask(taskId).catch((caught) => {
        error.value = caught instanceof Error ? caught.message : '任务轮询失败'
        stopPolling()
      })
    }, 1200)
  }

  async function startTask(payload: CreateTaskPayload) {
    loading.value = true
    error.value = null
    logs.value = []
    try {
      currentTask.value = await createGenerationTask(payload)
      await refreshLogs(currentTask.value.id)
      pollTask(currentTask.value.id)
    } catch (caught) {
      error.value = caught instanceof Error ? caught.message : '创建任务失败'
      throw caught
    } finally {
      loading.value = false
    }
  }

  async function publishCurrentTask() {
    if (!currentTask.value) return null
    publishing.value = true
    error.value = null
    try {
      currentTask.value = await publishTask(currentTask.value.id)
      await refreshLogs(currentTask.value.id)
      return currentTask.value
    } catch (caught) {
      error.value = caught instanceof Error ? caught.message : '发布失败'
      throw caught
    } finally {
      publishing.value = false
    }
  }

  function reset() {
    stopPolling()
    currentTask.value = null
    logs.value = []
    loading.value = false
    publishing.value = false
    error.value = null
  }

  return {
    currentTask,
    logs,
    loading,
    publishing,
    error,
    startTask,
    refreshTask,
    refreshLogs,
    pollTask,
    publishCurrentTask,
    stopPolling,
    reset,
  }
})
