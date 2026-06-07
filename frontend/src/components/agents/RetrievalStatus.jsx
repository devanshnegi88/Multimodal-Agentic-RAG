import { useAgents } from '../../context/AgentContext'
export default function RetrievalStatus() {
  const { agents } = useAgents()
  const a = agents.retrieval
  if (a.status === 'idle') return null
  return (
    <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--color-text-secondary)' }}>
      Retrieval: {a.count !== undefined ? `${a.count} chunks` : a.status}
    </div>
  )
}
