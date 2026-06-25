import React from 'react'
import { useTranslation } from 'react-i18next'
import { Card, Tag, Collapse, Tooltip, Space, Typography } from 'antd'
import {
  ExperimentOutlined,
  SearchOutlined,
  MedicineBoxOutlined,
  BookOutlined,
  ApartmentOutlined,
  LinkOutlined,
  FileTextOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { Skill, ChatReference, SkillType } from '@/types'

const { Text } = Typography

interface SkillCardProps {
  skill: Skill
  content: string
  references?: ChatReference[]
  confidence?: number
}

const iconMap: Record<string, React.ReactNode> = {
  experiment: <ExperimentOutlined />,
  search: <SearchOutlined />,
  'medicine-box': <MedicineBoxOutlined />,
  book: <BookOutlined />,
  apartment: <ApartmentOutlined />,
}

const borderColors: Record<SkillType, string> = {
  prompt_injection: '#1890ff',
  tool_call: '#52c41a',
}

const SkillCard: React.FC<SkillCardProps> = ({ skill, content, references, confidence }) => {
  const { t } = useTranslation()
  const borderColor = borderColors[skill.skill_type] || '#d9d9d9'
  const icon = iconMap[skill.icon] || <ExperimentOutlined />

  const formatSkillName = (name: string) =>
    name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())

  const renderReference = (reference: ChatReference) => {
    const colors: Record<string, string> = {
      variant: 'blue',
      report: 'green',
      evidence: 'orange',
      patient_summary: 'purple',
      clinical_notes: 'cyan',
    }
    const icons: Record<string, React.ReactNode> = {
      variant: <FileTextOutlined />,
      report: <FileTextOutlined />,
      evidence: <LinkOutlined />,
      patient_summary: <FileTextOutlined />,
      clinical_notes: <FileTextOutlined />,
    }

    return (
      <Tooltip key={reference.id} title={`Source: ${reference.type}`}>
        <Tag
          color={colors[reference.type] || 'default'}
          icon={icons[reference.type] || <FileTextOutlined />}
          style={{ cursor: 'pointer' }}
        >
          {reference.label}
        </Tag>
      </Tooltip>
    )
  }

  return (
    <Card
      size="small"
      style={{
        borderLeft: `4px solid ${borderColor}`,
        marginBottom: 8,
        boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
        <span style={{ marginRight: 8, fontSize: 16, color: borderColor }}>{icon}</span>
        <Text strong style={{ marginRight: 8 }}>{formatSkillName(skill.name)}</Text>
        <Tag color={skill.skill_type === 'prompt_injection' ? 'blue' : 'green'} style={{ fontSize: 10 }}>
          {skill.skill_type === 'prompt_injection' ? t('settings.aiAnalysis') : t('settings.dataQuery')}
        </Tag>
        {confidence !== undefined && (
          <Tag
            icon={<InfoCircleOutlined />}
            color={confidence >= 0.7 ? 'green' : confidence >= 0.5 ? 'orange' : 'red'}
            style={{ fontSize: 10, marginLeft: 'auto' }}
          >
            {Math.round(confidence * 100)}%
          </Tag>
        )}
      </div>

      <Collapse
        ghost
        defaultActiveKey={['content']}
        items={[{
          key: 'content',
          label: <Text type="secondary" style={{ fontSize: 12 }}>{t('common.result')}</Text>,
          children: (
            <div className="markdown-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {content}
              </ReactMarkdown>
            </div>
          ),
        }]}
      />

      {references && references.length > 0 && (
        <div style={{ marginTop: 8 }}>
          <Space wrap>{references.map(renderReference)}</Space>
        </div>
      )}
    </Card>
  )
}

export default SkillCard
