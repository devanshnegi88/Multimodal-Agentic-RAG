import { createContext, useContext, useState, useCallback, useRef } from 'react'
import { chatService } from '../services/chatService'
import toast from 'react-hot-toast'

const ChatContext = createContext(null)

export function ChatProvider({ children }) {
  const [sessions, setSessions] = useState([])
  const [currentSession, setCurrentSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [agentStatus, setAgentStatus] = useState({})
  const wsRef = useRef(null)

  const loadSessions = useCallback(async () => {
    try {
      const data = await chatService.getSessions()
      setSessions(data)
    } catch (e) {
      toast.error('Failed to load sessions')
    }
  }, [])

  const loadSession = useCallback(async (sessionId) => {
    try {
      const session = await chatService.getSession(sessionId)
      setCurrentSession(session)
      setMessages(session.messages || [])
      return session
    } catch (e) {
      toast.error('Session not found')
    }
  }, [])

  const sendMessage = useCallback(async ({ message, documentIds = [], useWebSearch = false, sessionId }) => {
    // Optimistically add user message
    const userMsg = { role: 'user', content: message, timestamp: new Date().toISOString() }
    setMessages((prev) => [...prev, userMsg])
    setIsStreaming(true)
    setAgentStatus({})

    // Placeholder for streaming assistant message
    const placeholderId = Date.now()
    setMessages((prev) => [...prev, { role: 'assistant', content: '', _id: placeholderId, streaming: true }])

    try {
      // Use REST endpoint (switch to WS for real streaming)
      const result = await chatService.sendMessage({
        message,
        session_id: sessionId || currentSession?._id || null,
        document_ids: documentIds,
        use_web_search: useWebSearch,
        stream: false,
      })

      // Update placeholder with real answer
      setMessages((prev) =>
        prev.map((m) =>
          m._id === placeholderId
            ? { ...result.message, _id: placeholderId, streaming: false, citations: result.citations }
            : m
        )
      )

      if (!currentSession) {
        setCurrentSession({ _id: result.session_id })
        loadSessions()
      }

      return result
    } catch (e) {
      setMessages((prev) => prev.filter((m) => m._id !== placeholderId))
      toast.error('Failed to send message')
    } finally {
      setIsStreaming(false)
    }
  }, [currentSession, loadSessions])

  const deleteSession = useCallback(async (sessionId) => {
    try {
      await chatService.deleteSession(sessionId)
      setSessions((prev) => prev.filter((s) => s._id !== sessionId))
      if (currentSession?._id === sessionId) {
        setCurrentSession(null)
        setMessages([])
      }
    } catch {
      toast.error('Failed to delete session')
    }
  }, [currentSession])

  const newChat = useCallback(() => {
    setCurrentSession(null)
    setMessages([])
    setAgentStatus({})
    if (wsRef.current) wsRef.current.close()
  }, [])

  return (
    <ChatContext.Provider value={{
      sessions, currentSession, messages, isStreaming, agentStatus,
      loadSessions, loadSession, sendMessage, deleteSession, newChat,
    }}>
      {children}
    </ChatContext.Provider>
  )
}

export const useChat = () => {
  const ctx = useContext(ChatContext)
  if (!ctx) throw new Error('useChat must be used inside ChatProvider')
  return ctx
}
