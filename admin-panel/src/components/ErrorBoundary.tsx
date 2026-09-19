import { Component, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
}

class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error: unknown, info: { componentStack: string }) {
    console.error('Необработанная ошибка в приложении:', error, info.componentStack)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 12,
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
          }}
        >
          <p>Что-то пошло не так.</p>
          <button className="primary" onClick={() => window.location.reload()}>
            Обновить страницу
          </button>
        </div>
      )
    }
    return this.props.children
  }
}

export default ErrorBoundary
