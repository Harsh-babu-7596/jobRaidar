import { useRef, useState } from 'react'

interface ResumeUploadProps {
  filename: string | null
  saving: boolean
  onUpload: (file: File) => Promise<unknown>
}

export function ResumeUpload({ filename, saving, onUpload }: ResumeUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [localError, setLocalError] = useState<string | null>(null)

  async function handleFile(file: File | undefined) {
    if (!file) return
    setLocalError(null)
    try {
      await onUpload(file)
    } catch (err) {
      setLocalError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      if (inputRef.current) inputRef.current.value = ''
    }
  }

  return (
    <div className="form">
      <p className="field-hint">
        Upload PDF, DOCX, or TXT. Keywords are extracted for job matching.
      </p>
      {filename && (
        <p className="field-hint">
          Current resume: <strong>{filename}</strong>
        </p>
      )}
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx,.txt,.md,application/pdf"
        hidden
        onChange={(e) => void handleFile(e.target.files?.[0])}
      />
      <button
        type="button"
        className="btn btn-ghost"
        disabled={saving}
        onClick={() => inputRef.current?.click()}
      >
        {saving ? 'Reading resume…' : 'Upload resume'}
      </button>
      {localError && (
        <p className="error-banner" style={{ margin: 0 }} role="alert">
          {localError}
        </p>
      )}
    </div>
  )
}
