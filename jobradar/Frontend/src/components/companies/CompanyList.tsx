import type { Company } from '../../types/company'
import { atsLabel } from '../../utils/ats'
import { formatRelative } from '../../utils/dates'
import { EmptyState } from '../common/EmptyState'

interface CompanyListProps {
  companies: Company[]
  loading: boolean
}

export function CompanyList({ companies, loading }: CompanyListProps) {
  if (loading) {
    return <p className="field-hint">Loading companies…</p>
  }

  if (companies.length === 0) {
    return (
      <EmptyState
        title="No companies yet"
        message="Add a Greenhouse or Lever board below, then scrape."
      />
    )
  }

  return (
    <ul className="company-list">
      {companies.map((company) => (
        <li key={company.id} className="company-item">
          <div className="company-name">{company.name}</div>
          <div className="company-meta">
            <span className="ats-badge">{atsLabel(company.ats_type)}</span>
            {!company.active && (
              <span className="inactive-flag">inactive</span>
            )}
            <span>Last scrape {formatRelative(company.last_scraped_at)}</span>
          </div>
        </li>
      ))}
    </ul>
  )
}
