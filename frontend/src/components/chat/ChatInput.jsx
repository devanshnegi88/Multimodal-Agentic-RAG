import { useState, useRef } from 'react'
import { Send, Globe, Paperclip, Mic } from 'lucide-react'
import { useChat } from '../../context/ChatContext'
import { useAgents } from '../../context/AgentContext'

export default function ChatInput({ documentIds = [], sessionId }) {
  const [value, setValue] = useState('')
  const [useWebSearch, setUseWebSearch] = useState(false)
  const { sendMessage, isStreaming } = useChat()
  const { resetAgents } = useAgents()
  const textareaRef = useRef(null)

  const handleSubmit = async () => {
    const msg = value.trim()
    if (!msg || isStreaming) return

    setValue('')
    resetAgents()
    await sendMessage({ message: msg, documentIds, useWebSearch, sessionId })
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="chat-input-area">
      {/* Options Bar */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
        <button
          onClick={() => setUseWebSearch(v => !v)}
          style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '5px 12px',
            borderRadius: 100,
            border: `1px solid ${useWebSearch ? 'var(--color-primary)' : 'var(--color-border)'}`,
            background: useWebSearch ? 'var(--color-primary-dim)' : 'transparent',
            color: useWebSearch ? 'var(--color-primary)' : 'var(--color-text-secondary)',
            cursor: 'pointer', fontSize: '0.78rem', fontFamily: 'var(--font-mono)',
            transition: 'all 0.2s',
          }}
        >
          <Globe size={13} /> Web Search
        </button>
      </div>

      {/* Input Row */}
      <div style={{
        display: 'flex',
        alignItems: 'flex-end',
        gap: 10,
        background: 'var(--color-surface-elevated)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-lg)',
        padding: '10px 14px',
        transition: 'border-color 0.2s',
      }}
        onFocus={() => {}} // handled by child
      >
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything about your documents…"
          rows={1}
          disabled={isStreaming}
          style={{
            flex: 1,
            background: 'none',
            border: 'none',
            outline: 'none',
            resize: 'none',
            color: 'var(--color-text)',
            fontFamily: 'var(--font-body)',
            fontSize: '0.9rem',
            lineHeight: 1.6,
            maxHeight: 160,
            overflowY: 'auto',
          }}
          onInput={(e) => {
            e.target.style.height = 'auto'
            e.target.style.height = Math.min(e.target.scrollHeight, 160) + 'px'
          }}
        />

        <button
          onClick={handleSubmit}
          disabled={!value.trim() || isStreaming}
          style={{
            width: 38, height: 38,
            background: value.trim() && !isStreaming ? 'var(--color-primary)' : 'var(--color-border)',
            border: 'none',
            borderRadius: 'var(--radius-md)',
            cursor: value.trim() && !isStreaming ? 'pointer' : 'not-allowed',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: 'white',
            transition: 'all 0.2s',
            flexShrink: 0,
          }}
        >
          {isStreaming
            ? <div style={{ width: 16, height: 16, border: '2px solid white', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
            : <Send size={16} />}
        </button>
      </div>

      <p style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', textAlign: 'center', marginTop: 8 }}>
        Press Enter to send · Shift+Enter for new line
      </p>
    </div>
  )
}
