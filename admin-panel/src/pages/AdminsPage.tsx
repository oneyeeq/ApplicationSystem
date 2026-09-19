import { useEffect, useState } from 'react'
import { useAuth } from '../auth/AuthContext'

interface AdminItem {
  id: number
  login: string
  tg_admin_id: number | null
  username: string | null
  is_active: boolean
}

function AdminsPage() {
  const { token } = useAuth()
  const [admins, setAdmins] = useState<AdminItem[]>([])
  const [login, setLogin] = useState('')
  const [password, setPassword] = useState('')
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    async function loadAdmins() {
      const response = await fetch('http://localhost:8000/admins/', {
        headers: { Authorization: `Bearer ${token}` },
        credentials: 'include',
      })
      const data = await response.json()
      if (response.ok) {
        setAdmins(data)
      }
    }
    loadAdmins()
  }, [token])

  async function handleCreateAdmin() {
    const response = await fetch('http://localhost:8000/admins/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      credentials: 'include',
      body: JSON.stringify({ login, password }),
    })
    const data = await response.json()
    if (response.ok) {
      setAdmins([...admins, data])
      setLogin('')
      setPassword('')
      setErrorMessage('')
    } else {
      setErrorMessage(typeof data.detail === 'string' ? data.detail : 'Некорректные данные')
    }
  }

  return (
    <div>
      <h1>Админы</h1>
      <table>
        <thead>
          <tr>
            <th>Логин</th>
            <th>Статус</th>
          </tr>
        </thead>
        <tbody>
          {admins.map((admin) => (
            <tr key={admin.id}>
              <td>{admin.login}</td>
              <td>{admin.is_active ? 'активен' : 'не активен'}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Добавить админа</h2>
      <input
        value={login}
        onChange={(e) => setLogin(e.target.value)}
        placeholder="Логин"
      />
      <input
        value={password}
        type="password"
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Пароль"
      />
      <button onClick={handleCreateAdmin}>Создать</button>
      <p>{errorMessage}</p>
    </div>
  )
}

export default AdminsPage
