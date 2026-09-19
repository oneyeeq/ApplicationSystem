import { useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { useNavigate } from 'react-router-dom'

function LoginPage() {
    const [login, setLogin] = useState("")
    const [password, setPassword] = useState("")
    const { setToken } = useAuth()
    const navigate = useNavigate()
    const [errorMessage, setErrorMessage] = useState("")

    async function handleLogin() {
        const response = await fetch("http://localhost:8000/auth/login/", 
        {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ login, password }),
        })
        const data = await response.json()
        if (response.ok) {
            setToken(data.access_token)
            navigate('/requests')
        } 
        else {
            setErrorMessage(typeof data.detail === "string" ? data.detail : "Некорректные данные")
        }
    }
    return (
        <div>
            <h1>
                Вход
            </h1>
            <input
                value={login} onChange={(e) => setLogin(e.target.value)} 
            />
            <input 
                value={password} type="password" onChange={(e) => setPassword(e.target.value)}
            />
            <button onClick={handleLogin}>
                Войти
            </button>
            <p>
                {errorMessage}
            </p>
        </div>
    )
}

export default LoginPage
