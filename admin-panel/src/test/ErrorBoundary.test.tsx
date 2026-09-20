import { render, screen } from '@testing-library/react'
import { it, expect} from 'vitest'
import ErrorBoundary from '../components/ErrorBoundary'

function ThrowingComponent(): never {
    throw new Error('тестовая ошибка')
}

it('показывает запасной экран, если дочерний компонент упал', () => {
    render(
        <ErrorBoundary>
            <ThrowingComponent/>
        </ErrorBoundary>
    )
    expect(screen.getByText('Что-то пошло не так.')).toBeInTheDocument()
})
