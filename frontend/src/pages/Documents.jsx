import { useEffect, useState } from 'react'
import { documentService } from '../services/documentService'
import DocumentCard from '../components/upload/DocumentCard'
import UploadBox from '../components/upload/UploadBox'
import Loader from '../components/common/Loader'
import { FileText, Filter } from 'lucide-react'

export default function Documents() {
  const [docs, setDocs] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')

  const load = async () => {
    setLoading(true)
    try {
      const data = await documentService.listDocuments()
      setDocs(data.documents || [])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const filtered = filter ? docs.filter(d => d.file_type === filter) : docs
  const types = [...new Set(docs.map(d => d.file_type))]

  return (
    <div style={{ padding: 32, maxWidth: 1200, margin: '0 auto' }}>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '1.8rem', marginBottom: 8 }}>Documents</h1>
        <p style={{ color: 'var(--color-text-secondary)' }}>Manage your knowledge base documents</p>
      </div>

      {/* Upload */}
      <div className="card" style={{ marginBottom: 32 }}>
        <h3 style={{ fontFamily: 'var(--font-display)', marginBottom: 16 }}>Upload Documents</h3>
        <UploadBox onUploaded={load} />
      </div>

      {/* Filter & List */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1rem' }}>
          {filtered.length} document{filtered.length !== 1 ? 's' : ''}
        </h3>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <Filter size={14} color="var(--color-text-muted)" />
          {['', ...types].map(t => (
            <button key={t} onClick={() => setFilter(t)} style={{
              padding: '4px 12px', borderRadius: 100, fontSize: '0.75rem',
              border: `1px solid ${filter === t ? 'var(--color-primary)' : 'var(--color-border)'}`,
              background: filter === t ? 'var(--color-primary-dim)' : 'transparent',
              color: filter === t ? 'var(--color-primary)' : 'var(--color-text-secondary)',
              cursor: 'pointer', fontFamily: 'var(--font-mono)',
            }}>
              {t || 'All'}
            </button>
          ))}
        </div>
      </div>

      {loading ? <Loader text="Loading documents…" /> : (
        filtered.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '48px 0', color: 'var(--color-text-muted)' }}>
            <FileText size={48} style={{ margin: '0 auto 12px', opacity: 0.3 }} />
            <p>No documents yet. Upload some above!</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 12 }}>
            {filtered.map(doc => (
              <DocumentCard key={doc.id} doc={doc} onDelete={id => setDocs(d => d.filter(x => x.id !== id))} />
            ))}
          </div>
        )
      )}
    </div>
  )
}
