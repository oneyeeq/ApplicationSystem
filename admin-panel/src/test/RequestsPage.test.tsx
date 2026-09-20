import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { it, expect, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '../auth/AuthContext'
import RequestsPage from '../pages/RequestsPage'

function paginatedResponse(items: unknown[], total = items.length): Response {
  return {
    ok: true,
    json: async () => ({ items, total, page: 1, page_size: 10 }),
  } as Response
}

function renderPage() {
  return render(
    <AuthProvider>
      <MemoryRouter>
        <RequestsPage />
      </MemoryRouter>
    </AuthProvider>
  )
}

it('отображает список заявок из API', async () => {
  globalThis.fetch = vi.fn().mockResolvedValueOnce(
    paginatedResponse([
      {
        id: 1,
        service_name: 'Установка кондиционера',
        phone_number: '+79990001122',
        user_id: 5,
        status: 'новая',
        created_at: '',
        updated_at: '',
      },
    ])
  )

  renderPage()

  expect(await screen.findByText('Установка кондиционера')).toBeInTheDocument()
  expect(screen.getByText('+79990001122')).toBeInTheDocument()
  expect(screen.getByText('новая')).toBeInTheDocument()
})

it('показывает кнопки действий в зависимости от статуса заявки', async () => {
  globalThis.fetch = vi.fn().mockResolvedValueOnce(
    paginatedResponse(
      [
        { id: 1, service_name: 'Новая заявка', phone_number: '1', user_id: 1, status: 'новая', created_at: '', updated_at: '' },
        { id: 2, service_name: 'В работе', phone_number: '2', user_id: 2, status: 'в_процессе', created_at: '', updated_at: '' },
        { id: 3, service_name: 'Завершённая', phone_number: '3', user_id: 3, status: 'завершена', created_at: '', updated_at: '' },
      ],
      3
    )
  )

  renderPage()
  await screen.findByText('Новая заявка')

  expect(screen.getByRole('button', { name: 'В работу' })).toBeInTheDocument()
  expect(screen.getByRole('button', { name: 'Завершить' })).toBeInTheDocument()
  expect(screen.getAllByRole('button', { name: 'Отклонить' })).toHaveLength(2)
  expect(screen.getAllByRole('button', { name: 'Удалить' })).toHaveLength(3)
})

it('кнопка «В работу» меняет статус заявки и обновляет строку', async () => {
  globalThis.fetch = vi
    .fn()
    .mockResolvedValueOnce(
      paginatedResponse([
        { id: 1, service_name: 'Новая заявка', phone_number: '1', user_id: 1, status: 'новая', created_at: '', updated_at: '' },
      ])
    )
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: 1,
        service_name: 'Новая заявка',
        phone_number: '1',
        user_id: 1,
        status: 'в_процессе',
        created_at: '',
        updated_at: '',
      }),
    } as Response)

  renderPage()
  await screen.findByText('Новая заявка')

  const user = userEvent.setup()
  await user.click(screen.getByRole('button', { name: 'В работу' }))

  expect(screen.getByText('в_процессе')).toBeInTheDocument()
  expect(screen.queryByText('новая')).not.toBeInTheDocument()
  expect(fetch).toHaveBeenCalledTimes(2)
})

it('кнопка «Удалить» удаляет заявку и перезагружает список', async () => {
  globalThis.fetch = vi
    .fn()
    .mockResolvedValueOnce(
      paginatedResponse([
        { id: 1, service_name: 'Заявка на удаление', phone_number: '1', user_id: 1, status: 'новая', created_at: '', updated_at: '' },
      ])
    )
    .mockResolvedValueOnce({ ok: true, json: async () => ({}) } as Response)
    .mockResolvedValueOnce(paginatedResponse([]))

  renderPage()
  await screen.findByText('Заявка на удаление')

  const user = userEvent.setup()
  await user.click(screen.getByRole('button', { name: 'Удалить' }))

  expect(screen.queryByText('Заявка на удаление')).not.toBeInTheDocument()
  expect(fetch).toHaveBeenCalledTimes(3)
})

it('кнопка «Вперёд» переключает страницу и делает новый запрос', async () => {
  globalThis.fetch = vi
    .fn()
    .mockResolvedValueOnce(
      paginatedResponse(
        [{ id: 1, service_name: 'Заявка 1', phone_number: '1', user_id: 1, status: 'новая', created_at: '', updated_at: '' }],
        15
      )
    )
    .mockResolvedValueOnce(
      paginatedResponse(
        [{ id: 11, service_name: 'Заявка 11', phone_number: '11', user_id: 11, status: 'новая', created_at: '', updated_at: '' }],
        15
      )
    )

  renderPage()
  await screen.findByText('Заявка 1')
  expect(screen.getByText('Стр. 1 из 2')).toBeInTheDocument()
  expect(screen.getByRole('button', { name: '← Назад' })).toBeDisabled()

  const user = userEvent.setup()
  await user.click(screen.getByRole('button', { name: 'Вперёд →' }))

  expect(await screen.findByText('Заявка 11')).toBeInTheDocument()
  expect(screen.getByText('Стр. 2 из 2')).toBeInTheDocument()
  expect(screen.getByRole('button', { name: 'Вперёд →' })).toBeDisabled()
})
