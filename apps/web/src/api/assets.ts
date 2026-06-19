import { apiRequest } from './client'

export interface AssetResponse {
  id: string
  filename: string
  contentType: string
  sizeBytes: number
  url: string
}

export function uploadAsset(file: File): Promise<AssetResponse> {
  const formData = new FormData()
  formData.append('file', file)

  return apiRequest<AssetResponse>('/api/assets', {
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}
