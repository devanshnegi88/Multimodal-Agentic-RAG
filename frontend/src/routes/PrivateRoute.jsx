import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Sidebar from '../components/common/Sidebar'
import Navbar from '../components/common/Navbar'
import Loader from '../components/common/Loader'

export default function PrivateRoute() {
  const { isAuthenticated, loading } = useAuth()

  if (loading) return <Loader fullscreen />
  if (!isAuthenticated) return <Navigate to="/login" replace />

  return (
    <div className="main-layout">
      <Sidebar />
      <div className="main-content">
        <Navbar />
        <Outlet />
      </div>
    </div>
  )
}
