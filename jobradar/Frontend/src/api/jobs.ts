import { apiRequest } from './client'
import type { Job, JobFilters } from '../types/job'
import type { MatchedJobsResponse } from '../types/profile'

export async function listJobs(
  filters: JobFilters = {},
): Promise<{ jobs: Job[]; meta?: MatchedJobsResponse }> {
  const params = new URLSearchParams()
  if (filters.search) params.set('search', filters.search)
  if (filters.location) params.set('location', filters.location)
  if (filters.active !== undefined) params.set('active', String(filters.active))
  if (filters.limit !== undefined) params.set('limit', String(filters.limit))
  if (filters.match) params.set('match', 'true')
  if (filters.keywords?.length) {
    params.set('keywords', filters.keywords.join(','))
  }

  const query = params.toString()
  const data = await apiRequest<Job[] | MatchedJobsResponse>(
    `/api/jobs${query ? `?${query}` : ''}`,
  )

  if (Array.isArray(data)) {
    return { jobs: data }
  }

  return { jobs: data.jobs ?? [], meta: data }
}
