import { useState } from 'react'
import type { Job } from '../../types/job'
import { formatDateTime, formatRelative, stripHtml } from '../../utils/dates'

interface JobRowProps {
  job: Job
}

export function JobRow({ job }: JobRowProps) {
  const [expanded, setExpanded] = useState(false)
  const plain = stripHtml(job.description)
  const preview = plain.slice(0, 480)
  const canExpand = plain.length > 0
  const matched = job.matched_keywords ?? []

  return (
    <article className="job-row">
      <div className="job-row-head">
        <div>
          <div className="job-title-row">
            <div className="job-title">{job.title}</div>
            {typeof job.match_score === 'number' && (
              <span className="match-score" title="Match score">
                {job.match_score.toFixed(1)}
              </span>
            )}
          </div>
          <div className="job-sub">
            <span>{job.company}</span>
            <span>{job.location || 'Location n/a'}</span>
            <span title={formatDateTime(job.first_seen_at)}>
              First seen {formatRelative(job.first_seen_at)}
            </span>
            {job.posted_at && (
              <span title={String(job.posted_at)}>
                Posted {formatDateTime(job.posted_at)}
              </span>
            )}
          </div>
          {matched.length > 0 && (
            <div className="matched-keywords">
              {matched.map((keyword) => (
                <span key={keyword} className="keyword-chip is-static">
                  {keyword}
                </span>
              ))}
            </div>
          )}
        </div>
        <div className="job-actions">
          {canExpand && (
            <button
              type="button"
              className="btn btn-ghost"
              onClick={() => setExpanded((v) => !v)}
            >
              {expanded ? 'Hide' : 'Details'}
            </button>
          )}
          <a
            className="btn btn-primary"
            href={job.apply_url}
            target="_blank"
            rel="noreferrer noopener"
          >
            Apply
          </a>
        </div>
      </div>
      {expanded && canExpand && (
        <p className="job-desc">
          {preview}
          {plain.length > 480 ? '…' : ''}
        </p>
      )}
    </article>
  )
}
