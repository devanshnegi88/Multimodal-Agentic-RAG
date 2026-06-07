import api from './api'

export const analyticsService = {
  async getOverview() {
    const { data } = await api.get('/analytics/overview')
    return data
  },

  async getUsage(days = 7) {
    const { data } = await api.get('/analytics/usage', { params: { days } })
    return data
  },

  async getAgentStats() {
    const { data } = await api.get('/analytics/agents')
    return data
  },

  async getDocumentStats() {
    const { data } = await api.get('/analytics/documents')
    return data
  },
}
