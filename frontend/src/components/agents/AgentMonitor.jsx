import { useAgents } from '../../context/AgentContext'
import { CheckCircle, Circle, Loader, AlertCircle } from 'lucide-react'

const STATUS_ICONS = {
  idle: <Circle size={14} color="var(--color-text-muted)" />,
  running: <Loader size={14} color="var(--color-warning)" style={{ animation: 'spin 0.8s linear infinite' }} />,
  done: <CheckCircle size={14} color="var(--color-success)" />,
  error: <AlertCircle size={14} color="var(--color-error)" />,
}

const STATUS_COLORS = {
  idle: 'var(--color-text-muted)',
  running: 'var(--color-warning)',
  done: 'var(--color-success)',
  error: 'var(--color-error)',
}

const AGENT_ORDER = ['memory', 'planner', 'retrieval', 'vision', 'web_search', 'critic', 'answer']

export default function AgentMonitor() {
  const { agents } = useAgents()
  const anyActive = Object.values(agents).some(a => a.status !== 'idle')
  if (!anyActive) return null

  return (
    <div style={{
      background: 'var(--color-surface)',
      border: '1px solid var(--color-border)',
      borderRadius: 'var(--radius-lg)',
      padding: '16px 20px',
      marginBottom: 16,
    }}>
      <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--color-text-muted)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
        Agent Pipeline
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 0, flexWrap: 'wrap' }}>
        {AGENT_ORDER.map((agentKey, i) => {
          const agent = agents[agentKey]
          return (
            <div key={agentKey} style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{
                display: 'flex', alignItems: 'center', gap: 6,
                padding: '5px 10px',
                borderRadius: 100,
                background: agent.status !== 'idle' ? 'var(--color-primary-dim)' : 'transparent',
                border: `1px solid ${agent.status !== 'idle' ? 'var(--color-border-hover)' : 'transparent'}`,
                transition: 'all 0.3s',
              }}>
                {STATUS_ICONS[agent.status]}
                <span style={{
                  fontSize: '0.75rem',
                  fontFamily: 'var(--font-mono)',
                  color: STATUS_COLORS[agent.status],
                  fontWeight: agent.status === 'running' ? 600 : 400,
                }}>
                  {agent.label || agentKey}
                </span>
              </div>
              {i < AGENT_ORDER.length - 1 && (
                <div style={{ width: 16, height: 1, background: 'var(--color-border)', margin: '0 2px' }} />
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
