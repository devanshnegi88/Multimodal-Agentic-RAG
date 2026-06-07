import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Trash2, Plus, ChevronRight, FileText } from 'lucide-react'
import { useChat } from '../context/ChatContext'
import ChatWindow from '../components/chat/ChatWindow'
import ChatInput from '../components/chat/ChatInput'
import AgentMonitor from '../components/agents/AgentMonitor'
import { format } from 'date-fns'
import '../styles/chat.css'

export default function Chat() {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const { sessions, currentSession, loadSessions, loadSession, deleteSession, newChat } = useChat()
  const [selectedDocs, setSelectedDocs] = useState([])

  useEffect(() => {
    loadSessions()
  }, [])

  useEffect(() => {
    if (sessionId) loadSession(sessionId)
  }, [sessionId])

  const handleNewChat = () => {
    newChat()
    navigate('/chat')
  }

  const handleDeleteSession = async (e, sid) => {
    e.stopPropagation()
    await deleteSession(sid)
    if (sessionId === sid) navigate('/chat')
  }

  return (
    <div className="chat-layout">
      {/* Sessions Sidebar */}
      <div className="chat-sidebar">
        <div className="chat-sidebar-header">
          <span style={{ fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: '0.9rem' }}>Conversations</span>
          <button className="btn btn-ghost" style={{ padding: '4px 8px', fontSize: '0.78rem' }} onClick={handleNewChat}>
            <Plus size={13} /> New
          </button>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: '8px' }}>
          {sessions.length === 0 ? (
            <p style={{ color: 'var(--color-text-muted)', fontSize: '0.82rem', textAlign: 'center', padding: 16 }}>No conversations yet</p>
          ) : (
            sessions.map(s => (
              <div key={s._id} onClick={() => navigate(`/chat/${s._id}`)} style={{
                padding: '10px 12px',
                borderRadius: 'var(--radius-md)',
                cursor: 'pointer',
                transition: 'all 0.15s',
                marginBottom: 2,
                display: 'flex', alignItems: 'center', gap: 8,
                background: currentSession?._id === s._id ? 'var(--color-primary-dim)' : 'transparent',
                border: `1px solid ${currentSession?._id === s._id ? 'var(--color-border-hover)' : 'transparent'}`,
              }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: '0.82rem', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {s.title || 'Untitled'}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)', marginTop: 1 }}>
                    {s.messages?.length || 0} msgs
                  </div>
                </div>
                <button onClick={e => handleDeleteSession(e, s._id)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)', padding: 2, opacity: 0, transition: 'opacity 0.15s' }}
                  onMouseOver={e => e.currentTarget.style.opacity = 1}
                  onMouseOut={e => e.currentTarget.style.opacity = 0}
                >
                  <Trash2 size={12} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="chat-main">
        {/* Agent Monitor Banner */}
        <div style={{ padding: '12px 24px 0' }}>
          <AgentMonitor />
        </div>

        {/* Messages */}
        <ChatWindow />

        {/* Input */}
        <ChatInput
          documentIds={selectedDocs}
          sessionId={currentSession?._id}
        />
      </div>
    </div>
  )
}
