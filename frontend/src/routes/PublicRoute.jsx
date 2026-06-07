import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Loader from '../components/common/Loader'

export default function PublicRoute() {
  const { isAuthenticated, loading } = useAuth()

  if (loading) return <Loader fullscreen />
  if (isAuthenticated) return <Navigate to="/" replace />

  return <Outlet />
}
