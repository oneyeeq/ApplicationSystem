import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export const API_BASE = 'http://localhost:8000'

export function useApiFetch() {
  const { token, setToken } = useAuth()
  const navigate = useNavigate()

  async function requestWith(path: string, options: RequestInit, accessToken: string | null) {
    return fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${accessToken}`,
      },
      credentials: 'include',
    })
  }

  return async function apiFetch(path: string, options: RequestInit = {}): Promise<Response> {
    const response = await requestWith(path, options, token)
    if (response.status !== 401) {
      return response
    }

    const refreshResponse = await fetch(`${API_BASE}/auth/refresh/`, {
      method: 'POST',
      credentials: 'include',
    })

    if (!refreshResponse.ok) {
      setToken(null)
      navigate('/login')
      return response
    }

    const refreshData = await refreshResponse.json()
    setToken(refreshData.access_token)
    return requestWith(path, options, refreshData.access_token)
  }
}
