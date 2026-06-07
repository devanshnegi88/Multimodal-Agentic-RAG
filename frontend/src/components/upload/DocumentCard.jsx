import { FileText, Trash2, CheckCircle, Clock, AlertCircle } from 'lucide-react'
import { documentService } from '../../services/documentService'
import toast from 'react-hot-toast'

const STATUS_ICON = { ready: <CheckCircle size={13} color="var(--color-success)" />, processing: <Clock size={13} color="var(--color-warning)" />, failed: <AlertCircle size={13} color="var(--color-error)" /> }

export default function DocumentCard({ doc, onDelete }) {
  const handleDelete = async () => {
    if (!confirm(`Delete "${doc.original_name}"?`)) return
    try {
      await documentService.deleteDocument(doc.id)
      toast.success('Document deleted')
      onDelete?.(doc.id)
    } catch { toast.error('Failed to delete') }
  }
  const sizeMB = (doc.file_size / 1024 / 1024).toFixed(2)
  return (
    <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', padding: '16px', display: 'flex', gap: 12, alignItems: 'flex-start' }}>
      <div style={{ width: 40, height: 40, background: 'var(--color-primary-dim)', borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
        <FileText size={20} color="var(--color-primary)" />
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontWeight: 600, fontSize: '0.9rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{doc.original_name}</div>
        <div style={{ display: 'flex', gap: 8, marginTop: 4, alignItems: 'center' }}>
          {STATUS_ICON[doc.status]}
          <span style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', fontFamily: 'var(--font-mono)' }}>
            {doc.file_type.toUpperCase()} · {sizeMB} MB · {doc.chunk_count} chunks
          </span>
        </div>
      </div>
      <button onClick={handleDelete} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)', padding: 4 }} title="Delete">
        <Trash2 size={15} />
      </button>
    </div>
  )
}
