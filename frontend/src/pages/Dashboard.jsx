import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { MessageSquare, FileText, Zap, Clock, ArrowRight, Upload } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { analyticsService } from '../services/analyticsService'
import { chatService } from '../services/chatService'
import { useChat } from '../context/ChatContext'
import UsageChart from '../components/analytics/UsageChart'
import '../styles/dashboard.css'

export default function Dashboard() {
  const { user } = useAuth()
  const { sessions, loadSessions } = useChat()
  const [overview, setOverview] = useState(null)
  const [usageData, setUsageData] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    loadSessions()
    analyticsService.getOverview().then(setOverview).catch(() => {})
    analyticsService.getUsage(7).then(d => setUsageData(d.daily_usage || [])).catch(() => {})
  }, [])

  const stats = [
    { label: 'Total Queries', value: overview?.total_queries ?? '—', icon: <MessageSquare size={20} />, color: 'var(--color-primary)' },
    { label: 'Documents', value: overview?.total_documents ?? '—', icon: <FileText size={20} />, color: 'var(--color-accent)' },
    { label: 'Chat Sessions', value: overview?.total_sessions ?? '—', icon: <Zap size={20} />, color: 'var(--color-accent-2)' },
    { label: 'Avg Response', value: overview ? `${overview.avg_response_time_ms}ms` : '—', icon: <Clock size={20} />, color: 'var(--color-success)' },
  ]

  return (
    <div className="dashboard-page">
      {/* Header */}
      <div className="dashboard-header">
        <h1>Good {getGreeting()}, {user?.username || 'there'} 👋</h1>
        <p style={{ color: 'var(--color-text-secondary)', marginTop: 6 }}>Here's what's happening with your knowledge base</p>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        {stats.map(({ label, value, icon, color }) => (
          <div key={label} className="stat-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
              <div style={{ color }}>{icon}</div>
            </div>
            <div className="stat-value" style={{ color }}>{value}</div>
            <div className="stat-label">{label}</div>
          </div>
        ))}
      </div>

      {/* Main grid */}
      <div className="dashboard-grid">
        {/* Usage chart */}
        <div>
          <UsageChart data={usageData} />
        </div>

        {/* Recent sessions */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1rem' }}>Recent Chats</h3>
            <button className="btn btn-ghost" style={{ padding: '5px 10px', fontSize: '0.78rem' }} onClick={() => navigate('/chat')}>
              View all <ArrowRight size={12} />
            </button>
          </div>
          {sessions.slice(0, 5).length === 0 ? (
            <div style={{ textAlign: 'center', padding: '24px 0', color: 'var(--color-text-muted)' }}>
              <MessageSquare size={32} style={{ margin: '0 auto 8px', opacity: 0.4 }} />
              <p style={{ fontSize: '0.85rem' }}>No chats yet. Start one!</p>
              <button className="btn btn-primary" style={{ marginTop: 12 }} onClick={() => navigate('/chat')}>
                <MessageSquare size={14} /> New Chat
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {sessions.slice(0, 5).map(s => (
                <div key={s._id} onClick={() => navigate(`/chat/${s._id}`)} style={{
                  padding: '10px 12px',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--color-border)',
                  cursor: 'pointer',
                  transition: 'all 0.15s',
                  fontSize: '0.85rem',
                }} onMouseOver={e => e.currentTarget.style.borderColor = 'var(--color-primary)'}
                  onMouseOut={e => e.currentTarget.style.borderColor = 'var(--color-border)'}
                >
                  <div style={{ fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{s.title}</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)', marginTop: 2, fontFamily: 'var(--font-mono)' }}>
                    {s.messages?.length || 0} messages
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick actions */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 16, marginTop: 24 }}>
        {[
          { label: 'New Chat', desc: 'Start a conversation', icon: <MessageSquare size={22} />, to: '/chat', color: 'var(--color-primary)' },
          { label: 'Upload Docs', desc: 'Add to knowledge base', icon: <Upload size={22} />, to: '/documents', color: 'var(--color-accent)' },
          { label: 'Analytics', desc: 'View usage stats', icon: <Zap size={22} />, to: '/analytics', color: 'var(--color-accent-2)' },
        ].map(({ label, desc, icon, to, color }) => (
          <button key={label} className="card" onClick={() => navigate(to)} style={{ cursor: 'pointer', textAlign: 'left', transition: 'all 0.2s', border: '1px solid var(--color-border)' }}
            onMouseOver={e => { e.currentTarget.style.borderColor = color; e.currentTarget.style.transform = 'translateY(-2px)' }}
            onMouseOut={e => { e.currentTarget.style.borderColor = 'var(--color-border)'; e.currentTarget.style.transform = '' }}
          >
            <div style={{ color, marginBottom: 12 }}>{icon}</div>
            <div style={{ fontWeight: 600, fontFamily: 'var(--font-display)', marginBottom: 4 }}>{label}</div>
            <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.8rem' }}>{desc}</div>
          </button>
        ))}
      </div>
    </div>
  )
}

function getGreeting() {
  const h = new Date().getHours()
  if (h < 12) return 'morning'
  if (h < 18) return 'afternoon'
  return 'evening'
}
