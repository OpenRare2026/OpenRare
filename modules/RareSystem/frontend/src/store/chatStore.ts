import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { StreamingChatMessage, Skill, WSResponse } from '@/types'
import { ChatWebSocket } from '@/services/websocket'

const MAX_HISTORY_MESSAGES = 100

interface ChatState {
  messages: StreamingChatMessage[]
  inputValue: string
  loading: boolean
  sessionToken: string | null
  skills: Skill[]
  activeSkill: Skill | null
  showSkillDropdown: boolean
  streamingMsgId: string | null
  ws: ChatWebSocket | null
  connectedPatientId: number | null

  setMessages: (messages: StreamingChatMessage[] | ((prev: StreamingChatMessage[]) => StreamingChatMessage[])) => void
  addMessage: (message: StreamingChatMessage) => void
  updateMessage: (id: string, update: Partial<StreamingChatMessage>) => void
  setInputValue: (value: string) => void
  setLoading: (loading: boolean) => void
  setSessionToken: (token: string | null) => void
  setSkills: (skills: Skill[]) => void
  setActiveSkill: (skill: Skill | null) => void
  setShowSkillDropdown: (show: boolean) => void
  setStreamingMsgId: (id: string | null) => void
  connectWebSocket: (patientId: number, onMessage: (data: WSResponse) => void, onError: () => void) => void
  disconnectWebSocket: () => void
  clearMessages: () => void
  clearHistory: () => void
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      messages: [],
      inputValue: '',
      loading: false,
      sessionToken: null,
      skills: [],
      activeSkill: null,
      showSkillDropdown: false,
      streamingMsgId: null,
      ws: null,
      connectedPatientId: null,

      setMessages: (messages) => {
        if (typeof messages === 'function') {
          set((state) => {
            const newMessages = messages(state.messages)
            return { messages: newMessages.slice(-MAX_HISTORY_MESSAGES) }
          })
        } else {
          set({ messages: messages.slice(-MAX_HISTORY_MESSAGES) })
        }
      },

      addMessage: (message) => set((state) => {
        const newMessages = [...state.messages, message]
        return { messages: newMessages.slice(-MAX_HISTORY_MESSAGES) }
      }),

      updateMessage: (id, update) => set((state) => ({
        messages: state.messages.map((m) => (m.id === id ? { ...m, ...update } : m)),
      })),

      setInputValue: (value) => set({ inputValue: value }),
      setLoading: (loading) => set({ loading }),
      setSessionToken: (token) => set({ sessionToken: token }),
      setSkills: (skills) => set({ skills }),
      setActiveSkill: (skill) => set({ activeSkill: skill }),
      setShowSkillDropdown: (show) => set({ showSkillDropdown: show }),
      setStreamingMsgId: (id) => set({ streamingMsgId: id }),

      connectWebSocket: (patientId, onMessage, onError) => {
        const { ws, connectedPatientId } = get()
        
        if (ws && connectedPatientId === patientId) {
          return
        }

        if (ws) {
          ws.close()
        }

        const newWs = new ChatWebSocket(patientId)
        newWs.onMessage(onMessage)
        newWs.onError(onError)
        newWs.connect()

        set({ ws: newWs, connectedPatientId: patientId })
      },

      disconnectWebSocket: () => {
        const { ws } = get()
        if (ws) {
          ws.close()
          set({ ws: null, connectedPatientId: null })
        }
      },

      clearMessages: () => set({ messages: [], sessionToken: null }),
      
      clearHistory: () => set({ messages: [], sessionToken: null }),
    }),
    {
      name: 'chat-history',
      partialize: (state) => ({ messages: state.messages }),
    }
  )
)
