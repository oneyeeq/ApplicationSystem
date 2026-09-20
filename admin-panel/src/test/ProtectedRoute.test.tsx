import { render, screen } from '@testing-library/react'
import { it, expect} from 'vitest'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider, AuthContext } from '../auth/AuthContext'
import ProtectedRoute from '../auth/ProtectedRoute'

it('без токена редиректит на /login', () => {
    render(<AuthProvider>
        <MemoryRouter initialEntries={['/protected']}>
            <Routes>
                <Route path="/login" element={<div>Login Page</div>} />
                <Route path="/protected" element={<ProtectedRoute><div>Secret Content</div></ProtectedRoute>} />
            </Routes>
        </MemoryRouter>
    </AuthProvider>)
    expect(screen.getByText('Login Page')).toBeInTheDocument()
    expect(screen.queryByText('Secret Content')).not.toBeInTheDocument()
})
it('с токеном показывает children', () => {
    render(<AuthContext.Provider value={{ token: 'fake-token', setToken: () => {} }}>
        <MemoryRouter initialEntries={['/protected']}>
            <Routes>
                <Route path="/login" element={<div>Login Page</div>} />
                <Route path="/protected" element={<ProtectedRoute><div>Secret Content</div></ProtectedRoute>} />
            </Routes>
        </MemoryRouter>
    </AuthContext.Provider>)
    expect(screen.getByText('Secret Content')).toBeInTheDocument()
    expect(screen.queryByText('Login Page')).not.toBeInTheDocument()
})

