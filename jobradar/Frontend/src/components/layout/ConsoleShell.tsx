import type { ReactNode } from 'react'

interface ConsoleShellProps {
  header: ReactNode
  rail: ReactNode
  main: ReactNode
}

export function ConsoleShell({ header, rail, main }: ConsoleShellProps) {
  return (
    <div className="console">
      {header}
      <div className="console-body">
        <aside className="rail">{rail}</aside>
        <section className="main">{main}</section>
      </div>
    </div>
  )
}
