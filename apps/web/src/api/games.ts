import { apiRequest } from './client'
import type { GameListItem, PlayDescriptor } from './types'
import type { PublishGamePayload } from './tasks'

export function fetchPublishedGames() {
  return apiRequest<GameListItem[]>('/api/games?status=published')
}

export function fetchPlayDescriptor(gameId: string) {
  return apiRequest<PlayDescriptor>(`/api/games/${gameId}/play`)
}

export function updateGame(gameId: string, payload: PublishGamePayload) {
  return apiRequest<GameListItem>(`/api/games/${gameId}`, {
    method: 'PATCH',
    data: payload,
  })
}
