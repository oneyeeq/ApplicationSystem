import { useEffect, useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { useApiFetch } from '../api/useApiFetch'
import tableStyles from '../components/Table.module.css'
import styles from './AdminsPage.module.css'

interface AdminItem {
  id: number
  login: string
  tg_admin_id: number | null
  username: string | null
  is_active: boolean
}

interface PaginatedAdmins {
  items: AdminItem[]
  total: number
  page: number
  page_size: number
}

const PAGE_SIZE = 20

function AdminsPage() {
  const { token } = useAuth()
  const apiFetch = useApiFetch()
  const [admins, setAdmins] = useState<AdminItem[]>([])
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [login, setLogin] = useState('')
  const [password, setPassword] = useState('')
  const [tgAdminId, setTgAdminId] = useState('')
  const [username, setUsername] = useState('')
  const [errorMessage, setErrorMessage] = useState('')

  const [editingId, setEditingId] = useState<number | null>(null)
  const [editTgAdminId, setEditTgAdminId] = useState('')
  const [editUsername, setEditUsername] = useState('')

  async function loadAdmins() {
    const response = await apiFetch(`/admins/paginated?page=${page}&page_size=${PAGE_SIZE}`)
    const data: PaginatedAdmins = await response.json()
    if (response.ok) {
      setAdmins(data.items)
      setTotal(data.total)
    }
  }

  useEffect(() => {
    loadAdmins()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, page])

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  async function handleCreateAdmin() {
    const response = await apiFetch('/admins/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        login,
        password,
        tg_admin_id: tgAdminId ? parseInt(tgAdminId, 10) : null,
        username: username || null,
      }),
    })
    const data = await response.json()
    if (response.ok) {
      setLogin('')
      setPassword('')
      setTgAdminId('')
      setUsername('')
      setErrorMessage('')
      // new admins sort first (newest first) — jump to page 1 to see them
      if (page === 1) {
        await loadAdmins()
      } else {
        setPage(1)
      }
    } else {
      setErrorMessage(typeof data.detail === 'string' ? data.detail : 'Некорректные данные')
    }
  }

  async function handleUpdateAdmin(adminId: number, body: Record<string, unknown>) {
    const response = await apiFetch(`/admins/${adminId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    const data = await response.json()
    if (response.ok) {
      setAdmins(admins.map((a) => (a.id === adminId ? data : a)))
    }
    return response.ok
  }

  async function handleDeleteAdmin(adminId: number) {
    const response = await apiFetch(`/admins/${adminId}`, { method: 'DELETE' })
    if (response.ok) {
      await loadAdmins()
      setErrorMessage('')
    } else {
      const data = await response.json()
      setErrorMessage(typeof data.detail === 'string' ? data.detail : 'Не удалось удалить админа')
    }
  }

  function startEditing(admin: AdminItem) {
    setEditingId(admin.id)
    setEditTgAdminId(admin.tg_admin_id?.toString() ?? '')
    setEditUsername(admin.username ?? '')
  }

  async function handleSaveEdit(adminId: number) {
    const ok = await handleUpdateAdmin(adminId, {
      tg_admin_id: editTgAdminId ? parseInt(editTgAdminId, 10) : null,
      username: editUsername || null,
    })
    if (ok) {
      setEditingId(null)
    }
  }

  return (
    <>
      <h1>Админы</h1>
      <div className={tableStyles.card}>
        <table className={tableStyles.table}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Логин</th>
              <th>Telegram ID</th>
              <th>Username</th>
              <th>Статус</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {admins.map((admin) => (
              <tr key={admin.id}>
                <td>{admin.id}</td>
                <td>{admin.login}</td>
                <td>
                  {editingId === admin.id ? (
                    <input
                      value={editTgAdminId}
                      onChange={(e) => setEditTgAdminId(e.target.value)}
                      placeholder="Telegram ID"
                    />
                  ) : (
                    admin.tg_admin_id ?? 'не привязан'
                  )}
                </td>
                <td>
                  {editingId === admin.id ? (
                    <input
                      value={editUsername}
                      onChange={(e) => setEditUsername(e.target.value)}
                      placeholder="Username"
                    />
                  ) : admin.username ? (
                    `@${admin.username}`
                  ) : (
                    'не указан'
                  )}
                </td>
                <td>{admin.is_active ? 'активен' : 'не активен'}</td>
                <td>
                  {editingId === admin.id ? (
                    <>
                      <button className="primary" onClick={() => handleSaveEdit(admin.id)}>
                        Сохранить
                      </button>
                      <button onClick={() => setEditingId(null)}>Отмена</button>
                    </>
                  ) : (
                    <>
                      <button onClick={() => startEditing(admin)}>Изменить Telegram</button>
                      <button
                        className={admin.is_active ? 'danger' : 'primary'}
                        onClick={() => handleUpdateAdmin(admin.id, { is_active: !admin.is_active })}
                      >
                        {admin.is_active ? 'Заблокировать' : 'Разблокировать'}
                      </button>
                      <button className="danger" onClick={() => handleDeleteAdmin(admin.id)}>
                        Удалить
                      </button>
                    </>
                  )}
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

      <div className={styles.section}>
        <h2>Добавить админа</h2>
        <div className={styles.form}>
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
          <input
            value={tgAdminId}
            onChange={(e) => setTgAdminId(e.target.value)}
            placeholder="Telegram ID (необязательно)"
          />
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Username (необязательно)"
          />
          <button className="primary" onClick={handleCreateAdmin}>
            Создать
          </button>
        </div>
        {errorMessage && <p className={styles.error}>{errorMessage}</p>}
      </div>
    </>
  )
}

export default AdminsPage
