import { useCallback, useEffect, useState } from 'react'
import { listJobs } from '../api/jobs'
import type { Job, JobFilters } from '../types/job'
import type { MatchedJobsResponse } from '../types/profile'

export function useJobs(filters: JobFilters) {
  const [jobs, setJobs] = useState<Job[]>([])
  const [meta, setMeta] = useState<MatchedJobsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const search = filters.search
  const location = filters.location
  const active = filters.active
  const limit = filters.limit
  const match = filters.match
  const keywordsKey = (filters.keywords ?? []).join('|')

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const keywords = keywordsKey
        ? keywordsKey.split('|').filter(Boolean)
        : undefined
      const result = await listJobs({
        search,
        location,
        active,
        limit,
        match,
        keywords,
      })
      setJobs(result.jobs)
      setMeta(result.meta ?? null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load jobs')
    } finally {
      setLoading(false)
    }
  }, [search, location, active, limit, match, keywordsKey])

  useEffect(() => {
    void refresh()
  }, [refresh])

  return { jobs, meta, loading, error, refresh }
}
