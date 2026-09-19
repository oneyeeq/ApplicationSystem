import { useEffect, useState } from 'react'
import { useAuth } from '../auth/AuthContext'

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

  useEffect(() => {
    async function loadRequests() {
      const response = await fetch('http://localhost:8000/requests/', {
        headers: { Authorization: `Bearer ${token}` },
        credentials: 'include',
      })
      const data = await response.json()
      if (response.ok) {
        setRequests(data)
      }
    }
    loadRequests()
  }, [token])

  async function handleStatusChange(requestId: number, newStatus: string) {
    const response = await fetch(`http://localhost:8000/requests/${requestId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      credentials: 'include',
      body: JSON.stringify({ status: newStatus }),
    })
    const data = await response.json()
    if (response.ok) {
      setRequests(requests.map((r) => (r.id === requestId ? data : r)))
    }
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Услуга</th>
          <th>Телефон</th>
          <th>Статус</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        {requests.map((request) => (
          <tr key={request.id}>
            <td>{request.service_name}</td>
            <td>{request.phone_number}</td>
            <td>{request.status}</td>
            <td>
              {request.status === STATUS.NEW && (
                <>
                  <button onClick={() => handleStatusChange(request.id, STATUS.IN_PROGRESS)}>
                    В работу
                  </button>{' '}
                  <button onClick={() => handleStatusChange(request.id, STATUS.REJECTED)}>
                    Отклонить
                  </button>
                </>
              )}
              {request.status === STATUS.IN_PROGRESS && (
                <>
                  <button onClick={() => handleStatusChange(request.id, STATUS.COMPLETED)}>
                    Завершить
                  </button>{' '}
                  <button onClick={() => handleStatusChange(request.id, STATUS.REJECTED)}>
                    Отклонить
                  </button>
                </>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default RequestsPage
