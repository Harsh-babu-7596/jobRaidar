import { useCallback, useState } from 'react'
import { runScrape } from '../api/scrape'
import type { ScrapeResponse } from '../types/scrape'

export function useScrape() {
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastResponse, setLastResponse] = useState<ScrapeResponse | null>(null)

  const scrapeNow = useCallback(async () => {
    setRunning(true)
    setError(null)
    try {
      const response = await runScrape()
      setLastResponse(response)
      return response
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Scrape failed'
      setError(message)
      throw err
    } finally {
      setRunning(false)
    }
  }, [])

  const dismiss = useCallback(() => {
    setLastResponse(null)
    setError(null)
  }, [])

  return { running, error, lastResponse, scrapeNow, dismiss }
}
