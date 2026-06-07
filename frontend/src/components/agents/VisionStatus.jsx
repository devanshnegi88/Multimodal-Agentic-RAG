import { useAgents } from '../../context/AgentContext'
export default function VisionStatus() {
  const { agents } = useAgents()
  const a = agents.vision
  if (a.status === 'idle') return null
  return <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--color-accent)' }}>Vision: {a.status}</div>
}
