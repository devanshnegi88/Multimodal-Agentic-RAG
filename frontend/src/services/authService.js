import api from './api'

export const authService = {
  async login(email, password) {
    const { data } = await api.post('/auth/login', { email, password })
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    return data
  },

  async register(email, username, password) {
    const { data } = await api.post('/auth/register', { email, username, password })
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    return data
  },

  async getMe() {
    const { data } = await api.get('/auth/me')
    return data
  },

  logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  },

  isAuthenticated() {
    return !!localStorage.getItem('access_token')
  },
}
