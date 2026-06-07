import { FileText, Image, Music, Video, Table } from 'lucide-react'
const ICONS = { pdf: FileText, png: Image, jpg: Image, jpeg: Image, mp3: Music, wav: Music, mp4: Video, mov: Video, xlsx: Table, csv: Table }
export default function FilePreview({ file }) {
  const ext = file.name.split('.').pop().toLowerCase()
  const Icon = ICONS[ext] || FileText
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '6px 10px', background: 'var(--color-surface-elevated)', borderRadius: 'var(--radius-sm)' }}>
      <Icon size={14} color="var(--color-primary)" />
      <span style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>{file.name}</span>
    </div>
  )
}
