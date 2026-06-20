import axios, { AxiosError, type AxiosRequestConfig } from 'axios'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly payload?: unknown,
  ) {
    super(message)
  }
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

function toApiError(error: unknown): ApiError {
  if (error instanceof AxiosError) {
    const status = error.response?.status ?? 0
    const payload = error.response?.data
    const message = typeof payload === 'object' && payload && 'detail' in payload
      ? String((payload as { detail: unknown }).detail)
      : error.message || `Request failed with status ${status}`

    return new ApiError(message, status, payload)
  }

  return new ApiError(error instanceof Error ? error.message : 'Unknown API error', 0)
}

export async function apiRequest<T>(path: string, config: AxiosRequestConfig = {}): Promise<T> {
  try {
    const response = await apiClient.request<T>({
      url: path,
      ...config,
    })
    return response.data
  } catch (error) {
    throw toApiError(error)
  }
}
