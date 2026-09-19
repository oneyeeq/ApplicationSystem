import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import styles from './Layout.module.css'

function Layout() {
  const { setToken } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    try {
      await fetch('http://localhost:8000/auth/logout/', {
        method: 'POST',
        credentials: 'include',
      })
    } finally {
      setToken(null)
      navigate('/login')
    }
  }

  function navLinkClassName({ isActive }: { isActive: boolean }) {
    return isActive ? `${styles.navLink} ${styles.navLinkActive}` : styles.navLink
  }

  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar}>
        <div className={styles.brand}>Request Service</div>
        <NavLink to="/requests" className={navLinkClassName}>
          Заявки
        </NavLink>
        <NavLink to="/admins" className={navLinkClassName}>
          Админы
        </NavLink>
        <NavLink to="/users" className={navLinkClassName}>
          Пользователи
        </NavLink>
        <button className={styles.logoutButton} onClick={handleLogout}>
          Выйти
        </button>
      </aside>
      <main className={styles.content}>
        <Outlet />
      </main>
    </div>
  )
}

export default Layout
