import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { format } from 'date-fns'
import CitationViewer from './CitationViewer'
import SourceCard from './SourceCard'

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  const time = message.timestamp ? format(new Date(message.timestamp), 'HH:mm') : ''

  return (
    <div className={`message-bubble ${isUser ? 'user' : 'assistant'}`}>
      {!isUser && (
        <div style={{
          width: 28, height: 28,
          background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent))',
          borderRadius: '50%',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '0.7rem', fontWeight: 700, color: 'white',
          marginBottom: 8, flexShrink: 0,
        }}>
          AI
        </div>
      )}

      <div className="message-content">
        {isUser ? (
          <p style={{ margin: 0 }}>{message.content}</p>
        ) : (
          <ReactMarkdown remarkPlugins={[remarkGfm]} components={{
            code({ node, inline, className, children, ...props }) {
              return inline
                ? <code style={{ background: 'var(--color-bg)', padding: '1px 6px', borderRadius: 4, fontFamily: 'var(--font-mono)', fontSize: '0.85em' }} {...props}>{children}</code>
                : <pre style={{ background: 'var(--color-bg)', padding: 12, borderRadius: 8, overflow: 'auto', margin: '8px 0' }}><code style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85em' }} {...props}>{children}</code></pre>
            },
            p({ children }) { return <p style={{ margin: '0 0 8px' }}>{children}</p> },
            ul({ children }) { return <ul style={{ paddingLeft: 20, margin: '4px 0' }}>{children}</ul> },
            ol({ children }) { return <ol style={{ paddingLeft: 20, margin: '4px 0' }}>{children}</ol> },
          }}>
            {message.content}
          </ReactMarkdown>
        )}
      </div>

      {/* Citations */}
      {message.citations?.length > 0 && (
        <CitationViewer citations={message.citations} />
      )}

      {/* Sources */}
      {message.sources?.length > 0 && (
        <div style={{ marginTop: 8, display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {message.sources.map((src, i) => <SourceCard key={i} source={src} index={i + 1} />)}
        </div>
      )}

      <div style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', marginTop: 6, textAlign: isUser ? 'right' : 'left', fontFamily: 'var(--font-mono)' }}>
        {time}
      </div>
    </div>
  )
}
