import { useEffect, useState } from 'react'
import { AddCompanyForm } from './components/companies/AddCompanyForm'
import { CompanyList } from './components/companies/CompanyList'
import { ExcelImport } from './components/companies/ExcelImport'
import { ErrorBanner } from './components/common/ErrorBanner'
import { JobFeed } from './components/jobs/JobFeed'
import { JobFilters } from './components/jobs/JobFilters'
import { ConsoleShell } from './components/layout/ConsoleShell'
import { HeaderBar } from './components/layout/HeaderBar'
import { KeywordEditor } from './components/resume/KeywordEditor'
import { ResumeUpload } from './components/resume/ResumeUpload'
import { ScrapePanel } from './components/scrape/ScrapePanel'
import { useCompanies } from './hooks/useCompanies'
import { useHealth } from './hooks/useHealth'
import { useJobs } from './hooks/useJobs'
import { useProfile } from './hooks/useProfile'
import { useScrape } from './hooks/useScrape'

function useDebouncedValue(value: string, delayMs = 250): string {
  const [debounced, setDebounced] = useState(value)

  useEffect(() => {
    const id = window.setTimeout(() => setDebounced(value), delayMs)
    return () => window.clearTimeout(id)
  }, [value, delayMs])

  return debounced
}

export default function App() {
  const [search, setSearch] = useState('')
  const [location, setLocation] = useState('')
  const [matchOnly, setMatchOnly] = useState(true)
  const debouncedSearch = useDebouncedValue(search.trim())
  const debouncedLocation = useDebouncedValue(location.trim())

  const health = useHealth()
  const companies = useCompanies()
  const profile = useProfile()
  const jobs = useJobs({
    search: debouncedSearch || undefined,
    location: debouncedLocation || undefined,
    active: true,
    limit: 200,
    match: matchOnly,
  })
  const scrape = useScrape()

  async function handleScrape() {
    try {
      await scrape.scrapeNow()
      await Promise.all([companies.refresh(), jobs.refresh()])
    } catch {
      // error surfaced via scrape.error
    }
  }

  const keywordCount = profile.profile?.keywords.length ?? 0

  return (
    <ConsoleShell
      header={
        <HeaderBar
          apiOk={health.ok}
          scraping={scrape.running}
          onScrape={() => void handleScrape()}
          companyCount={companies.companies.length}
        />
      }
      rail={
        <>
          <div className="rail-section">
            <h2>Resume keywords</h2>
            {profile.error && <ErrorBanner message={profile.error} />}
            <ResumeUpload
              filename={profile.profile?.resume_filename ?? null}
              saving={profile.saving}
              onUpload={profile.upload}
            />
            {!profile.loading && (
              <KeywordEditor
                keywords={profile.profile?.keywords ?? []}
                saving={profile.saving}
                onSave={async (keywords) => {
                  await profile.saveKeywords(keywords)
                  await jobs.refresh()
                }}
              />
            )}
          </div>
          <div className="rail-section">
            <h2>Companies from Excel</h2>
            <ExcelImport onImported={companies.refresh} />
          </div>
          <div className="rail-section">
            <h2>Tracked companies</h2>
            {companies.error && <ErrorBanner message={companies.error} />}
            <CompanyList
              companies={companies.companies}
              loading={companies.loading}
            />
          </div>
          <div className="rail-section">
            <h2>Add company</h2>
            <AddCompanyForm
              saving={companies.saving}
              onSubmit={companies.addCompany}
            />
          </div>
        </>
      }
      main={
        <>
          <div className="main-toolbar">
            <JobFilters
              search={search}
              location={location}
              matchOnly={matchOnly}
              onSearchChange={setSearch}
              onLocationChange={setLocation}
              onMatchOnlyChange={setMatchOnly}
            />
          </div>
          <ScrapePanel
            error={scrape.error}
            lastResponse={scrape.lastResponse}
            onDismiss={scrape.dismiss}
          />
          {jobs.error && <ErrorBanner message={jobs.error} />}
          {jobs.meta?.message && <ErrorBanner message={jobs.meta.message} />}
          <p className="feed-meta">
            {jobs.loading
              ? 'Refreshing feed…'
              : matchOnly
                ? `${jobs.jobs.length} matched job${jobs.jobs.length === 1 ? '' : 's'} · ${keywordCount} keyword${keywordCount === 1 ? '' : 's'}${
                    typeof jobs.meta?.scanned === 'number'
                      ? ` · scanned ${jobs.meta.scanned}`
                      : ''
                  }`
                : `${jobs.jobs.length} job${jobs.jobs.length === 1 ? '' : 's'} shown`}
          </p>
          <JobFeed jobs={jobs.jobs} loading={jobs.loading} />
        </>
      }
    />
  )
}
