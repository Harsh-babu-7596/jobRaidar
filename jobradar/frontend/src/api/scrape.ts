import { apiRequest } from './client'
import type { ScrapeResponse } from '../types/scrape'

export function runScrape(): Promise<ScrapeResponse> {
  return apiRequest<ScrapeResponse>('/api/scrape/run', { method: 'POST' })
}
