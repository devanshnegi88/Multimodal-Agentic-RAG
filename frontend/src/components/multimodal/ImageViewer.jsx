import { useState } from 'react'
import { ZoomIn, ZoomOut } from 'lucide-react'
export default function ImageViewer({ src, alt = '' }) {
  const [zoom, setZoom] = useState(1)
  return (
    <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
      <div style={{ padding: '8px 12px', borderBottom: '1px solid var(--color-border)', display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
        <button className="btn btn-ghost" style={{ padding: '4px 8px' }} onClick={() => setZoom(z => Math.max(0.5, z-0.25))}><ZoomOut size={14} /></button>
        <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', alignSelf: 'center' }}>{Math.round(zoom*100)}%</span>
        <button className="btn btn-ghost" style={{ padding: '4px 8px' }} onClick={() => setZoom(z => Math.min(3, z+0.25))}><ZoomIn size={14} /></button>
      </div>
      <div style={{ overflow: 'auto', padding: 16, textAlign: 'center' }}>
        <img src={src} alt={alt} style={{ transform: `scale(${zoom})`, transformOrigin: 'top center', maxWidth: '100%', transition: 'transform 0.2s' }} />
      </div>
    </div>
  )
}
