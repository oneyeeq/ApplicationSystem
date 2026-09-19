import { useEffect, useState } from 'react'
import { useAuth } from '../auth/AuthContext'

interface UserItem {
  id: number
  tg_user_id: number
  username: string | null
  is_active: boolean
  active_requests: number
}

function UsersPage() {
  const { token } = useAuth()
  const [users, setUsers] = useState<UserItem[]>([])

  useEffect(() => {
    async function loadUsers() {
      const response = await fetch('http://localhost:8000/users/', {
        headers: { Authorization: `Bearer ${token}` },
        credentials: 'include',
      })
      const data = await response.json()
      if (response.ok) {
        setUsers(data)
      }
    }
    loadUsers()
  }, [token])

  async function handleToggleActive(userId: number, newIsActive: boolean) {
    const response = await fetch(`http://localhost:8000/users/${userId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      credentials: 'include',
      body: JSON.stringify({ is_active: newIsActive }),
    })
    const data = await response.json()
    if (response.ok) {
      setUsers(users.map((u) => (u.id === userId ? data : u)))
    }
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Telegram ID</th>
          <th>Username</th>
          <th>Активных заявок</th>
          <th>Статус</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        {users.map((user) => (
          <tr key={user.id}>
            <td>{user.tg_user_id}</td>
            <td>{user.username ?? '—'}</td>
            <td>{user.active_requests}</td>
            <td>{user.is_active ? 'активен' : 'заблокирован'}</td>
            <td>
              <button onClick={() => handleToggleActive(user.id, !user.is_active)}>
                {user.is_active ? 'Заблокировать' : 'Разблокировать'}
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default UsersPage
