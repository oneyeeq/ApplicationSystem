import { Routes, Route } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import RequestsPage from './pages/RequestsPage'
import AdminsPage from './pages/AdminsPage'
import UsersPage from './pages/UsersPage'
import { useEffect, useState } from 'react'
import { useAuth } from './auth/AuthContext'
import ProtectedRoute from './auth/ProtectedRoute'
import Layout from './components/Layout'


function App() {
  const [isCheckingAuth, setIsCheckingAuth] = useState(true)
  const { setToken } = useAuth()
  useEffect(() => {
  async function restoreSession() {
    try {
      const response = await fetch("http://localhost:8000/auth/refresh/", {
        method: "POST",
        credentials: "include",
      })
      if (response.ok) {
        const data = await response.json()
        setToken(data.access_token)
      }
    } finally {
      setIsCheckingAuth(false)
    }
  }
  restoreSession()
}, [])
  if (isCheckingAuth) {
  return <p>Загрузка...</p>
  }
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route path="/requests" element={<RequestsPage />} />
        <Route path="/admins" element={<AdminsPage />} />
        <Route path="/users" element={<UsersPage />} />
      </Route>
    </Routes>

  )
}

export default App
