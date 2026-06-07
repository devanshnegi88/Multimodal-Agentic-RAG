import { useAgents } from '../../context/AgentContext'
export default function PlannerStatus() {
  const { currentPlan, agents } = useAgents()
  if (!currentPlan || agents.planner.status === 'idle') return null
  return (
    <div style={{ padding: '8px 12px', background: 'var(--color-primary-dim)', borderRadius: 'var(--radius-md)', fontSize: '0.78rem', fontFamily: 'var(--font-mono)', color: 'var(--color-primary)', marginBottom: 8 }}>
      Plan: {currentPlan.strategy} · top_k={currentPlan.top_k} · intent={currentPlan.intent}
    </div>
  )
}
