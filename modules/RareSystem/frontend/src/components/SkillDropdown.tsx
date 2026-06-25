import React, { useState, useEffect, useRef, useMemo } from 'react'
import { Input, List, Typography, Tag } from 'antd'
import {
  ExperimentOutlined,
  SearchOutlined,
  MedicineBoxOutlined,
  BookOutlined,
  ApartmentOutlined,
} from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import type { Skill, SkillType } from '@/types'

const { Text } = Typography

interface SkillDropdownProps {
  skills: Skill[]
  onSelect: (skill: Skill) => void
  visible: boolean
  onClose: () => void
}

const iconMap: Record<string, React.ReactNode> = {
  experiment: <ExperimentOutlined />,
  search: <SearchOutlined />,
  'medicine-box': <MedicineBoxOutlined />,
  book: <BookOutlined />,
  apartment: <ApartmentOutlined />,
}

const typeColors: Record<SkillType, string> = {
  prompt_injection: 'blue',
  tool_call: 'green',
}

const SkillDropdown: React.FC<SkillDropdownProps> = ({ skills, onSelect, visible, onClose }) => {
  const { t } = useTranslation()
  const [search, setSearch] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const listRef = useRef<HTMLDivElement>(null)

  const typeLabels: Record<SkillType, string> = {
    prompt_injection: t('settings.aiAnalysis'),
    tool_call: t('settings.dataQuery'),
  }

  useEffect(() => {
    if (visible) {
      setSearch('')
      setSelectedIndex(0)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [visible])

  const filteredSkills = useMemo(() => {
    if (!search.trim()) return skills
    const lower = search.toLowerCase()
    return skills.filter(s =>
      s.name.toLowerCase().includes(lower) ||
      s.description.toLowerCase().includes(lower)
    )
  }, [skills, search])

  useEffect(() => {
    setSelectedIndex(0)
  }, [filteredSkills.length])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setSelectedIndex(i => Math.min(i + 1, filteredSkills.length - 1))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setSelectedIndex(i => Math.max(i - 1, 0))
    } else if (e.key === 'Enter' && filteredSkills[selectedIndex]) {
      e.preventDefault()
      onSelect(filteredSkills[selectedIndex])
      onClose()
    } else if (e.key === 'Escape') {
      e.preventDefault()
      onClose()
    }
  }

  if (!visible) return null

  return (
    <div
      style={{
        position: 'absolute',
        bottom: '100%',
        left: 0,
        right: 0,
        marginBottom: 4,
        background: '#fff',
        border: '1px solid #d9d9d9',
        borderRadius: 8,
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        maxHeight: 320,
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        zIndex: 1000,
      }}
    >
      <div style={{ padding: '8px 12px', borderBottom: '1px solid #f0f0f0' }}>
        <Input
          ref={inputRef as any}
          placeholder={t('skills.searchPlaceholder')}
          value={search}
          onChange={e => setSearch(e.target.value)}
          onKeyDown={handleKeyDown}
          size="small"
          style={{ borderRadius: 6 }}
          allowClear
        />
      </div>
      <div ref={listRef} style={{ overflowY: 'auto', flex: 1 }}>
        <List
          size="small"
          dataSource={filteredSkills}
          renderItem={(skill, index) => (
            <List.Item
              onClick={() => { onSelect(skill); onClose() }}
              style={{
                padding: '8px 12px',
                cursor: 'pointer',
                background: index === selectedIndex ? '#e6f7ff' : 'transparent',
                transition: 'background 0.15s',
              }}
              onMouseEnter={() => setSelectedIndex(index)}
            >
              <div style={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                <span style={{ marginRight: 8, fontSize: 16 }}>
                  {iconMap[skill.icon] || <ExperimentOutlined />}
                </span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Text strong style={{ fontSize: 13 }}>
                      {skill.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </Text>
                    <Tag color={typeColors[skill.skill_type]} style={{ fontSize: 10, lineHeight: '16px', margin: 0 }}>
                      {typeLabels[skill.skill_type]}
                    </Tag>
                  </div>
                  <Text type="secondary" style={{ fontSize: 11, display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {skill.description}
                  </Text>
                </div>
              </div>
            </List.Item>
          )}
        />
      </div>
    </div>
  )
}

export default SkillDropdown
