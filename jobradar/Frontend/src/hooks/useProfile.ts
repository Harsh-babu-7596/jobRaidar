import { useCallback, useEffect, useState } from 'react'
import { getProfile, updateKeywords, uploadResume } from '../api/resume'
import type { Profile } from '../types/profile'

export function useProfile() {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setProfile(await getProfile())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load profile')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const saveKeywords = useCallback(async (keywords: string[]) => {
    setSaving(true)
    setError(null)
    try {
      const next = await updateKeywords(keywords)
      setProfile(next)
      return next
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to save keywords'
      setError(message)
      throw err
    } finally {
      setSaving(false)
    }
  }, [])

  const upload = useCallback(async (file: File) => {
    setSaving(true)
    setError(null)
    try {
      const next = await uploadResume(file)
      setProfile(next)
      return next
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to upload resume'
      setError(message)
      throw err
    } finally {
      setSaving(false)
    }
  }, [])

  return { profile, loading, saving, error, refresh, saveKeywords, upload }
}
