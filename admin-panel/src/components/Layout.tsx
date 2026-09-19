import { Link, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

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


  return (
    <div>
      <nav>
        <Link to="/requests">Заявки</Link>
        <Link to="/admins">Админы</Link>
        <Link to="/users">Пользователи</Link>
        <button onClick={handleLogout}>Выйти</button>
      </nav>
      <Outlet />
    </div>
  )
}

export default Layout