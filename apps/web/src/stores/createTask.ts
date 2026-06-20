import { defineStore } from 'pinia'
import { ref } from 'vue'

import { unpublishGame, updateGame } from '@/api/games'
import {
  cancelTask,
  createGenerationTask,
  deleteTask,
  fetchTask,
  fetchTaskLogs,
  fetchTasks,
  publishTask,
  retryTask,
  type AgentLogResponse,
  type CreateTaskPayload,
  type GenerationTaskResponse,
  type PublishGamePayload,
} from '@/api/tasks'

const terminalStatuses = new Set<GenerationTaskResponse['status']>(['succeeded', 'failed', 'canceled'])

export const useCreateTaskStore = defineStore('createTask', () => {
  const currentTask = ref<GenerationTaskResponse | null>(null)
  const tasks = ref<GenerationTaskResponse[]>([])
  const logs = ref<AgentLogResponse[]>([])
  const loading = ref(false)
  const historyLoading = ref(false)
  const publishing = ref(false)
  const savingPublishInfo = ref(false)
  const unpublishingGame = ref(false)
  const canceling = ref(false)
  const retrying = ref(false)
  const deletingTaskId = ref<string | null>(null)
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

  async function publishCurrentTask(payload: PublishGamePayload) {
    if (!currentTask.value) return null
    publishing.value = true
    error.value = null
    try {
      currentTask.value = await publishTask(currentTask.value.id, payload)
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

  async function saveCurrentGameInfo(payload: PublishGamePayload) {
    const gameId = currentTask.value?.result.gameId
    if (!currentTask.value || !gameId) return null
    savingPublishInfo.value = true
    error.value = null
    try {
      await updateGame(gameId, payload)
      currentTask.value = await fetchTask(currentTask.value.id)
      await loadHistory()
      return currentTask.value
    } catch (caught) {
      error.value = caught instanceof Error ? caught.message : '保存发布信息失败'
      throw caught
    } finally {
      savingPublishInfo.value = false
    }
  }

  async function unpublishCurrentGame() {
    const gameId = currentTask.value?.result.gameId
    if (!currentTask.value || !gameId) return null
    unpublishingGame.value = true
    error.value = null
    try {
      await unpublishGame(gameId)
      currentTask.value = await fetchTask(currentTask.value.id)
      await loadHistory()
      return currentTask.value
    } catch (caught) {
      error.value = caught instanceof Error ? caught.message : '下架游戏失败'
      throw caught
    } finally {
      unpublishingGame.value = false
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

  async function deleteTaskById(taskId: string) {
    deletingTaskId.value = taskId
    error.value = null
    try {
      await deleteTask(taskId)
      tasks.value = tasks.value.filter((task) => task.id !== taskId)
      if (currentTask.value?.id === taskId) {
        stopPolling()
        currentTask.value = null
        logs.value = []
      }
      return true
    } catch (caught) {
      error.value = caught instanceof Error ? caught.message : '删除任务失败'
      throw caught
    } finally {
      deletingTaskId.value = null
    }
  }

  function reset() {
    stopPolling()
    currentTask.value = null
    logs.value = []
    loading.value = false
    publishing.value = false
    savingPublishInfo.value = false
    unpublishingGame.value = false
    canceling.value = false
    retrying.value = false
    deletingTaskId.value = null
    error.value = null
  }

  return {
    currentTask,
    tasks,
    logs,
    loading,
    historyLoading,
    publishing,
    savingPublishInfo,
    unpublishingGame,
    canceling,
    retrying,
    deletingTaskId,
    error,
    startTask,
    loadHistory,
    selectTask,
    refreshTask,
    refreshLogs,
    pollTask,
    publishCurrentTask,
    saveCurrentGameInfo,
    unpublishCurrentGame,
    cancelCurrentTask,
    retryTaskById,
    deleteTaskById,
    stopPolling,
    reset,
  }
})
