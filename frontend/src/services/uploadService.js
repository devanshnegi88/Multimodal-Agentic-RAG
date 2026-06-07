import api from './api'

export const uploadService = {
  async uploadFiles(files, onProgress) {
    const formData = new FormData()
    files.forEach((f) => formData.append('files', f))

    const { data } = await api.post('/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        const pct = Math.round((e.loaded * 100) / e.total)
        onProgress?.(pct)
      },
    })
    return data
  },

  async getUploadStatus(docId) {
    const { data } = await api.get(`/upload/status/${docId}`)
    return data
  },

  pollStatus(docId, onUpdate, intervalMs = 2000) {
    const interval = setInterval(async () => {
      try {
        const status = await this.getUploadStatus(docId)
        onUpdate(status)
        if (status.status === 'ready' || status.status === 'failed') {
          clearInterval(interval)
        }
      } catch {
        clearInterval(interval)
      }
    }, intervalMs)
    return () => clearInterval(interval)
  },
}
