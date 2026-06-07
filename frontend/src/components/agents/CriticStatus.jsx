import { useAgents } from '../../context/AgentContext'
export default function CriticStatus() {
  const { agents } = useAgents()
  const a = agents.critic
  if (a.status === 'idle') return null
  return <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--color-success)' }}>Critic: {a.verdict || a.status}</div>
}
