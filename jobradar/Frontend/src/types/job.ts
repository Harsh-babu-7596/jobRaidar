export interface Job {
  id: number
  company: string
  title: string
  location: string | null
  description: string | null
  apply_url: string
  posted_at: string | null
  first_seen_at: string
  active: boolean
  match_score?: number | null
  matched_keywords?: string[]
}

export interface JobFilters {
  search?: string
  location?: string
  active?: boolean
  limit?: number
  match?: boolean
  keywords?: string[]
}
