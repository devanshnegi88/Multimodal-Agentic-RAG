import { FileText, CheckCircle, Loader, AlertCircle } from 'lucide-react'

const STATUS_CONFIG = {
  uploading: { color: 'var(--color-primary)', icon: <Loader size={14} style={{ animation: 'spin 0.8s linear infinite' }} />, label: 'Uploading' },
  processing: { color: 'var(--color-warning)', icon: <Loader size={14} style={{ animation: 'spin 0.8s linear infinite' }} />, label: 'Processing' },
  ready: { color: 'var(--color-success)', icon: <CheckCircle size={14} />, label: 'Ready' },
  failed: { color: 'var(--color-error)', icon: <AlertCircle size={14} />, label: 'Failed' },
}

export default function UploadProgress({ upload }) {
  const cfg = STATUS_CONFIG[upload.status] || STATUS_CONFIG.uploading
  const ext = upload.file?.name?.split('.').pop()?.toLowerCase()

  return (
    <div style={{
      background: 'var(--color-surface)',
      border: '1px solid var(--color-border)',
      borderRadius: 'var(--radius-md)',
      padding: '12px 16px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
        <div style={{
          width: 32, height: 32,
          background: 'var(--color-primary-dim)',
          borderRadius: 8,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <FileText size={16} color="var(--color-primary)" />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: '0.85rem', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {upload.file?.name}
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--color-text-secondary)', display: 'flex', alignItems: 'center', gap: 4, marginTop: 1 }}>
            <span style={{ color: cfg.color }}>{cfg.icon}</span>
            <span style={{ color: cfg.color }}>{cfg.label}</span>
            {upload.status === 'uploading' && <span>· {upload.progress}%</span>}
          </div>
        </div>
      </div>

      {upload.status === 'uploading' && (
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${upload.progress}%` }} />
        </div>
      )}
    </div>
  )
}
