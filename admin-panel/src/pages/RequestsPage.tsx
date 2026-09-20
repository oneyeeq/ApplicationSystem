import { useEffect, useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { useApiFetch } from '../api/useApiFetch'
import tableStyles from '../components/Table.module.css'

const STATUS = {
  NEW: 'новая',
  IN_PROGRESS: 'в_процессе',
  COMPLETED: 'завершена',
  REJECTED: 'отклонена',
} as const

interface RequestItem {
  id: number
  service_name: string
  phone_number: string
  user_id: number
  status: string
  created_at: string
  updated_at: string
}

interface PaginatedRequests {
  items: RequestItem[]
  total: number
  page: number
  page_size: number
}

const PAGE_SIZE = 10

function RequestsPage() {
  const [requests, setRequests] = useState<RequestItem[]>([])
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const { token } = useAuth()
  const apiFetch = useApiFetch()

  async function loadRequests() {
    const response = await apiFetch(`/requests/paginated?page=${page}&page_size=${PAGE_SIZE}`)
    const data: PaginatedRequests = await response.json()
    if (response.ok) {
      setRequests(data.items)
      setTotal(data.total)
    }
  }

  useEffect(() => {
    loadRequests()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, page])

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  async function handleStatusChange(requestId: number, newStatus: string) {
    const response = await apiFetch(`/requests/${requestId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus }),
    })
    const data = await response.json()
    if (response.ok) {
      setRequests(requests.map((r) => (r.id === requestId ? data : r)))
    }
  }

  async function handleDeleteRequest(requestId: number) {
    const response = await apiFetch(`/requests/${requestId}`, { method: 'DELETE' })
    if (response.ok) {
      await loadRequests()
    }
  }

  return (
    <>
      <h1>Заявки</h1>
      <div className={tableStyles.card}>
        <table className={tableStyles.table}>
          <thead>
            <tr>
              <th>ID</th>
              <th>ID пользователя</th>
              <th>Услуга</th>
              <th>Телефон</th>
              <th>Статус</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {requests.map((request) => (
              <tr key={request.id}>
                <td>{request.id}</td>
                <td>{request.user_id}</td>
                <td>{request.service_name}</td>
                <td>{request.phone_number}</td>
                <td>{request.status}</td>
                <td>
                  {request.status === STATUS.NEW && (
                    <>
                      <button
                        className="primary"
                        onClick={() => handleStatusChange(request.id, STATUS.IN_PROGRESS)}
                      >
                        В работу
                      </button>
                      <button
                        className="danger"
                        onClick={() => handleStatusChange(request.id, STATUS.REJECTED)}
                      >
                        Отклонить
                      </button>
                    </>
                  )}
                  {request.status === STATUS.IN_PROGRESS && (
                    <>
                      <button
                        className="primary"
                        onClick={() => handleStatusChange(request.id, STATUS.COMPLETED)}
                      >
                        Завершить
                      </button>
                      <button
                        className="danger"
                        onClick={() => handleStatusChange(request.id, STATUS.REJECTED)}
                      >
                        Отклонить
                      </button>
                    </>
                  )}
                  <button className="danger" onClick={() => handleDeleteRequest(request.id)}>
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
    </>
  )
}

export default RequestsPage
