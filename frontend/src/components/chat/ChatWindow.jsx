import { useEffect, useRef } from 'react'
import { useChat } from '../../context/ChatContext'
import MessageBubble from './MessageBubble'
import StreamingMessage from './StreamingMessage'
import { MessageSquare } from 'lucide-react'

export default function ChatWindow() {
  const { messages, isStreaming } = useChat()
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (messages.length === 0) {
    return (
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 16,
        color: 'var(--color-text-muted)',
      }}>
        <div style={{
          width: 64, height: 64,
          background: 'var(--color-primary-dim)',
          border: '1px solid var(--color-border)',
          borderRadius: '50%',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <MessageSquare size={28} color="var(--color-primary)" />
        </div>
        <div style={{ textAlign: 'center' }}>
          <p style={{ fontFamily: 'var(--font-display)', fontSize: '1.1rem', color: 'var(--color-text-secondary)', marginBottom: 4 }}>
            Start a conversation
          </p>
          <p style={{ fontSize: '0.85rem' }}>Upload documents and ask questions about them</p>
        </div>
      </div>
    )
  }

  return (
    <div className="messages-area">
      {messages.map((msg, i) => (
        msg.streaming
          ? <StreamingMessage key={msg._id || i} content={msg.content} />
          : <MessageBubble key={msg._id || i} message={msg} />
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
