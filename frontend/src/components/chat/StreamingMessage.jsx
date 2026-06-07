// StreamingMessage.jsx
export function StreamingMessage({ content }) {
  return (
    <div className="message-bubble assistant">
      <div style={{
        width: 28, height: 28,
        background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent))',
        borderRadius: '50%',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '0.7rem', fontWeight: 700, color: 'white',
        marginBottom: 8,
        animation: 'pulse 1.5s ease infinite',
      }}>
        AI
      </div>
      <div className="message-content">
        <span>{content}</span>
        <span className="typing-cursor" />
      </div>
    </div>
  )
}
export default StreamingMessage
