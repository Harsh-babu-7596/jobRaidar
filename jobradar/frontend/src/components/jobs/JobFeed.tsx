import type { Job } from '../../types/job'
import { EmptyState } from '../common/EmptyState'
import { JobRow } from './JobRow'

interface JobFeedProps {
  jobs: Job[]
  loading: boolean
}

export function JobFeed({ jobs, loading }: JobFeedProps) {
  if (loading) {
    return (
      <EmptyState title="Loading feed" message="Pulling jobs from the API…" />
    )
  }

  if (jobs.length === 0) {
    return (
      <EmptyState
        title="No jobs on the radar"
        message="Add a company and run Scrape now to populate this feed."
      />
    )
  }

  return (
    <div className="job-feed">
      {jobs.map((job) => (
        <JobRow key={job.id} job={job} />
      ))}
    </div>
  )
}
