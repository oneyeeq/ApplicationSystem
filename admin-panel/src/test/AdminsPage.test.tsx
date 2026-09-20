import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { it, expect, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '../auth/AuthContext'
import AdminsPage from '../pages/AdminsPage'

function paginatedAdmins(items: unknown[], total = items.length): Response {
  return {
    ok: true,
    json: async () => ({ items, total, page: 1, page_size: 10 }),
  } as Response
}

function renderPage() {
  return render(
    <AuthProvider>
      <MemoryRouter>
        <AdminsPage />
      </MemoryRouter>
    </AuthProvider>
  )
}

it('отображает список админов', async () => {
  globalThis.fetch = vi.fn().mockResolvedValueOnce(
    paginatedAdmins([{ id: 1, login: 'admin1', tg_admin_id: 123, username: 'nick', is_active: true }])
  )

  renderPage()

  expect(await screen.findByText('admin1')).toBeInTheDocument()
  expect(screen.getByText('123')).toBeInTheDocument()
  expect(screen.getByText('@nick')).toBeInTheDocument()
  expect(screen.getByText('активен')).toBeInTheDocument()
})

it('создание админа отправляет данные формы и добавляет его в список', async () => {
  globalThis.fetch = vi
    .fn()
    .mockResolvedValueOnce(paginatedAdmins([]))
    .mockResolvedValueOnce({ ok: true, json: async () => ({ id: 2, login: 'newadmin' }) } as Response)
    .mockResolvedValueOnce(
      paginatedAdmins([{ id: 2, login: 'newadmin', tg_admin_id: null, username: null, is_active: true }])
    )

  renderPage()

  const user = userEvent.setup()
  await user.type(screen.getByPlaceholderText('Логин'), 'newadmin')
  await user.type(screen.getByPlaceholderText('Пароль'), 'secret123')
  await user.click(screen.getByRole('button', { name: 'Создать' }))

  expect(await screen.findByText('newadmin')).toBeInTheDocument()
  expect(screen.getByPlaceholderText('Логин')).toHaveValue('')
  expect(fetch).toHaveBeenCalledTimes(3)
})

it('ошибка при создании админа показывает сообщение и не очищает поля', async () => {
  globalThis.fetch = vi
    .fn()
    .mockResolvedValueOnce(paginatedAdmins([]))
    .mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Такой логин уже занят' }),
    } as Response)

  renderPage()

  const user = userEvent.setup()
  await user.type(screen.getByPlaceholderText('Логин'), 'admin1')
  await user.type(screen.getByPlaceholderText('Пароль'), 'secret123')
  await user.click(screen.getByRole('button', { name: 'Создать' }))

  expect(await screen.findByText('Такой логин уже занят')).toBeInTheDocument()
  expect(screen.getByPlaceholderText('Логин')).toHaveValue('admin1')
  expect(fetch).toHaveBeenCalledTimes(2)
})

it('редактирование Telegram-данных обновляет строку после сохранения', async () => {
  globalThis.fetch = vi
    .fn()
    .mockResolvedValueOnce(
      paginatedAdmins([{ id: 1, login: 'admin1', tg_admin_id: null, username: null, is_active: true }])
    )
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 1, login: 'admin1', tg_admin_id: 555, username: 'newnick', is_active: true }),
    } as Response)

  renderPage()
  await screen.findByText('admin1')

  const user = userEvent.setup()
  await user.click(screen.getByRole('button', { name: 'Изменить Telegram' }))
  await user.type(screen.getByPlaceholderText('Telegram ID'), '555')
  await user.type(screen.getByPlaceholderText('Username'), 'newnick')
  await user.click(screen.getByRole('button', { name: 'Сохранить' }))

  expect(await screen.findByText('555')).toBeInTheDocument()
  expect(screen.getByText('@newnick')).toBeInTheDocument()
  expect(screen.queryByRole('button', { name: 'Сохранить' })).not.toBeInTheDocument()
})

it('кнопка «Заблокировать» меняет статус админа', async () => {
  globalThis.fetch = vi
    .fn()
    .mockResolvedValueOnce(
      paginatedAdmins([{ id: 1, login: 'admin1', tg_admin_id: null, username: null, is_active: true }])
    )
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 1, login: 'admin1', tg_admin_id: null, username: null, is_active: false }),
    } as Response)

  renderPage()
  await screen.findByText('admin1')

  const user = userEvent.setup()
  await user.click(screen.getByRole('button', { name: 'Заблокировать' }))

  expect(screen.getByText('не активен')).toBeInTheDocument()
  expect(screen.getByRole('button', { name: 'Разблокировать' })).toBeInTheDocument()
})

it('неудачное удаление админа показывает сообщение об ошибке', async () => {
  globalThis.fetch = vi
    .fn()
    .mockResolvedValueOnce(
      paginatedAdmins([{ id: 1, login: 'admin1', tg_admin_id: null, username: null, is_active: true }])
    )
    .mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Нельзя удалить последнего админа' }),
    } as Response)

  renderPage()
  await screen.findByText('admin1')

  const user = userEvent.setup()
  await user.click(screen.getByRole('button', { name: 'Удалить' }))

  expect(await screen.findByText('Нельзя удалить последнего админа')).toBeInTheDocument()
  expect(screen.getByText('admin1')).toBeInTheDocument()
})
