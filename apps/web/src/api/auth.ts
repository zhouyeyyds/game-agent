import { apiRequest } from './client'
import type { User } from './types'

export interface AuthCredentials {
  email: string
  password: string
}

export interface RegisterPayload extends AuthCredentials {
  displayName: string
}

export function fetchMe() {
  return apiRequest<User>('/api/auth/me')
}

export function login(payload: AuthCredentials) {
  return apiRequest<User>('/api/auth/login', {
    method: 'POST',
    data: payload,
  })
}

export function register(payload: RegisterPayload) {
  return apiRequest<User>('/api/auth/register', {
    method: 'POST',
    data: payload,
  })
}

export function logout() {
  return apiRequest<{ ok: boolean }>('/api/auth/logout', { method: 'POST' })
}
