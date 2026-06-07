import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { User, Mail, Calendar, Shield, Edit2, Save } from 'lucide-react'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

export default function Profile() {
  const { user, logout } = useAuth()
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({ username: user?.username || '', email: user?.email || '' })

  const handleSave = async () => {
    try {
      // In prod: call PATCH /api/auth/me
      toast.success('Profile updated')
      setEditing(false)
    } catch {
      toast.error('Failed to update profile')
    }
  }

  const infoItems = [
    { icon: <User size={16} />, label: 'Username', value: user?.username },
    { icon: <Mail size={16} />, label: 'Email', value: user?.email },
    { icon: <Calendar size={16} />, label: 'Member since', value: user?.created_at ? format(new Date(user.created_at), 'MMMM d, yyyy') : 'N/A' },
    { icon: <Shield size={16} />, label: 'Status', value: user?.is_active ? 'Active' : 'Inactive' },
  ]

  return (
    <div style={{ padding: 32, maxWidth: 700 }}>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '1.8rem', marginBottom: 6 }}>Profile</h1>
        <p style={{ color: 'var(--color-text-secondary)' }}>Manage your account information</p>
      </div>

      {/* Avatar & header */}
      <div className="card" style={{ marginBottom: 20, display: 'flex', alignItems: 'center', gap: 20 }}>
        <div style={{
          width: 80, height: 80,
          background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent))',
          borderRadius: '50%',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '2rem', fontWeight: 800, color: 'white',
          fontFamily: 'var(--font-display)',
          flexShrink: 0,
          boxShadow: '0 0 30px var(--color-primary-glow)',
        }}>
          {user?.username?.[0]?.toUpperCase() || 'U'}
        </div>
        <div style={{ flex: 1 }}>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.4rem', marginBottom: 4 }}>{user?.username}</h2>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>{user?.email}</p>
          <span className="badge badge-success" style={{ marginTop: 8, display: 'inline-flex' }}>Active</span>
        </div>
        <button
          className="btn btn-ghost"
          onClick={() => setEditing(v => !v)}
          style={{ alignSelf: 'flex-start' }}
        >
          <Edit2 size={14} /> {editing ? 'Cancel' : 'Edit'}
        </button>
      </div>

      {/* Edit form */}
      {editing && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ fontFamily: 'var(--font-display)', marginBottom: 20 }}>Edit Profile</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 500, marginBottom: 6, color: 'var(--color-text-secondary)' }}>Username</label>
              <input
                className="input"
                value={form.username}
                onChange={e => setForm(f => ({ ...f, username: e.target.value }))}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 500, marginBottom: 6, color: 'var(--color-text-secondary)' }}>Email</label>
              <input
                className="input"
                type="email"
                value={form.email}
                onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
              />
            </div>
            <button className="btn btn-primary" onClick={handleSave} style={{ alignSelf: 'flex-start' }}>
              <Save size={14} /> Save Changes
            </button>
          </div>
        </div>
      )}

      {/* Info */}
      <div className="card" style={{ marginBottom: 20 }}>
        <h3 style={{ fontFamily: 'var(--font-display)', marginBottom: 20 }}>Account Information</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
          {infoItems.map(({ icon, label, value }, i) => (
            <div key={label} style={{
              display: 'flex', alignItems: 'center', gap: 12,
              padding: '14px 0',
              borderBottom: i < infoItems.length - 1 ? '1px solid var(--color-border)' : 'none',
            }}>
              <div style={{ color: 'var(--color-primary)', width: 32, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {icon}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: 2 }}>{label}</div>
                <div style={{ fontSize: '0.9rem', fontWeight: 500 }}>{value || '—'}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Danger zone */}
      <div className="card" style={{ borderColor: 'rgba(248,113,113,0.2)' }}>
        <h3 style={{ fontFamily: 'var(--font-display)', marginBottom: 8, color: 'var(--color-error)' }}>Danger Zone</h3>
        <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.85rem', marginBottom: 16 }}>
          Once you log out, you will need your credentials to sign back in.
        </p>
        <button className="btn btn-danger" onClick={logout}>Sign Out</button>
      </div>
    </div>
  )
}
