import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authService } from '../services/authService'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const init = async () => {
      if (authService.isAuthenticated()) {
        try {
          const me = await authService.getMe()
          setUser(me)
        } catch {
          authService.logout()
        }
      }
      setLoading(false)
    }
    init()
  }, [])

  const login = useCallback(async (email, password) => {
    await authService.login(email, password)
    const me = await authService.getMe()
    setUser(me)
  }, [])

  const register = useCallback(async (email, username, password) => {
    await authService.register(email, username, password)
    // Minimal user from token for now
    setUser({ email, username })
  }, [])

  const logout = useCallback(() => {
    authService.logout()
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
