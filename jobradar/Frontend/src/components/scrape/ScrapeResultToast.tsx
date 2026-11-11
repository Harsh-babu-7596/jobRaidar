import type { ScrapeResponse } from '../../types/scrape'

interface ScrapeResultToastProps {
  response: ScrapeResponse
  onDismiss: () => void
}

export function ScrapeResultToast({
  response,
  onDismiss,
}: ScrapeResultToastProps) {
  const { summary, results } = response
  const hasFail = summary.failed > 0

  return (
    <div
      className={`scrape-toast${hasFail ? ' has-fail' : ''}`}
      role="status"
    >
      <div className="scrape-toast-head">
        <h3>{hasFail ? 'Scrape finished with issues' : 'Scrape complete'}</h3>
        <button type="button" className="btn btn-ghost" onClick={onDismiss}>
          Dismiss
        </button>
      </div>
      <div className="scrape-summary">
        <span>
          Companies <strong>{summary.companies}</strong>
        </span>
        <span>
          Fetched <strong>{summary.fetched}</strong>
        </span>
        <span>
          Inserted <strong>{summary.inserted}</strong>
        </span>
        <span>
          Updated <strong>{summary.updated}</strong>
        </span>
        <span>
          Failed <strong>{summary.failed}</strong>
        </span>
      </div>
      {results.length > 0 && (
        <ul className="scrape-results">
          {results.map((item) => (
            <li key={`${item.company}-${item.status}`}>
              {item.company}: {item.status}
              {item.status === 'success'
                ? ` · +${item.inserted} / ~${item.updated} (fetched ${item.fetched})`
                : item.error
                  ? ` · ${item.error}`
                  : ''}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
