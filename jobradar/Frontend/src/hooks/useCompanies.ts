import { useCallback, useEffect, useState } from 'react'
import { createCompany, listCompanies } from '../api/companies'
import type { Company, CompanyCreate } from '../types/company'

export function useCompanies() {
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setCompanies(await listCompanies())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load companies')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const addCompany = useCallback(
    async (payload: CompanyCreate) => {
      setSaving(true)
      setError(null)
      try {
        const created = await createCompany(payload)
        setCompanies((prev) =>
          [...prev, created].sort((a, b) => a.name.localeCompare(b.name)),
        )
        return created
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to create company'
        setError(message)
        throw err
      } finally {
        setSaving(false)
      }
    },
    [],
  )

  return { companies, loading, error, saving, refresh, addCompany }
}
