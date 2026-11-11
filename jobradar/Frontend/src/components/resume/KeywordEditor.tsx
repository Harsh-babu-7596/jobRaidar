import { useEffect, useState, type FormEvent, type KeyboardEvent } from 'react'

interface KeywordEditorProps {
  keywords: string[]
  saving: boolean
  onSave: (keywords: string[]) => Promise<unknown>
}

export function KeywordEditor({ keywords, saving, onSave }: KeywordEditorProps) {
  const [draft, setDraft] = useState<string[]>(keywords)
  const [input, setInput] = useState('')
  const [dirty, setDirty] = useState(false)

  useEffect(() => {
    setDraft(keywords)
    setDirty(false)
  }, [keywords])

  function addToken(raw: string) {
    const token = raw.trim()
    if (!token) return
    setDraft((prev) => {
      if (prev.some((item) => item.toLowerCase() === token.toLowerCase())) {
        return prev
      }
      return [...prev, token]
    })
    setDirty(true)
    setInput('')
  }

  function removeToken(token: string) {
    setDraft((prev) => prev.filter((item) => item !== token))
    setDirty(true)
  }

  function onKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === 'Enter' || event.key === ',') {
      event.preventDefault()
      addToken(input.replace(/,/g, ''))
    }
    if (event.key === 'Backspace' && !input && draft.length) {
      removeToken(draft[draft.length - 1])
    }
  }

  async function handleSave(event: FormEvent) {
    event.preventDefault()
    let next = draft
    const pending = input.trim()
    if (pending) {
      if (!draft.some((item) => item.toLowerCase() === pending.toLowerCase())) {
        next = [...draft, pending]
        setDraft(next)
      }
      setInput('')
    }
    await onSave(next)
    setDirty(false)
  }

  return (
    <form className="form" onSubmit={(e) => void handleSave(e)}>
      <div className="keyword-cloud" aria-label="Keywords">
        {draft.map((token) => (
          <button
            key={token}
            type="button"
            className="keyword-chip"
            onClick={() => removeToken(token)}
            title="Remove keyword"
          >
            {token}
            <span aria-hidden>×</span>
          </button>
        ))}
      </div>
      <div className="field">
        <label htmlFor="keyword-input">Add keyword</label>
        <input
          id="keyword-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Type a skill and press Enter"
        />
        <span className="field-hint">
          Click a chip to remove. Save after edits.
        </span>
      </div>
      <button
        type="submit"
        className="btn btn-ghost"
        disabled={saving || !dirty}
      >
        {saving ? 'Saving…' : 'Save keywords'}
      </button>
    </form>
  )
}
