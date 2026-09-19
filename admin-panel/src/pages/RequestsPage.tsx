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

function RequestsPage() {
  const [requests, setRequests] = useState<RequestItem[]>([])
  const { token } = useAuth()
  const apiFetch = useApiFetch()

  useEffect(() => {
    async function loadRequests() {
      const response = await apiFetch('/requests/')
      const data = await response.json()
      if (response.ok) {
        setRequests(data)
      }
    }
    loadRequests()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

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
      setRequests(requests.filter((r) => r.id !== requestId))
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
    </>
  )
}

export default RequestsPage
