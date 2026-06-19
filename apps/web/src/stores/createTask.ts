import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface AgentLogItem {
  id: string
  level: 'debug' | 'info' | 'warning' | 'error'
  nodeName: string
  message: string
  createdAt: string
}

export interface GenerationTask {
  id: string
  status: 'pending' | 'running' | 'succeeded' | 'failed'
  currentStep: string
  resultGameId?: string | null
  resultManifestUrl?: string | null
  errorMessage?: string | null
}

export const useCreateTaskStore = defineStore('createTask', () => {
  const currentTask = ref<GenerationTask | null>(null)
  const logs = ref<AgentLogItem[]>([])

  function setTask(task: GenerationTask | null) {
    currentTask.value = task
  }

  function setLogs(nextLogs: AgentLogItem[]) {
    logs.value = nextLogs
  }

  function reset() {
    currentTask.value = null
    logs.value = []
  }

  return {
    currentTask,
    logs,
    setTask,
    setLogs,
    reset,
  }
})
