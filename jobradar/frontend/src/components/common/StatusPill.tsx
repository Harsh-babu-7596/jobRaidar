interface StatusPillProps {
  ok: boolean | null
  label?: string
}

export function StatusPill({ ok, label }: StatusPillProps) {
  const text =
    label ??
    (ok === null ? 'Checking API…' : ok ? 'API online' : 'API offline')

  const className = [
    'status-pill',
    ok === true ? 'is-ok' : '',
    ok === false ? 'is-down' : '',
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <span className={className} title={text}>
      <span className="status-dot" aria-hidden />
      {text}
    </span>
  )
}
