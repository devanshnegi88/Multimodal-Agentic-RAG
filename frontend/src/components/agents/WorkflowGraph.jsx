export default function WorkflowGraph() {
  return (
    <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--color-text-secondary)' }}>
      {['Memory','Planner','Retrieval','Vision','Web','Critic','Answer'].map((n,i,arr) => (
        <span key={n} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ padding: '2px 8px', background: 'var(--color-surface-elevated)', borderRadius: 4, border: '1px solid var(--color-border)' }}>{n}</span>
          {i < arr.length - 1 && <span>→</span>}
        </span>
      ))}
    </div>
  )
}
