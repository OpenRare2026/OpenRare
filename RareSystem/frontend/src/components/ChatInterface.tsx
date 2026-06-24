import React, { useRef, useEffect, useCallback } from 'react'
import {
  Input,
  Button,
  Space,
  Typography,
  Tag,
  Avatar,
  Empty,
  Divider,
  message as antdMessage,
  Popconfirm,
} from 'antd'
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  DeleteOutlined,
  HistoryOutlined,
} from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import type { StreamingChatMessage, Skill, WSResponse } from '@/types'
import { wsManager } from '@/services/websocket'
import api from '@/services/api'
import StreamingMessage from './StreamingMessage'
import SkillDropdown from './SkillDropdown'
import { useChatStore } from '@/store/chatStore'

const { Text } = Typography
const { TextArea } = Input

interface ChatInterfaceProps {
  patientId: number
  initialMessages?: StreamingChatMessage[]
  onSessionCreated?: (sessionToken: string) => void
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  patientId,
  initialMessages = [],
  onSessionCreated,
}) => {
  const { t } = useTranslation()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const streamingMsgIdRef = useRef<string | null>(null)
  
  const {
    messages,
    inputValue,
    loading,
    sessionToken,
    skills,
    activeSkill,
    showSkillDropdown,
    setMessages,
    updateMessage,
    setInputValue,
    setLoading,
    setSessionToken,
    setSkills,
    setActiveSkill,
    setShowSkillDropdown,
    clearHistory,
  } = useChatStore()

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  useEffect(() => {
    if (initialMessages.length > 0 && messages.length === 0) {
      setMessages(initialMessages)
    }
  }, [initialMessages, messages.length, setMessages])

  useEffect(() => {
    const handleWSMessage = (data: WSResponse) => {
      const msgId = streamingMsgIdRef.current
      
      if (data.type === 'chunk') {
        if (!msgId) return
        const currentMsg = useChatStore.getState().messages.find(m => m.id === msgId)
        updateMessage(msgId, {
          content: (currentMsg?.content || '') + (data.content || ''),
          is_streaming: true,
          skill_name: data.skill_name || currentMsg?.skill_name,
          skill_type: data.skill_type || currentMsg?.skill_type,
        })
      } else if (data.type === 'skill_result') {
        if (!msgId) return
        updateMessage(msgId, {
          content: data.content || '',
          skill_name: data.skill_name,
          skill_type: data.skill_type,
          references: data.references,
          confidence: data.confidence,
        })
      } else if (data.type === 'done') {
        if (data.session_token) {
          setSessionToken(data.session_token)
          onSessionCreated?.(data.session_token)
        }

        if (msgId) {
          updateMessage(msgId, {
            is_streaming: false,
            references: data.references,
            confidence: data.confidence !== undefined ? data.confidence : undefined,
          })
        }

        setLoading(false)
        streamingMsgIdRef.current = null
        setActiveSkill(null)
      } else if (data.type === 'error') {
        if (msgId) {
          updateMessage(msgId, {
            content: `Error: ${data.content || 'Unknown error'}`,
            is_streaming: false,
          })
        }
        setLoading(false)
        streamingMsgIdRef.current = null
        setActiveSkill(null)
      } else if (data.type === 'session_info' && data.session_token) {
        setSessionToken(data.session_token)
        onSessionCreated?.(data.session_token)
      }
    }

    const handleWSError = () => {
      antdMessage.error(t('chat.wsError'))
    }

    wsManager.connect(patientId)
    const unsubscribe = wsManager.subscribe(handleWSMessage, handleWSError)

    loadSkills()

    return () => {
      unsubscribe()
    }
  }, [patientId])

  const loadSkills = useCallback(async () => {
    try {
      const skillList = await api.getSkills()
      setSkills(skillList.filter(s => s.is_enabled))
    } catch (err) {
      console.error('Failed to load skills:', err)
    }
  }, [setSkills])

  useEffect(() => {
    if (useChatStore.getState().skills.length === 0) {
      loadSkills()
    }
  }, [loadSkills])

  const handleSend = useCallback(() => {
    if (!inputValue.trim() || loading) return

    const userMessage: StreamingChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString(),
    }

    const assistantMsgId = `resp-${Date.now()}`
    const assistantMessage: StreamingChatMessage = {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      is_streaming: true,
      skill_name: activeSkill?.name,
      skill_type: activeSkill?.skill_type,
    }

    setMessages([...messages, userMessage, assistantMessage])
    streamingMsgIdRef.current = assistantMsgId
    setInputValue('')
    setLoading(true)

    if (wsManager.isConnected()) {
      const msgType = activeSkill ? 'skill' : 'chat'
      wsManager.send({
        type: msgType,
        content: userMessage.content,
        skill_name: activeSkill?.name,
        session_token: sessionToken ?? undefined,
      })
    } else {
      api.sendChatMessage(patientId, userMessage.content, sessionToken ?? undefined)
        .then(response => {
          updateMessage(assistantMsgId, {
            content: response.content,
            is_streaming: false,
            references: response.references,
            confidence: response.confidence,
          })
          setLoading(false)
        })
        .catch(() => {
          antdMessage.error(t('chat.responseError'))
          setMessages(messages.filter(m => m.id !== assistantMsgId && m.id !== userMessage.id))
          setLoading(false)
        })
    }

    setActiveSkill(null)
    setShowSkillDropdown(false)
  }, [inputValue, loading, patientId, sessionToken, activeSkill, messages])

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (showSkillDropdown) return
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value
    setInputValue(value)

    if (value === '/') {
      setShowSkillDropdown(true)
    } else if (!value.startsWith('/') && showSkillDropdown) {
      setShowSkillDropdown(false)
    }
  }

  const handleSkillSelect = (skill: Skill) => {
    setActiveSkill(skill)
    setInputValue('')
    setShowSkillDropdown(false)
  }

  const renderMessage = (msg: StreamingChatMessage) => {
    const isUser = msg.role === 'user'

    if (isUser) {
      return (
        <div
          key={msg.id}
          style={{
            display: 'flex',
            justifyContent: 'flex-end',
            marginBottom: 16,
          }}
        >
          <div style={{ display: 'flex', maxWidth: '80%', flexDirection: 'row-reverse' }}>
            <Avatar
              icon={<UserOutlined />}
              style={{ background: '#1890ff', margin: '0 0 0 12px', flexShrink: 0 }}
            />
            <div>
              <div
                style={{
                  background: '#1890ff',
                  color: 'white',
                  padding: '12px 16px',
                  borderRadius: 12,
                  borderTopRightRadius: 4,
                }}
              >
                <Text style={{ margin: 0, color: 'inherit', whiteSpace: 'pre-wrap' }}>{msg.content}</Text>
              </div>
              <div style={{ marginTop: 4 }}>
                <Text type="secondary" style={{ fontSize: 11 }}>
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </Text>
              </div>
            </div>
          </div>
        </div>
      )
    }

    return (
      <div
        key={msg.id}
        style={{
          display: 'flex',
          justifyContent: 'flex-start',
          marginBottom: 16,
        }}
      >
        <div style={{ display: 'flex', maxWidth: '80%', flexDirection: 'row' }}>
          <Avatar
            icon={<RobotOutlined />}
            style={{ background: '#52c41a', margin: '0 12px 0 0', flexShrink: 0 }}
          />
          <div style={{ flex: 1, minWidth: 0 }}>
            {msg.skill_name ? (
              <StreamingMessage
                content={msg.content}
                isStreaming={!!msg.is_streaming}
                references={msg.references}
                confidence={msg.confidence}
                skillName={msg.skill_name}
                skillType={msg.skill_type}
                skills={skills}
              />
            ) : (
              <div
                style={{
                  background: '#f5f5f5',
                  padding: '12px 16px',
                  borderRadius: 12,
                  borderTopLeftRadius: 4,
                }}
              >
                <StreamingMessage
                  content={msg.content}
                  isStreaming={!!msg.is_streaming}
                  references={msg.references}
                  confidence={msg.confidence}
                  skills={skills}
                />
              </div>
            )}
            <div style={{ marginTop: 4, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Text type="secondary" style={{ fontSize: 11 }}>
                {new Date(msg.timestamp).toLocaleTimeString()}
              </Text>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        background: '#fff',
      }}
    >
      {messages.length > 0 && (
        <div
          style={{
            padding: '8px 16px',
            borderBottom: '1px solid #f0f0f0',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            background: '#fafafa',
          }}
        >
          <Space>
            <HistoryOutlined style={{ color: '#8c8c8c' }} />
            <Text type="secondary" style={{ fontSize: 12 }}>
              {t('chat.historyCount', { count: messages.length })}
            </Text>
          </Space>
          <Popconfirm
            title={t('chat.clearConfirm')}
            description={t('chat.clearDesc')}
            onConfirm={() => {
              clearHistory()
              antdMessage.success(t('chat.clearHistory'))
            }}
            okText={t('common.confirm')}
            cancelText={t('common.cancel')}
            okButtonProps={{ danger: true }}
          >
            <Button
              type="text"
              size="small"
              danger
              icon={<DeleteOutlined />}
            >
              {t('chat.clearHistory')}
            </Button>
          </Popconfirm>
        </div>
      )}
      
      <div
        style={{
          flex: 1,
          overflow: 'auto',
          padding: '16px 16px 8px 16px',
        }}
      >
        {messages.length === 0 ? (
          <Empty
            description={t('chat.startConversation')}
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            style={{ marginTop: 60 }}
          />
        ) : (
          messages.map(renderMessage)
        )}
        <div ref={messagesEndRef} />
      </div>

      <Divider style={{ margin: '8px 0 0 0' }} />

      <div style={{ padding: '12px 16px', background: '#fafafa', position: 'relative' }}>
        <Space.Compact style={{ width: '100%' }}>
          <TextArea
            value={inputValue}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder={activeSkill ? t('chat.skillPlaceholder', { skill: activeSkill.name }) : t('chat.placeholder')}
            autoSize={{ minRows: 1, maxRows: 4 }}
            disabled={loading}
            style={{ borderRadius: '8px 0 0 8px', resize: 'none' }}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            loading={loading}
            style={{ height: 'auto', borderRadius: '0 8px 8px 0' }}
          />
        </Space.Compact>

        {activeSkill && (
          <div style={{ marginTop: 8 }}>
            <Tag
              color="blue"
              closable
              onClose={() => setActiveSkill(null)}
            >
              {activeSkill.name}
            </Tag>
          </div>
        )}

        {showSkillDropdown && (
          <SkillDropdown
            skills={skills}
            visible={showSkillDropdown}
            onSelect={handleSkillSelect}
            onClose={() => setShowSkillDropdown(false)}
          />
        )}
      </div>
    </div>
  )
}

export default ChatInterface
