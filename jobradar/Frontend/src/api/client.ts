const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') ||
  'http://127.0.0.1:8000'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function parseError(response: Response): Promise<string> {
  try {
    const data: unknown = await response.json()
    if (typeof data === 'string') return data
    if (data && typeof data === 'object') {
      const record = data as Record<string, unknown>
      if (typeof record.detail === 'string') return record.detail
      if (Array.isArray(record.detail)) {
        return record.detail
          .map((item) =>
            typeof item === 'object' && item && 'msg' in item
              ? String((item as { msg: unknown }).msg)
              : JSON.stringify(item),
          )
          .join('; ')
      }
      if (typeof record.message === 'string') return record.message
    }
  } catch {
    // fall through
  }
  return response.statusText || `Request failed (${response.status})`
}

export async function apiRequest<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      Accept: 'application/json',
      ...(init?.body ? { 'Content-Type': 'application/json' } : {}),
      ...init?.headers,
    },
  })

  if (!response.ok) {
    throw new ApiError(response.status, await parseError(response))
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

export { API_BASE_URL }
