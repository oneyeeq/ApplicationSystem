import { useEffect, useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { useApiFetch } from '../api/useApiFetch'
import tableStyles from '../components/Table.module.css'
import styles from './UsersPage.module.css'

interface UserItem {
  id: number
  tg_user_id: number
  username: string | null
  is_active: boolean
  active_requests: number
}

interface PaginatedUsers {
  items: UserItem[]
  total: number
  page: number
  page_size: number
}

const PAGE_SIZE = 20

function UsersPage() {
  const { token } = useAuth()
  const apiFetch = useApiFetch()
  const [users, setUsers] = useState<UserItem[]>([])
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [errorMessage, setErrorMessage] = useState('')

  async function loadUsers() {
    const response = await apiFetch(`/users/paginated?page=${page}&page_size=${PAGE_SIZE}`)
    const data: PaginatedUsers = await response.json()
    if (response.ok) {
      setUsers(data.items)
      setTotal(data.total)
    }
  }

  useEffect(() => {
    loadUsers()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, page])

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  async function handleToggleActive(userId: number, newIsActive: boolean) {
    const response = await apiFetch(`/users/${userId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_active: newIsActive }),
    })
    const data = await response.json()
    if (response.ok) {
      setUsers(users.map((u) => (u.id === userId ? data : u)))
    }
  }

  async function handleDeleteUser(userId: number) {
    const response = await apiFetch(`/users/${userId}`, { method: 'DELETE' })
    if (response.ok) {
      await loadUsers()
      setErrorMessage('')
    } else {
      const data = await response.json()
      setErrorMessage(typeof data.detail === 'string' ? data.detail : 'Не удалось удалить пользователя')
    }
  }

  return (
    <>
      <h1>Пользователи</h1>
      <div className={tableStyles.card}>
        <table className={tableStyles.table}>
          <thead>
            <tr>
              <th>ID</th>
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
                <td>{user.id}</td>
                <td>{user.tg_user_id}</td>
                <td>{user.username ?? 'не указан'}</td>
                <td>{user.active_requests}</td>
                <td>{user.is_active ? 'активен' : 'заблокирован'}</td>
                <td>
                  <button
                    className={user.is_active ? 'danger' : 'primary'}
                    onClick={() => handleToggleActive(user.id, !user.is_active)}
                  >
                    {user.is_active ? 'Заблокировать' : 'Разблокировать'}
                  </button>
                  <button className="danger" onClick={() => handleDeleteUser(user.id)}>
                    Удалить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className={tableStyles.pagination}>
        <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
          ← Назад
        </button>
        <span className={tableStyles.pageInfo}>
          Стр. {page} из {totalPages}
        </span>
        <button disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
          Вперёд →
        </button>
      </div>
      {errorMessage && <p className={styles.error}>{errorMessage}</p>}
    </>
  )
}

export default UsersPage
