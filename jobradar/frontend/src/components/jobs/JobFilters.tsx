interface JobFiltersProps {
  search: string
  location: string
  matchOnly: boolean
  onSearchChange: (value: string) => void
  onLocationChange: (value: string) => void
  onMatchOnlyChange: (value: boolean) => void
}

export function JobFilters({
  search,
  location,
  matchOnly,
  onSearchChange,
  onLocationChange,
  onMatchOnlyChange,
}: JobFiltersProps) {
  return (
    <div className="filters">
      <div className="field">
        <label htmlFor="job-search">Title search</label>
        <input
          id="job-search"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="engineer, designer…"
        />
      </div>
      <div className="field">
        <label htmlFor="job-location">Location</label>
        <input
          id="job-location"
          value={location}
          onChange={(e) => onLocationChange(e.target.value)}
          placeholder="Remote, NYC…"
        />
      </div>
      <label className="toggle-field" htmlFor="match-only">
        <input
          id="match-only"
          type="checkbox"
          checked={matchOnly}
          onChange={(e) => onMatchOnlyChange(e.target.checked)}
        />
        <span>Match resume keywords</span>
      </label>
    </div>
  )
}
