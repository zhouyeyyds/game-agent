import { apiRequest } from './client'
import type { GameListItem, PlayDescriptor } from './types'

export function fetchPublishedGames() {
  return apiRequest<GameListItem[]>('/api/games?status=published')
}

export function fetchPlayDescriptor(gameId: string) {
  return apiRequest<PlayDescriptor>(`/api/games/${gameId}/play`)
}
