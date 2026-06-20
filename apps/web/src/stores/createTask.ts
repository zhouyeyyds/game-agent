import { defineStore } from 'pinia'
import { ref } from 'vue'

import {
  cancelTask,
  createGenerationTask,
  fetchTask,
  fetchTaskLogs,
  fetchTasks,
  publishTask,
  retryTask,
  type AgentLogResponse,
  type CreateTaskPayload,
  type GenerationTaskResponse,
} from '@/api/tasks'

const terminalStatuses = new Set<GenerationTaskResponse['status']>(['succeeded', 'failed', 'canceled'])

export const useCreateTaskStore = defineStore('createTask', () => {
  const currentTask = ref<GenerationTaskResponse | null>(null)
  const tasks = ref<GenerationTaskResponse[]>([])
  const logs = ref<AgentLogResponse[]>([])
  const loading = ref(false)
  const historyLoading = ref(false)
  const publishing = ref(false)
  const canceling = ref(false)
  const retrying = ref(false)
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
    if (terminalStatuses.has(currentTask.value.status)) {
      stopPolling()
    }
    await loadHistory()
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
      await loadHistory()
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
      await loadHistory()
      return currentTask.value
    } catch (caught) {
      error.value = caught instanceof Error ? caught.message : '发布失败'
      throw caught
    } finally {
      publishing.value = false
    }
  }

  async function loadHistory() {
    historyLoading.value = true
    try {
      tasks.value = await fetchTasks({ limit: 20 })
    } catch (caught) {
      error.value = caught instanceof Error ? caught.message : '加载任务历史失败'
      throw caught
    } finally {
      historyLoading.value = false
    }
  }

  async function selectTask(task: GenerationTaskResponse) {
    stopPolling()
    currentTask.value = task
    await refreshLogs(task.id)
    if (!terminalStatuses.has(task.status)) {
      pollTask(task.id)
    }
  }

  async function cancelCurrentTask() {
    if (!currentTask.value) return null
    canceling.value = true
    error.value = null
    try {
      currentTask.value = await cancelTask(currentTask.value.id)
      await refreshLogs(currentTask.value.id)
      stopPolling()
      await loadHistory()
      return currentTask.value
    } catch (caught) {
      error.value = caught instanceof Error ? caught.message : '取消任务失败'
      throw caught
    } finally {
      canceling.value = false
    }
  }

  async function retryTaskById(taskId: string) {
    retrying.value = true
    error.value = null
    try {
      currentTask.value = await retryTask(taskId)
      logs.value = []
      await refreshLogs(currentTask.value.id)
      await loadHistory()
      pollTask(currentTask.value.id)
      return currentTask.value
    } catch (caught) {
      error.value = caught instanceof Error ? caught.message : '重试任务失败'
      throw caught
    } finally {
      retrying.value = false
    }
  }

  function reset() {
    stopPolling()
    currentTask.value = null
    logs.value = []
    loading.value = false
    publishing.value = false
    canceling.value = false
    retrying.value = false
    error.value = null
  }

  return {
    currentTask,
    tasks,
    logs,
    loading,
    historyLoading,
    publishing,
    canceling,
    retrying,
    error,
    startTask,
    loadHistory,
    selectTask,
    refreshTask,
    refreshLogs,
    pollTask,
    publishCurrentTask,
    cancelCurrentTask,
    retryTaskById,
    stopPolling,
    reset,
  }
})
