import { useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
export default function PDFViewer({ url }) {
  const [page, setPage] = useState(1)
  return (
    <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
      <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--color-border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: '0.85rem', fontFamily: 'var(--font-mono)' }}>Page {page}</span>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-ghost" style={{ padding: '4px 8px' }} onClick={() => setPage(p => Math.max(1, p-1))}><ChevronLeft size={14} /></button>
          <button className="btn btn-ghost" style={{ padding: '4px 8px' }} onClick={() => setPage(p => p+1)}><ChevronRight size={14} /></button>
        </div>
      </div>
      <iframe src={url ? `${url}#page=${page}` : ''} style={{ width: '100%', height: 600, border: 'none' }} title="PDF" />
    </div>
  )
}
