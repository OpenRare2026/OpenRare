import { useCallback, useEffect } from 'react'
import { message, notification } from 'antd'
import type { MessageInstance } from 'antd/es/message/interface'
import type { NotificationInstance } from 'antd/es/notification/interface'
import type { ArgsProps as NotificationArgsProps } from 'antd/es/notification'

import {
  APIError,
  NetworkError,
  TimeoutError,
  ValidationError,
  AuthenticationError,
  NotFoundError,
  ServerError,
} from '@/services/api'

interface ToastOptions {
  duration?: number
  key?: string
  onClose?: () => void
}

interface ErrorToastOptions extends ToastOptions {
  showDetails?: boolean
  onRetry?: () => void
}

let messageApi: MessageInstance
let notificationApi: NotificationInstance

export function useToast() {
  const [messageInstance, messageContextHolder] = message.useMessage()
  const [notificationInstance, notificationContextHolder] = notification.useNotification()

  useEffect(() => {
    messageApi = messageInstance
    notificationApi = notificationInstance
  }, [messageInstance, notificationInstance])

  const success = useCallback((content: string, options?: ToastOptions) => {
    messageInstance.success({
      content,
      duration: options?.duration ?? 3,
      key: options?.key,
      onClose: options?.onClose,
    })
  }, [messageInstance])

  const info = useCallback((content: string, options?: ToastOptions) => {
    messageInstance.info({
      content,
      duration: options?.duration ?? 3,
      key: options?.key,
      onClose: options?.onClose,
    })
  }, [messageInstance])

  const warning = useCallback((content: string, options?: ToastOptions) => {
    messageInstance.warning({
      content,
      duration: options?.duration ?? 4,
      key: options?.key,
      onClose: options?.onClose,
    })
  }, [messageInstance])

  const error = useCallback((content: string, options?: ToastOptions) => {
    messageInstance.error({
      content,
      duration: options?.duration ?? 5,
      key: options?.key,
      onClose: options?.onClose,
    })
  }, [messageInstance])

  const loading = useCallback((content: string, options?: ToastOptions) => {
    messageInstance.loading({
      content,
      duration: options?.duration ?? 0,
      key: options?.key,
      onClose: options?.onClose,
    })
  }, [messageInstance])

  const dismiss = useCallback((key?: string) => {
    if (key) {
      messageInstance.destroy(key)
    } else {
      messageInstance.destroy()
    }
  }, [messageInstance])

  const notify = useCallback((
    type: 'success' | 'info' | 'warning' | 'error',
    title: string,
    description?: string,
    options?: NotificationArgsProps
  ) => {
    notificationInstance[type]({
      message: title,
      description,
      placement: 'topRight',
      duration: 4.5,
      ...options,
    })
  }, [notificationInstance])

  const apiError = useCallback((err: Error, options?: ErrorToastOptions) => {
    let title = 'Error'
    let description = err.message

    if (err instanceof NetworkError) {
      title = 'Network Error'
      description = 'Unable to connect to the server. Please check your internet connection.'
    } else if (err instanceof TimeoutError) {
      title = 'Request Timeout'
      description = 'The request took too long to complete. Please try again.'
    } else if (err instanceof ValidationError) {
      title = 'Validation Error'
      description = err.message
      if (err.details && options?.showDetails !== false) {
        const fieldErrors = Object.entries(err.details as Record<string, string[]>)
          .map(([field, msgs]) => `${field}: ${msgs.join(', ')}`)
          .join('<br>')
        description = fieldErrors
      }
    } else if (err instanceof AuthenticationError) {
      title = 'Authentication Required'
      description = 'Please log in to continue.'
    } else if (err instanceof NotFoundError) {
      title = 'Not Found'
      description = 'The requested resource was not found.'
    } else if (err instanceof ServerError) {
      title = 'Server Error'
      description = 'A server error occurred. Please try again later.'
    } else if (err instanceof APIError) {
      title = 'Error'
      description = err.message
    }

    notificationInstance.error({
      message: title,
      description,
      placement: 'topRight',
      duration: 6,
    })
  }, [notificationInstance])

  const apiSuccess = useCallback((
    title: string,
    description?: string
  ) => {
    notificationInstance.success({
      message: title,
      description,
      placement: 'topRight',
      duration: 4,
    })
  }, [notificationInstance])

  const apiWarning = useCallback((
    title: string,
    description?: string
  ) => {
    notificationInstance.warning({
      message: title,
      description,
      placement: 'topRight',
      duration: 5,
    })
  }, [notificationInstance])

  const confirm = useCallback((
    title: string,
    description: string,
    onConfirm: () => void,
    onCancel?: () => void
  ) => {
    notificationInstance.warning({
      message: title,
      description,
      placement: 'topRight',
      duration: 0,
      btn: (
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => {
              notificationInstance.destroy()
              onConfirm()
            }}
            style={{
              padding: '4px 12px',
              background: '#1890ff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Confirm
          </button>
          <button
            onClick={() => {
              notificationInstance.destroy()
              onCancel?.()
            }}
            style={{
              padding: '4px 12px',
              background: '#f0f0f0',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Cancel
          </button>
        </div>
      ),
    })
  }, [notificationInstance])

  return {
    success,
    info,
    warning,
    error,
    loading,
    dismiss,
    notify,
    apiError,
    apiSuccess,
    apiWarning,
    confirm,
    messageContextHolder,
    notificationContextHolder,
  }
}

export type ToastFunction = ReturnType<typeof useToast>

export function showErrorToast(error: Error): void {
  if (!notificationApi) {
    console.error('Toast not initialized:', error)
    return
  }

  const toast = useToast()
  toast.apiError(error)
}

export function showSuccessToast(message: string, description?: string): void {
  if (!notificationApi) {
    console.log('Success:', message, description)
    return
  }

  notificationApi.success({
    message,
    description,
    placement: 'topRight',
    duration: 4,
  })
}

export function showWarningToast(message: string, description?: string): void {
  if (!notificationApi) {
    console.warn('Warning:', message, description)
    return
  }

  notificationApi.warning({
    message,
    description,
    placement: 'topRight',
    duration: 5,
  })
}

export function showInfoToast(message: string, duration: number = 3): void {
  if (!messageApi) {
    console.info('Info:', message)
    return
  }

  messageApi.info(message, duration)
}

export function showLoadingToast(message: string, key?: string): string {
  const loadingKey = key || `loading-${Date.now()}`
  
  if (!messageApi) {
    console.log('Loading:', message)
    return loadingKey
  }

  messageApi.loading({
    content: message,
    key: loadingKey,
    duration: 0,
  })

  return loadingKey
}

export function hideLoadingToast(key?: string): void {
  if (!messageApi) {
    return
  }

  if (key) {
    messageApi.destroy(key)
  } else {
    messageApi.destroy()
  }
}

export { messageApi, notificationApi }
