import { renderHook } from "@testing-library/react";
import { it, expect, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '../auth/AuthContext'
import { useApiFetch } from "../api/useApiFetch";

function wrapper({ children }: { children: React.ReactNode }) {
    return <AuthProvider><MemoryRouter>{children}</MemoryRouter></AuthProvider>
}

it('обычный запрос без 401 отправляется один раз', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({ status: 200, ok: true } as Response)
    const { result } = renderHook(() => useApiFetch(), { wrapper })
    const response = await result.current('/requests/')
    expect(response.status).toBe(200)
    expect(fetch).toHaveBeenCalledTimes(1)
})
it('после ошибки 401 обновляется токен и повторяется запрос', async () => {
    globalThis.fetch = vi.fn()
    .mockResolvedValueOnce({ status: 401 } as Response)
    .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ access_token: 'new-token' }),
    } as Response)
    .mockResolvedValueOnce({ status: 200, ok: true } as Response)
    const { result } = renderHook(() => useApiFetch(), { wrapper })
    const response = await result.current('/requests/')
    expect(response.status).toBe(200)
    expect(fetch).toHaveBeenCalledTimes(3)
})
it('после ошибки 401 обновления токена не удалось', async () => {
    globalThis.fetch = vi.fn()
    .mockResolvedValueOnce({ status: 401 } as Response)
    .mockResolvedValueOnce({ok: false } as Response)
    const { result } = renderHook(() => useApiFetch(), { wrapper })
    const response = await result.current('/requests/')
    expect(response.status).toBe(401)
    expect(fetch).toHaveBeenCalledTimes(2)
})
