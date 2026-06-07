import api from './api'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

export const chatService = {
  async sendMessage(payload) {
    const { data } = await api.post('/chat/message', payload)
    return data
  },

  async getSessions() {
    const { data } = await api.get('/chat/sessions')
    return data.sessions
  },

  async getSession(sessionId) {
    const { data } = await api.get(`/chat/sessions/${sessionId}`)
    return data
  },

  async deleteSession(sessionId) {
    await api.delete(`/chat/sessions/${sessionId}`)
  },

  connectWebSocket(sessionId, { onToken, onStatus, onDone, onError }) {
    const token = localStorage.getItem('access_token')
    const ws = new WebSocket(`${WS_URL}/api/chat/ws/${sessionId}?token=${token}`)

    ws.onopen = () => console.log('[WS] Connected:', sessionId)
    ws.onclose = () => console.log('[WS] Disconnected')
    ws.onerror = (e) => onError?.(e)

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data)
      if (msg.type === 'token') onToken?.(msg.data.text)
      else if (msg.type === 'status') onStatus?.(msg.data)
      else if (msg.type === 'done') onDone?.(msg.data)
      else if (msg.type === 'error') onError?.(msg.data)
    }

    return ws
  },
}
