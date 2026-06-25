import React, { Component, ErrorInfo, ReactNode } from 'react'
import { Result, Button, Typography, Space, Collapse } from 'antd'
import { BugOutlined, ReloadOutlined, HomeOutlined } from '@ant-design/icons'

const { Paragraph, Text } = Typography
const { Panel } = Collapse

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
  showDetails?: boolean
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
  errorId: string | null
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
    }
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
      errorId: `error-${Date.now()}`,
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({ errorInfo })

    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }

    console.error('ErrorBoundary caught an error:', error, errorInfo)
  }

  handleReload = (): void => {
    window.location.reload()
  }

  handleGoHome = (): void => {
    window.location.href = '/'
  }

  handleCopyError = (): void => {
    const { error, errorInfo } = this.state
    if (!error) return

    const errorDetails = [
      `Error ID: ${this.state.errorId}`,
      `Time: ${new Date().toISOString()}`,
      `Message: ${error.message}`,
      `Stack: ${error.stack}`,
      errorInfo ? `Component Stack: ${errorInfo.componentStack}` : '',
    ]
      .filter(Boolean)
      .join('<br><br>')

    navigator.clipboard.writeText(errorDetails).catch(console.error)
  }

  render(): ReactNode {
    const { hasError, error, errorInfo, errorId } = this.state
    const { children, fallback, showDetails = true } = this.props

    if (hasError) {
      if (fallback) {
        return fallback
      }

      return (
        <div
          style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '24px',
            background: '#f5f5f5',
          }}
        >
          <Result
            status="error"
            icon={<BugOutlined style={{ color: '#ff4d4f' }} />}
            title="Something went wrong"
            subTitle={
              <Space direction="vertical" size="small">
                <Text>We apologize for the inconvenience. An unexpected error has occurred.</Text>
                {errorId && (
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    Error ID: {errorId}
                  </Text>
                )}
              </Space>
            }
            extra={[
              <Button
                key="reload"
                type="primary"
                icon={<ReloadOutlined />}
                onClick={this.handleReload}
              >
                Reload Page
              </Button>,
              <Button
                key="home"
                icon={<HomeOutlined />}
                onClick={this.handleGoHome}
              >
                Go to Home
              </Button>,
            ]}
          >
            {showDetails && error && (
              <div style={{ textAlign: 'left', maxWidth: '600px', margin: '0 auto' }}>
                <Collapse ghost>
                  <Panel header="View error details" key="1">
                    <Paragraph>
                      <Text strong>Error Message:</Text>
                      <br />
                      <Text code>{error.message}</Text>
                    </Paragraph>

                    {error.stack && (
                      <Paragraph>
                        <Text strong>Stack Trace:</Text>
                        <br />
                        <Text
                          code
                          style={{
                            display: 'block',
                            maxWidth: '100%',
                            overflow: 'auto',
                            whiteSpace: 'pre-wrap',
                            wordBreak: 'break-word',
                            maxHeight: '200px',
                            fontSize: '11px',
                          }}
                        >
                          {error.stack}
                        </Text>
                      </Paragraph>
                    )}

                    {errorInfo?.componentStack && (
                      <Paragraph>
                        <Text strong>Component Stack:</Text>
                        <br />
                        <Text
                          code
                          style={{
                            display: 'block',
                            maxWidth: '100%',
                            overflow: 'auto',
                            whiteSpace: 'pre-wrap',
                            wordBreak: 'break-word',
                            maxHeight: '200px',
                            fontSize: '11px',
                          }}
                        >
                          {errorInfo.componentStack}
                        </Text>
                      </Paragraph>
                    )}

                    <Button size="small" onClick={this.handleCopyError}>
                      Copy Error Details
                    </Button>
                  </Panel>
                </Collapse>
              </div>
            )}
          </Result>
        </div>
      )
    }

    return children
  }
}

export default ErrorBoundary

export function withErrorBoundary<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  errorBoundaryProps?: Omit<Props, 'children'>
): React.FC<P> {
  const displayName = WrappedComponent.displayName || WrappedComponent.name || 'Component'

  const ComponentWithErrorBoundary: React.FC<P> = (props) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <WrappedComponent {...props} />
    </ErrorBoundary>
  )

  ComponentWithErrorBoundary.displayName = `withErrorBoundary(${displayName})`

  return ComponentWithErrorBoundary
}

export function useErrorBoundary(): {
  ErrorBoundary: typeof ErrorBoundary
  withErrorBoundary: typeof withErrorBoundary
} {
  return { ErrorBoundary, withErrorBoundary }
}
