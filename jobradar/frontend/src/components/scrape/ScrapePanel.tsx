import type { ScrapeResponse } from '../../types/scrape'
import { ErrorBanner } from '../common/ErrorBanner'
import { ScrapeResultToast } from './ScrapeResultToast'

interface ScrapePanelProps {
  error: string | null
  lastResponse: ScrapeResponse | null
  onDismiss: () => void
}

export function ScrapePanel({
  error,
  lastResponse,
  onDismiss,
}: ScrapePanelProps) {
  return (
    <>
      {error && <ErrorBanner message={error} />}
      {lastResponse && (
        <ScrapeResultToast response={lastResponse} onDismiss={onDismiss} />
      )}
    </>
  )
}
