import { Navigate } from 'react-router-dom'
import { useAuth } from './AuthContext'
import type { ReactNode } from 'react'

function ProtectedRoute({ children }: { children: ReactNode }) {
  const { token } = useAuth()
  if (!token) {
    return <Navigate to="/login" />
  }
  return children
}

export default ProtectedRoute
