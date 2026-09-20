import { render, screen } from '@testing-library/react'
import { it, expect } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '../auth/AuthContext'
import LoginPage from '../pages/LoginPage'

it('рендерит поля логина и пароля', () => {
    render(<AuthProvider>
            <MemoryRouter>
                <LoginPage />
            </MemoryRouter>
        </AuthProvider>)
    const loginInput = screen.getByLabelText('Логин')
    const passwordInput = screen.getByLabelText('Пароль')
    expect(loginInput).toBeInTheDocument()
    expect(passwordInput).toBeInTheDocument()
})