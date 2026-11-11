export interface Profile {
  keywords: string[]
  resume_filename: string | null
  updated_at: string | null
}

export interface CompanyImportResult {
  created: number
  updated: number
  skipped: number
  total_rows: number
  errors: string[]
}

export interface MatchedJobsResponse {
  jobs: import('./job').Job[]
  keywords_used: string[]
  matched?: number
  scanned?: number
  message?: string
}
