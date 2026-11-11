import { API_BASE_URL, ApiError, apiRequest } from './client'
import type { Profile } from '../types/profile'

export function getProfile(): Promise<Profile> {
  return apiRequest<Profile>('/api/resume/profile')
}

export function updateKeywords(keywords: string[]): Promise<Profile> {
  return apiRequest<Profile>('/api/resume/keywords', {
    method: 'PUT',
    body: JSON.stringify({ keywords }),
  })
}

export async function uploadResume(file: File): Promise<Profile> {
  const body = new FormData()
  body.append('file', file)

  const response = await fetch(`${API_BASE_URL}/api/resume/upload`, {
    method: 'POST',
    body,
  })

  if (!response.ok) {
    let message = response.statusText
    try {
      const data: unknown = await response.json()
      if (data && typeof data === 'object' && 'detail' in data) {
        message = String((data as { detail: unknown }).detail)
      }
    } catch {
      // ignore
    }
    throw new ApiError(response.status, message)
  }

  return (await response.json()) as Profile
}
