import { useCallback, useEffect, useState } from 'react'
import { getHealth } from '../api/health'

export function useHealth(pollMs = 15000) {
  const [ok, setOk] = useState<boolean | null>(null)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    try {
      const data = await getHealth()
      setOk(data.status === 'ok')
      setError(null)
    } catch (err) {
      setOk(false)
      setError(err instanceof Error ? err.message : 'API unreachable')
    }
  }, [])

  useEffect(() => {
    void refresh()
    const id = window.setInterval(() => void refresh(), pollMs)
    return () => window.clearInterval(id)
  }, [pollMs, refresh])

  return { ok, error, refresh }
}
