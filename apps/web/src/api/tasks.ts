import { apiRequest } from './client'

export interface CreateTaskPayload {
  ideaText: string
  assetIds: string[]
}

export interface TaskResult {
  gameId: string | null
  manifestUrl: string | null
  publishedAt: string | null
  title: string | null
  description: string | null
  coverUrl: string | null
  tags: string[]
}

export interface PublishGamePayload {
  title: string
  description: string
  coverUrl?: string | null
  tags: string[]
}

export interface GenerationTaskResponse {
  id: string
  status: 'pending' | 'running' | 'succeeded' | 'failed' | 'canceled'
  currentStep: string
  ideaText: string
  assetIds: string[]
  result: TaskResult
  errorMessage: string | null
  createdAt: string | null
  startedAt: string | null
  finishedAt: string | null
  retriedFromTaskId: string | null
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

export function fetchTasks(params: { limit?: number; offset?: number; status?: string } = {}) {
  return apiRequest<GenerationTaskResponse[]>('/api/generation-tasks', {
    params,
  })
}

export function fetchTaskLogs(taskId: string) {
  return apiRequest<AgentLogResponse[]>(`/api/generation-tasks/${taskId}/logs`)
}

export function cancelTask(taskId: string) {
  return apiRequest<GenerationTaskResponse>(`/api/generation-tasks/${taskId}/cancel`, {
    method: 'POST',
  })
}

export function retryTask(taskId: string) {
  return apiRequest<GenerationTaskResponse>(`/api/generation-tasks/${taskId}/retry`, {
    method: 'POST',
  })
}

export function publishTask(taskId: string, payload: PublishGamePayload) {
  return apiRequest<GenerationTaskResponse>(`/api/generation-tasks/${taskId}/publish`, {
    method: 'POST',
    data: payload,
  })
}
