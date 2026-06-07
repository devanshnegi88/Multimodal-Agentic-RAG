import { useState, useEffect } from 'react'
import api from '../services/api'
import { useTheme } from '../context/ThemeContext'
import toast from 'react-hot-toast'
import { Save } from 'lucide-react'

export default function Settings() {
  const { theme, toggleTheme } = useTheme()
  const [settings, setSettings] = useState({
    llm_model: 'claude-3-5-sonnet-20241022',
    embedding_model: 'text-embedding-3-small',
    chunk_size: 512,
    chunk_overlap: 64,
    top_k: 5,
    use_reranker: true,
    use_hybrid_search: true,
  })
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    api.get('/settings/').then(r => setSettings(r.data)).catch(() => {})
  }, [])

  const save = async () => {
    setSaving(true)
    try {
      await api.patch('/settings/', settings)
      toast.success('Settings saved')
    } catch { toast.error('Failed to save') }
    finally { setSaving(false) }
  }

  const Section = ({ title, children }) => (
    <div className="card" style={{ marginBottom: 20 }}>
      <h3 style={{ fontFamily: 'var(--font-display)', marginBottom: 20, paddingBottom: 12, borderBottom: '1px solid var(--color-border)' }}>{title}</h3>
      {children}
    </div>
  )

  const Field = ({ label, hint, children }) => (
    <div style={{ marginBottom: 18 }}>
      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, marginBottom: 6 }}>{label}</label>
      {hint && <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: 6 }}>{hint}</p>}
      {children}
    </div>
  )

  return (
    <div style={{ padding: 32, maxWidth: 720 }}>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '1.8rem', marginBottom: 6 }}>Settings</h1>
        <p style={{ color: 'var(--color-text-secondary)' }}>Configure your RAG pipeline and preferences</p>
      </div>

      <Section title="Appearance">
        <Field label="Theme">
          <div style={{ display: 'flex', gap: 10 }}>
            {['dark', 'light'].map(t => (
              <button key={t} onClick={() => t !== theme && toggleTheme()} style={{
                padding: '8px 20px', borderRadius: 'var(--radius-md)', cursor: 'pointer', fontFamily: 'var(--font-mono)',
                border: `1px solid ${theme === t ? 'var(--color-primary)' : 'var(--color-border)'}`,
                background: theme === t ? 'var(--color-primary-dim)' : 'transparent',
                color: theme === t ? 'var(--color-primary)' : 'var(--color-text-secondary)',
              }}>
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </button>
            ))}
          </div>
        </Field>
      </Section>

      <Section title="Language Model">
        <Field label="Model" hint="Claude model to use for chat and agent tasks">
          <select className="input" value={settings.llm_model} onChange={e => setSettings(s => ({ ...s, llm_model: e.target.value }))}>
            <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet (recommended)</option>
            <option value="claude-3-5-haiku-20241022">Claude 3.5 Haiku (fast)</option>
            <option value="claude-opus-4-6">Claude Opus 4.6 (most capable)</option>
          </select>
        </Field>
        <Field label="Embedding Model">
          <select className="input" value={settings.embedding_model} onChange={e => setSettings(s => ({ ...s, embedding_model: e.target.value }))}>
            <option value="text-embedding-3-small">text-embedding-3-small (fast)</option>
            <option value="text-embedding-3-large">text-embedding-3-large (accurate)</option>
          </select>
        </Field>
      </Section>

      <Section title="Retrieval">
        {[
          { key: 'chunk_size', label: 'Chunk Size', hint: 'Characters per chunk (128-2048)', min: 128, max: 2048 },
          { key: 'chunk_overlap', label: 'Chunk Overlap', hint: 'Overlap between chunks (0-256)', min: 0, max: 256 },
          { key: 'top_k', label: 'Top K Results', hint: 'Number of chunks to retrieve (1-20)', min: 1, max: 20 },
        ].map(({ key, label, hint, min, max }) => (
          <Field key={key} label={`${label}: ${settings[key]}`} hint={hint}>
            <input type="range" min={min} max={max} value={settings[key]} onChange={e => setSettings(s => ({ ...s, [key]: +e.target.value }))} style={{ width: '100%', accentColor: 'var(--color-primary)' }} />
          </Field>
        ))}

        {[
          { key: 'use_reranker', label: 'Enable Reranker', hint: 'Use Cohere reranker for better accuracy' },
          { key: 'use_hybrid_search', label: 'Hybrid Search', hint: 'Combine dense + BM25 sparse retrieval' },
        ].map(({ key, label, hint }) => (
          <Field key={key} label={label} hint={hint}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
              <div onClick={() => setSettings(s => ({ ...s, [key]: !s[key] }))} style={{
                width: 44, height: 24, borderRadius: 12, padding: 2, cursor: 'pointer',
                background: settings[key] ? 'var(--color-primary)' : 'var(--color-border)',
                transition: 'background 0.2s',
                position: 'relative',
              }}>
                <div style={{ width: 20, height: 20, borderRadius: '50%', background: 'white', position: 'absolute', top: 2, left: settings[key] ? 22 : 2, transition: 'left 0.2s' }} />
              </div>
              <span style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>{settings[key] ? 'Enabled' : 'Disabled'}</span>
            </label>
          </Field>
        ))}
      </Section>

      <button className="btn btn-primary" onClick={save} disabled={saving} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <Save size={15} /> {saving ? 'Saving…' : 'Save Settings'}
      </button>
    </div>
  )
}
