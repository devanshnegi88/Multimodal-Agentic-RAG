import { useEffect, useState } from 'react'
import { analyticsService } from '../services/analyticsService'
import UsageChart from '../components/analytics/UsageChart'
import AgentChart from '../components/analytics/AgentChart'
import QueryChart from '../components/analytics/QueryChart'
import AccuracyChart from '../components/analytics/AccuracyChart'
import Loader from '../components/common/Loader'
import '../styles/analytics.css'

export default function Analytics() {
  const [overview, setOverview] = useState(null)
  const [usage, setUsage] = useState([])
  const [agents, setAgents] = useState([])
  const [docStats, setDocStats] = useState([])
  const [days, setDays] = useState(7)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const [ov, us, ag, ds] = await Promise.all([
          analyticsService.getOverview(),
          analyticsService.getUsage(days),
          analyticsService.getAgentStats(),
          analyticsService.getDocumentStats(),
        ])
        setOverview(ov)
        setUsage(us.daily_usage || [])
        setAgents(ag.agent_stats || [])
        setDocStats(ds.document_types || [])
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [days])

  // Mock accuracy data
  const accuracyData = usage.map((u, i) => ({ date: u.date, score: 70 + Math.random() * 25 }))

  if (loading) return <div style={{ padding: 32 }}><Loader text="Loading analytics…" /></div>

  return (
    <div className="analytics-page">
      <div style={{ marginBottom: 28, display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '1.8rem', marginBottom: 6 }}>Analytics</h1>
          <p style={{ color: 'var(--color-text-secondary)' }}>Track usage and performance metrics</p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {[7, 14, 30].map(d => (
            <button key={d} onClick={() => setDays(d)} style={{
              padding: '6px 14px', borderRadius: 100, fontSize: '0.8rem',
              border: `1px solid ${days === d ? 'var(--color-primary)' : 'var(--color-border)'}`,
              background: days === d ? 'var(--color-primary-dim)' : 'transparent',
              color: days === d ? 'var(--color-primary)' : 'var(--color-text-secondary)',
              cursor: 'pointer', fontFamily: 'var(--font-mono)',
            }}>
              {d}d
            </button>
          ))}
        </div>
      </div>

      {/* Overview Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
        {[
          { label: 'Total Queries', value: overview?.total_queries ?? 0 },
          { label: 'Documents', value: overview?.total_documents ?? 0 },
          { label: 'Sessions', value: overview?.total_sessions ?? 0 },
          { label: 'Avg Response', value: `${overview?.avg_response_time_ms ?? 0}ms` },
        ].map(({ label, value }) => (
          <div key={label} className="card" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 800, fontFamily: 'var(--font-display)', color: 'var(--color-primary)' }}>{value}</div>
            <div style={{ fontSize: '0.78rem', color: 'var(--color-text-secondary)', marginTop: 4, textTransform: 'uppercase', letterSpacing: '0.06em' }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="analytics-grid">
        <UsageChart data={usage} />
        <QueryChart data={usage} />
        <AgentChart data={agents} />
        <AccuracyChart data={accuracyData} />
      </div>

      {/* Document breakdown */}
      {docStats.length > 0 && (
        <div className="card" style={{ marginTop: 24 }}>
          <div style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: 16 }}>Document Types</div>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            {docStats.map(({ type, count, total_size_bytes }) => (
              <div key={type} style={{ flex: '1 1 140px', background: 'var(--color-surface-elevated)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', padding: '12px 16px' }}>
                <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--color-primary)', marginBottom: 4 }}>{type.toUpperCase()}</div>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, fontFamily: 'var(--font-display)' }}>{count}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>{(total_size_bytes / 1024 / 1024).toFixed(1)} MB</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
