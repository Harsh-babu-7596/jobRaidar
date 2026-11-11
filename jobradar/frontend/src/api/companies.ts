import { API_BASE_URL, ApiError, apiRequest } from './client'
import type { AtsDetection, Company, CompanyCreate } from '../types/company'
import type { CompanyImportResult } from '../types/profile'

export function listCompanies(): Promise<Company[]> {
  return apiRequest<Company[]>('/api/companies')
}

export function createCompany(payload: CompanyCreate): Promise<Company> {
  return apiRequest<Company>('/api/companies', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function detectAts(careerUrl: string): Promise<AtsDetection> {
  return apiRequest<AtsDetection>('/api/companies/detect', {
    method: 'POST',
    body: JSON.stringify({ career_url: careerUrl }),
  })
}

export function companiesTemplateUrl(): string {
  return `${API_BASE_URL}/api/companies/template.xlsx`
}

export async function importCompaniesExcel(
  file: File,
): Promise<CompanyImportResult> {
  const body = new FormData()
  body.append('file', file)

  const response = await fetch(`${API_BASE_URL}/api/companies/import`, {
    method: 'POST',
    body,
  })

  if (!response.ok) {
    let message = response.statusText
    try {
      const data: unknown = await response.json()
      if (data && typeof data === 'object' && 'detail' in data) {
        message = String((data as { detail: unknown }).detail)
      }
    } catch {
      // ignore
    }
    throw new ApiError(response.status, message)
  }

  return (await response.json()) as CompanyImportResult
}
