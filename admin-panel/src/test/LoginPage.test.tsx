import { render, screen } from '@testing-library/react'
import {userEvent} from '@testing-library/user-event'
import { it, expect } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '../auth/AuthContext'
import LoginPage from '../pages/LoginPage'
import { vi } from 'vitest'

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
it('печать в поле логина обновляет его значение', async () =>{
    render(<AuthProvider>
            <MemoryRouter>
                <LoginPage />
            </MemoryRouter>
        </AuthProvider>)

    const user = userEvent.setup()
    const loginInput = screen.getByLabelText('Логин')
    await user.type(loginInput, 'admin')
    expect(loginInput).toHaveValue("admin")
})


it('неудачный логин не прошёл', async () =>{
    globalThis.fetch = vi.fn().mockResolvedValue({
        ok: false,
        json: async () => ({ detail: 'Неверный логин или пароль' }),
    } as Response)
    render(<AuthProvider>
            <MemoryRouter>
                <LoginPage />
            </MemoryRouter>
        </AuthProvider>)
    const user = userEvent.setup()
    const loginInput = screen.getByLabelText('Логин')
    await user.type(loginInput, 'burmaldan')
    const button = screen.getByRole('button', {name : 'Войти'})
    await user.click(button)
    expect(screen.getByText('Неверный логин или пароль')).toBeInTheDocument()
})

it('успешный логин не показывает ошибку', async () =>{
    globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ access_token: 'fake-token' }),
    } as Response)
    render(<AuthProvider>
            <MemoryRouter>
                <LoginPage />
            </MemoryRouter>
        </AuthProvider>)
    const user = userEvent.setup()
    const loginInput = screen.getByLabelText('Логин')
    const passwordInput = screen.getByLabelText('Пароль')
    await user.type(loginInput, 'burmaldan')
    await user.type(passwordInput, 'burmaldan')
    const button = screen.getByRole('button', {name : 'Войти'})
    await user.click(button)
    expect(screen.queryByText('Неверный логин или пароль')).not.toBeInTheDocument()
})