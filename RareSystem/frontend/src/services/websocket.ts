import type { WSMessage, WSResponse } from '@/types'

type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error'

export class ChatWebSocket {
  private ws: WebSocket | null = null
  private patientId: number
  private reconnectAttempts = 0
  private maxReconnectAttempts = 10
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private messageBuffer: WSMessage[] = []
  private messageCallback: ((data: WSResponse) => void) | null = null
  private errorCallback: ((error: Event) => void) | null = null
  private closeCallback: ((event: CloseEvent) => void) | null = null
  private _state: ConnectionState = 'disconnected'

  constructor(patientId: number) {
    this.patientId = patientId
  }

  get isConnected(): boolean {
    return this._state === 'connected'
  }

  get state(): ConnectionState {
    return this._state
  }

  connect(): void {
    if (this.ws && (this._state === 'connected' || this._state === 'connecting')) {
      return
    }

    if (this.ws) {
      try { this.ws.close() } catch { }
      this.ws = null
    }

    this._state = 'connecting'
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const url = `${protocol}//${host}/api/chat/ws/${this.patientId}`

    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      this._state = 'connected'
      this.reconnectAttempts = 0
      this.flushBuffer()
    }

    this.ws.onmessage = (event: MessageEvent) => {
      try {
        const data: WSResponse = JSON.parse(event.data)
        this.messageCallback?.(data)
      } catch {
        // skip malformed
      }
    }

    this.ws.onerror = (event: Event) => {
      this._state = 'error'
      this.errorCallback?.(event)
    }

    this.ws.onclose = (event: CloseEvent) => {
      this._state = 'disconnected'
      this.closeCallback?.(event)
      this.attemptReconnect()
    }
  }

  send(message: WSMessage): void {
    if (this.isConnected && this.ws) {
      this.ws.send(JSON.stringify(message))
    } else {
      this.messageBuffer.push(message)
      if (this._state === 'disconnected') {
        this.connect()
      }
    }
  }

  onMessage(callback: (data: WSResponse) => void): void {
    this.messageCallback = callback
  }

  onError(callback: (error: Event) => void): void {
    this.errorCallback = callback
  }

  onClose(callback: (event: CloseEvent) => void): void {
    this.closeCallback = callback
  }

  close(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    this.reconnectAttempts = this.maxReconnectAttempts
    this._state = 'disconnected'
    if (this.ws) {
      try {
        this.ws.close()
      } catch {
        // Ignore close errors during cleanup
      }
    }
    this.ws = null
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) return

    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000)
    this.reconnectAttempts++

    this.reconnectTimer = setTimeout(() => {
      this.connect()
    }, delay)
  }

  private flushBuffer(): void {
    while (this.messageBuffer.length > 0 && this.isConnected) {
      const msg = this.messageBuffer.shift()!
      this.send(msg)
    }
  }
}

class WebSocketManager {
  private static instance: WebSocketManager | null = null
  private ws: ChatWebSocket | null = null
  private patientId: number | null = null
  private listeners: Set<(data: WSResponse) => void> = new Set()
  private errorListeners: Set<(error: Event) => void> = new Set()
  private refCount = 0

  static getInstance(): WebSocketManager {
    if (!WebSocketManager.instance) {
      WebSocketManager.instance = new WebSocketManager()
    }
    return WebSocketManager.instance
  }

  connect(patientId: number): void {
    if (this.ws && this.patientId === patientId) {
      return
    }

    if (this.ws) {
      this.ws.close()
    }

    this.patientId = patientId
    this.ws = new ChatWebSocket(patientId)
    this.ws.onMessage((data) => {
      this.listeners.forEach(cb => cb(data))
    })
    this.ws.onError((error) => {
      this.errorListeners.forEach(cb => cb(error))
    })
    this.ws.connect()
  }

  subscribe(onMessage: (data: WSResponse) => void, onError: (error: Event) => void): () => void {
    this.listeners.add(onMessage)
    this.errorListeners.add(onError)
    this.refCount++

    return () => {
      this.listeners.delete(onMessage)
      this.errorListeners.delete(onError)
      this.refCount--
      if (this.refCount <= 0) {
        this.refCount = 0
      }
    }
  }

  send(message: WSMessage): void {
    if (this.ws && this.ws.isConnected) {
      this.ws.send(message)
    }
  }

  isConnected(): boolean {
    return this.ws?.isConnected ?? false
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
      this.patientId = null
    }
  }
}

export const wsManager = WebSocketManager.getInstance()
