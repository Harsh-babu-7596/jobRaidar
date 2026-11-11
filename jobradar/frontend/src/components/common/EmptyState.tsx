interface EmptyStateProps {
  title: string
  message: string
}

export function EmptyState({ title, message }: EmptyStateProps) {
  return (
    <div className="empty" role="status">
      <strong>{title}</strong>
      <p>{message}</p>
    </div>
  )
}
