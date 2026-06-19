import { apiRequest } from './client'

export interface CreateTaskPayload {
  ideaText: string
  assetIds: string[]
}

export interface TaskResult {
  gameId: string | null
  manifestUrl: string | null
}

export interface GenerationTaskResponse {
  id: string
  status: 'pending' | 'running' | 'succeeded' | 'failed'
  currentStep: string
  ideaText: string
  assetIds: string[]
  result: TaskResult
  errorMessage: string | null
}

export interface AgentLogResponse {
  id: string
  level: 'debug' | 'info' | 'warning' | 'error'
  nodeName: string
  message: string
  createdAt: string
}

export function createGenerationTask(payload: CreateTaskPayload) {
  return apiRequest<GenerationTaskResponse>('/api/generation-tasks', {
    method: 'POST',
    data: payload,
  })
}

export function fetchTask(taskId: string) {
  return apiRequest<GenerationTaskResponse>(`/api/generation-tasks/${taskId}`)
}

export function fetchTaskLogs(taskId: string) {
  return apiRequest<AgentLogResponse[]>(`/api/generation-tasks/${taskId}/logs`)
}

export function publishTask(taskId: string) {
  return apiRequest<GenerationTaskResponse>(`/api/generation-tasks/${taskId}/publish`, {
    method: 'POST',
  })
}
