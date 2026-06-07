import api from './api'

export const documentService = {
  async listDocuments(params = {}) {
    const { data } = await api.get('/documents/', { params })
    return data
  },

  async getDocument(docId) {
    const { data } = await api.get(`/documents/${docId}`)
    return data
  },

  async deleteDocument(docId) {
    await api.delete(`/documents/${docId}`)
  },

  async getDocumentChunks(docId) {
    const { data } = await api.get(`/documents/${docId}/chunks`)
    return data
  },
}
