import { FileText } from 'lucide-react'

export default function SourceCard({ source, index }) {
  return (
    <div style={{
      background: 'var(--color-bg)',
      border: '1px solid var(--color-border)',
      borderRadius: 'var(--radius-md)',
      padding: '8px 12px',
      fontSize: '0.76rem',
      maxWidth: 240,
      display: 'flex',
      gap: 8,
      alignItems: 'flex-start',
    }}>
      <div style={{
        width: 22, height: 22,
        background: 'var(--color-primary-dim)',
        borderRadius: 6,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flexShrink: 0,
      }}>
        <FileText size={12} color="var(--color-primary)" />
      </div>
      <div>
        <div style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-primary)', fontSize: '0.7rem', marginBottom: 2 }}>
          Source {index}
        </div>
        <p style={{ color: 'var(--color-text-secondary)', margin: 0, lineHeight: 1.4, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
          {source.text}
        </p>
        <div style={{ marginTop: 4, fontFamily: 'var(--font-mono)', fontSize: '0.65rem', color: 'var(--color-text-muted)' }}>
          Score: {(source.score * 100).toFixed(0)}%
        </div>
      </div>
    </div>
  )
}
