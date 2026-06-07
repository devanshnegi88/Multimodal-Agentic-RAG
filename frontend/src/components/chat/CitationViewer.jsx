import { useState } from 'react'
import { BookOpen, Globe, ChevronDown, ChevronUp } from 'lucide-react'

export default function CitationViewer({ citations = [] }) {
  const [open, setOpen] = useState(false)
  if (!citations.length) return null

  return (
    <div style={{ marginTop: 10 }}>
      <button
        onClick={() => setOpen(v => !v)}
        style={{
          display: 'flex', alignItems: 'center', gap: 6,
          background: 'none', border: 'none', cursor: 'pointer',
          color: 'var(--color-text-secondary)', fontSize: '0.78rem',
          fontFamily: 'var(--font-mono)', padding: 0,
        }}
      >
        <BookOpen size={13} />
        {citations.length} citation{citations.length > 1 ? 's' : ''}
        {open ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
      </button>

      {open && (
        <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 6 }}>
          {citations.map((cit, i) => (
            <div key={i} style={{
              background: 'var(--color-bg)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-sm)',
              padding: '8px 12px',
              fontSize: '0.78rem',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                {cit.type === 'web' ? <Globe size={12} color="var(--color-accent-2)" /> : <BookOpen size={12} color="var(--color-primary)" />}
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-primary)', fontWeight: 600 }}>
                  [{cit.ref_id}]
                </span>
                {cit.title && <span style={{ color: 'var(--color-text-secondary)' }}>{cit.title}</span>}
                {cit.url && <a href={cit.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--color-accent-2)', fontSize: '0.72rem' }}>↗</a>}
              </div>
              <p style={{ color: 'var(--color-text-secondary)', margin: 0, lineHeight: 1.5 }}>
                {cit.text_excerpt}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
