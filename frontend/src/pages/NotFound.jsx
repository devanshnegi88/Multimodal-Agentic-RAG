import { useNavigate } from 'react-router-dom'
import { Home, AlertTriangle } from 'lucide-react'

export default function NotFound() {
  const navigate = useNavigate()

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--color-bg)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'column',
      gap: 24,
      padding: 32,
      textAlign: 'center',
    }} className="bg-grid">
      <div style={{
        width: 80, height: 80,
        background: 'rgba(248,113,113,0.1)',
        border: '1px solid rgba(248,113,113,0.3)',
        borderRadius: '50%',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        <AlertTriangle size={36} color="var(--color-error)" />
      </div>

      <div>
        <div style={{ fontFamily: 'var(--font-display)', fontSize: '6rem', fontWeight: 900, color: 'var(--color-primary)', lineHeight: 1, marginBottom: 8 }}>404</div>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.6rem', marginBottom: 8 }}>Page not found</h2>
        <p style={{ color: 'var(--color-text-secondary)', maxWidth: 400, margin: '0 auto' }}>
          The page you're looking for doesn't exist or has been moved.
        </p>
      </div>

      <button className="btn btn-primary" onClick={() => navigate('/')}>
        <Home size={15} /> Back to Dashboard
      </button>
    </div>
  )
}
