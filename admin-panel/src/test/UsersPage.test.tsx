import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { it, expect, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '../auth/AuthContext'
import UsersPage from '../pages/UsersPage'

function paginatedUsers(items: unknown[], total = items.length): Response {
  return {
    ok: true,
    json: async () => ({ items, total, page: 1, page_size: 10 }),
  } as Response
}

function renderPage() {
  return render(
    <AuthProvider>
      <MemoryRouter>
        <UsersPage />
      </MemoryRouter>
    </AuthProvider>
  )
}

it('отображает список пользователей', async () => {
  globalThis.fetch = vi.fn().mockResolvedValueOnce(
    paginatedUsers([{ id: 1, tg_user_id: 111, username: 'ivan', is_active: true, active_requests: 2 }])
  )

  renderPage()

  expect(await screen.findByText('ivan')).toBeInTheDocument()
  expect(screen.getByText('111')).toBeInTheDocument()
  expect(screen.getByText('2')).toBeInTheDocument()
  expect(screen.getByText('активен')).toBeInTheDocument()
})

it('кнопка «Заблокировать» меняет статус пользователя', async () => {
  globalThis.fetch = vi
    .fn()
    .mockResolvedValueOnce(
      paginatedUsers([{ id: 1, tg_user_id: 111, username: 'ivan', is_active: true, active_requests: 0 }])
    )
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 1, tg_user_id: 111, username: 'ivan', is_active: false, active_requests: 0 }),
    } as Response)

  renderPage()
  await screen.findByText('ivan')

  const user = userEvent.setup()
  await user.click(screen.getByRole('button', { name: 'Заблокировать' }))

  expect(screen.getByText('заблокирован')).toBeInTheDocument()
  expect(screen.getByRole('button', { name: 'Разблокировать' })).toBeInTheDocument()
})

it('неудачное удаление пользователя показывает сообщение об ошибке', async () => {
  globalThis.fetch = vi
    .fn()
    .mockResolvedValueOnce(
      paginatedUsers([{ id: 1, tg_user_id: 111, username: 'ivan', is_active: true, active_requests: 3 }])
    )
    .mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'У пользователя есть активные заявки' }),
    } as Response)

  renderPage()
  await screen.findByText('ivan')

  const user = userEvent.setup()
  await user.click(screen.getByRole('button', { name: 'Удалить' }))

  expect(await screen.findByText('У пользователя есть активные заявки')).toBeInTheDocument()
  expect(screen.getByText('ivan')).toBeInTheDocument()
})

it('кнопка «Вперёд» переключает страницу и делает новый запрос', async () => {
  globalThis.fetch = vi
    .fn()
    .mockResolvedValueOnce(
      paginatedUsers([{ id: 1, tg_user_id: 111, username: 'ivan', is_active: true, active_requests: 0 }], 15)
    )
    .mockResolvedValueOnce(
      paginatedUsers([{ id: 11, tg_user_id: 999, username: 'petr', is_active: true, active_requests: 0 }], 15)
    )

  renderPage()
  await screen.findByText('ivan')
  expect(screen.getByRole('button', { name: '← Назад' })).toBeDisabled()

  const user = userEvent.setup()
  await user.click(screen.getByRole('button', { name: 'Вперёд →' }))

  expect(await screen.findByText('petr')).toBeInTheDocument()
  expect(screen.getByText('Стр. 2 из 2')).toBeInTheDocument()
})
