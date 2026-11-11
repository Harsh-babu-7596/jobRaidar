import { useRef, useState } from 'react'
import { companiesTemplateUrl, importCompaniesExcel } from '../../api/companies'
import type { CompanyImportResult } from '../../types/profile'

interface ExcelImportProps {
  onImported: () => Promise<unknown> | void
}

export function ExcelImport({ onImported }: ExcelImportProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState<CompanyImportResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleFile(file: File | undefined) {
    if (!file) return
    setBusy(true)
    setError(null)
    setResult(null)
    try {
      const imported = await importCompaniesExcel(file)
      setResult(imported)
      await onImported()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Import failed')
    } finally {
      setBusy(false)
      if (inputRef.current) inputRef.current.value = ''
    }
  }

  return (
    <div className="form">
      <p className="field-hint">
        Required: <code>name</code>, <code>career_url</code>. Optional:{' '}
        <code>ats_type</code> (use <code>auto</code>), <code>ats_identifier</code>,{' '}
        <code>active</code>
      </p>
      <div className="row-actions">
        <a className="btn btn-ghost" href={companiesTemplateUrl()}>
          Download template
        </a>
        <button
          type="button"
          className="btn btn-ghost"
          disabled={busy}
          onClick={() => inputRef.current?.click()}
        >
          {busy ? 'Importing…' : 'Upload Excel'}
        </button>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept=".xlsx,.xlsm"
        hidden
        onChange={(e) => void handleFile(e.target.files?.[0])}
      />
      {error && (
        <p className="error-banner" style={{ margin: 0 }} role="alert">
          {error}
        </p>
      )}
      {result && (
        <p className="field-hint">
          Imported {result.total_rows} rows · created {result.created} · updated{' '}
          {result.updated}
          {result.skipped ? ` · skipped ${result.skipped}` : ''}
        </p>
      )}
    </div>
  )
}
