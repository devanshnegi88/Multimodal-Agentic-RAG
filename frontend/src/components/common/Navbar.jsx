import { useLocation } from 'react-router-dom'
import { Sun, Moon, Bell } from 'lucide-react'
import { useTheme } from '../../context/ThemeContext'
import ThemeToggle from './ThemeToggle'

const PAGE_TITLES = {
  '/': 'Dashboard',
  '/chat': 'Chat',
  '/documents': 'Documents',
  '/analytics': 'Analytics',
  '/settings': 'Settings',
  '/profile': 'Profile',
}

export default function Navbar() {
  const { pathname } = useLocation()
  const title = PAGE_TITLES[pathname] || PAGE_TITLES[Object.keys(PAGE_TITLES).find(k => pathname.startsWith(k) && k !== '/')] || 'Page'

  return (
    <header style={{
      height: 'var(--header-height)',
      background: 'var(--color-surface)',
      borderBottom: '1px solid var(--color-border)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 24px',
      position: 'sticky',
      top: 0,
      zIndex: 50,
    }}>
      <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.2rem', fontWeight: 700 }}>
        {title}
      </h2>

      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <ThemeToggle />
        <button
          style={{
            width: 36, height: 36,
            background: 'none',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)',
            cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: 'var(--color-text-secondary)',
          }}
        >
          <Bell size={16} />
        </button>
      </div>
    </header>
  )
}
