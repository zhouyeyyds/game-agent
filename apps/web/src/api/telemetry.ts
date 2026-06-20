import { apiRequest } from './client'

export interface TelemetryEventPayload {
  eventType: string
  entityType?: string
  entityId?: string
  requestId?: string
  payload?: Record<string, unknown>
}

export function trackEvent(event: TelemetryEventPayload) {
  return apiRequest('/api/telemetry/events', {
    method: 'POST',
    data: event,
  }).catch(() => undefined)
}
