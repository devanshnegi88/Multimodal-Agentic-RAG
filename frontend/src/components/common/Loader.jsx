import { Zap } from 'lucide-react'

export default function Loader({ fullscreen = false, size = 'md', text = 'Loading...' }) {
  const spinnerSize = size === 'sm' ? 20 : size === 'lg' ? 48 : 32

  const spinner = (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
      <div style={{
        width: spinnerSize, height: spinnerSize,
        border: `2px solid var(--color-border)`,
        borderTopColor: 'var(--color-primary)',
        borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
      }} />
      {text && <span style={{ color: 'var(--color-text-secondary)', fontSize: '0.85rem', fontFamily: 'var(--font-mono)' }}>{text}</span>}
    </div>
  )

  if (fullscreen) {
    return (
      <div style={{
        position: 'fixed', inset: 0,
        background: 'var(--color-bg)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        zIndex: 9999,
      }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20 }}>
          <div style={{
            width: 56, height: 56,
            background: 'var(--color-primary)',
            borderRadius: 16,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 30px var(--color-primary-glow)',
            animation: 'pulse 2s ease infinite',
          }}>
            <Zap size={28} color="white" />
          </div>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.2rem', fontWeight: 700 }}>AgenticRAG</div>
          {spinner}
        </div>
      </div>
    )
  }

  return spinner
}
