import { API_BASE_URL, apiRequest } from './client'
import type { User } from './types'

export interface AuthCredentials {
  email: string
  password: string
}

export interface RegisterPayload extends AuthCredentials {
  displayName: string
}

export interface OAuthProviderStatus {
  provider: 'github' | 'google' | string
  configured: boolean
  status: string
  startUrl: string | null
}

export interface OAuthProvidersResponse {
  providers: OAuthProviderStatus[]
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

export function fetchOAuthProviders() {
  return apiRequest<OAuthProvidersResponse>('/api/auth/oauth/providers')
}

export function oauthStartUrl(provider: 'github' | 'google', redirect: string) {
  const query = new URLSearchParams({ redirect })
  return `${API_BASE_URL}/api/auth/oauth/${provider}/start?${query.toString()}`
}
