export interface ScrapeResult {
  company: string
  fetched: number
  inserted: number
  updated: number
  status: 'success' | 'failed' | string
  error?: string
}

export interface ScrapeSummary {
  companies: number
  fetched: number
  inserted: number
  updated: number
  failed: number
}

export interface ScrapeResponse {
  results: ScrapeResult[]
  summary: ScrapeSummary
}
