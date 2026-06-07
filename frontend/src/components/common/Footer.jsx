export default function Footer() {
  return (
    <footer style={{
      padding: '16px 24px',
      borderTop: '1px solid var(--color-border)',
      textAlign: 'center',
      color: 'var(--color-text-muted)',
      fontSize: '0.75rem',
      fontFamily: 'var(--font-mono)',
    }}>
      Multimodal Agentic RAG © {new Date().getFullYear()} — Powered by Claude + LangGraph
    </footer>
  )
}
