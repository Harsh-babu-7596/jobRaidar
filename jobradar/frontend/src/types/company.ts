export type AtsType =
  | 'auto'
  | 'greenhouse'
  | 'lever'
  | 'ashby'
  | 'smartrecruiters'
  | 'workable'
  | 'workday'
  | 'generic'
  | 'custom'

export interface Company {
  id: number
  name: string
  career_url: string
  ats_type: AtsType | string
  ats_identifier: string | null
  active: boolean
  last_scraped_at: string | null
}

export interface CompanyCreate {
  name: string
  career_url: string
  ats_type?: AtsType
  ats_identifier?: string | null
  active?: boolean
}

export interface AtsDetection {
  ats_type: string
  ats_identifier: string | null
  confidence: string
  source: string
  notes?: string
}
