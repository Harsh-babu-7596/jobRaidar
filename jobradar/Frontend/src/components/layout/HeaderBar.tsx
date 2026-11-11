import { StatusPill } from '../common/StatusPill'

interface HeaderBarProps {
  apiOk: boolean | null
  scraping: boolean
  onScrape: () => void
  companyCount: number
}

export function HeaderBar({
  apiOk,
  scraping,
  onScrape,
  companyCount,
}: HeaderBarProps) {
  return (
    <header className="header">
      <div className="brand">
        <div className="brand-mark">
          <h1 className="brand-name">
            Job<span>Radar</span>
          </h1>
        </div>
        <p className="brand-tag">
          Local ATS monitor · {companyCount} tracked{' '}
          {companyCount === 1 ? 'company' : 'companies'}
        </p>
      </div>
      <div className="header-actions">
        <StatusPill ok={apiOk} />
        <button
          type="button"
          className="btn btn-primary"
          onClick={onScrape}
          disabled={scraping || apiOk === false}
        >
          {scraping ? 'Scanning…' : 'Scrape now'}
        </button>
      </div>
    </header>
  )
}
