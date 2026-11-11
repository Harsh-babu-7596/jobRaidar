import { useState, type FormEvent } from 'react'
import { detectAts } from '../../api/companies'
import type { AtsType, CompanyCreate } from '../../types/company'
import { ATS_OPTIONS, atsLabel } from '../../utils/ats'

interface AddCompanyFormProps {
  saving: boolean
  onSubmit: (payload: CompanyCreate) => Promise<unknown>
}

const INITIAL = {
  name: '',
  career_url: '',
  ats_type: 'auto' as AtsType,
  ats_identifier: '',
}

export function AddCompanyForm({ saving, onSubmit }: AddCompanyFormProps) {
  const [form, setForm] = useState(INITIAL)
  const [localError, setLocalError] = useState<string | null>(null)
  const [detectHint, setDetectHint] = useState<string | null>(null)
  const [detecting, setDetecting] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)

  async function handleDetect() {
    if (!form.career_url.trim()) {
      setLocalError('Enter a career URL first.')
      return
    }
    setDetecting(true)
    setLocalError(null)
    try {
      const detected = await detectAts(form.career_url.trim())
      setForm((f) => ({
        ...f,
        ats_type: detected.ats_type as AtsType,
        ats_identifier: detected.ats_identifier ?? '',
      }))
      setDetectHint(
        `Detected ${atsLabel(detected.ats_type)}` +
          (detected.ats_identifier ? ` · ${detected.ats_identifier}` : '') +
          ` (${detected.confidence})`,
      )
      setShowAdvanced(true)
    } catch (err) {
      setLocalError(err instanceof Error ? err.message : 'Detection failed')
    } finally {
      setDetecting(false)
    }
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setLocalError(null)

    if (!form.name.trim() || !form.career_url.trim()) {
      setLocalError('Name and career URL are required.')
      return
    }

    try {
      await onSubmit({
        name: form.name.trim(),
        career_url: form.career_url.trim(),
        ats_type: form.ats_type,
        ats_identifier: form.ats_identifier.trim() || null,
        active: true,
      })
      setForm(INITIAL)
      setDetectHint(null)
      setShowAdvanced(false)
    } catch (err) {
      setLocalError(err instanceof Error ? err.message : 'Could not add company')
    }
  }

  return (
    <form className="form" onSubmit={(e) => void handleSubmit(e)}>
      <div className="field">
        <label htmlFor="company-name">Company name</label>
        <input
          id="company-name"
          value={form.name}
          onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
          placeholder="Acme Corp"
          autoComplete="organization"
          required
        />
      </div>

      <div className="field">
        <label htmlFor="career-url">Career URL</label>
        <input
          id="career-url"
          type="url"
          value={form.career_url}
          onChange={(e) => {
            setForm((f) => ({ ...f, career_url: e.target.value }))
            setDetectHint(null)
          }}
          placeholder="https://company.com/careers"
          required
        />
        <span className="field-hint">
          Paste any careers page. Known ATS boards are auto-detected; others use
          the generic parser.
        </span>
      </div>

      <div className="row-actions">
        <button
          type="button"
          className="btn btn-ghost"
          disabled={detecting || saving}
          onClick={() => void handleDetect()}
        >
          {detecting ? 'Detecting…' : 'Detect ATS'}
        </button>
        <button
          type="button"
          className="btn btn-ghost"
          onClick={() => setShowAdvanced((v) => !v)}
        >
          {showAdvanced ? 'Hide advanced' : 'Advanced'}
        </button>
      </div>

      {detectHint && <p className="field-hint">{detectHint}</p>}

      {showAdvanced && (
        <>
          <div className="field">
            <label htmlFor="ats-type">ATS</label>
            <select
              id="ats-type"
              value={form.ats_type}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  ats_type: e.target.value as AtsType,
                }))
              }
            >
              {ATS_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          <div className="field">
            <label htmlFor="ats-id">ATS identifier (optional)</label>
            <input
              id="ats-id"
              value={form.ats_identifier}
              onChange={(e) =>
                setForm((f) => ({ ...f, ats_identifier: e.target.value }))
              }
              placeholder="Usually filled by auto-detect"
            />
          </div>
        </>
      )}

      {localError && (
        <p className="error-banner" style={{ margin: 0 }} role="alert">
          {localError}
        </p>
      )}

      <button type="submit" className="btn btn-ghost" disabled={saving}>
        {saving ? 'Adding…' : 'Add company'}
      </button>
    </form>
  )
}
