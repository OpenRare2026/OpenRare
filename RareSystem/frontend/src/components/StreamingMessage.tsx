import React, { useEffect, useRef } from 'react'
import { Tag, Space, Spin, Tooltip } from 'antd'
import {
  LinkOutlined,
  FileTextOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { ChatReference, SkillType } from '@/types'
import SkillCard from './SkillCard'
import type { Skill } from '@/types'

interface StreamingMessageProps {
  content: string
  isStreaming: boolean
  references?: ChatReference[]
  confidence?: number
  skillName?: string
  skillType?: SkillType
  skills?: Skill[]
}

const referenceColors: Record<string, string> = {
  variant: 'blue',
  report: 'green',
  evidence: 'orange',
  patient_summary: 'purple',
  clinical_notes: 'cyan',
}

const referenceIcons: Record<string, React.ReactNode> = {
  variant: <FileTextOutlined />,
  report: <FileTextOutlined />,
  evidence: <LinkOutlined />,
  patient_summary: <FileTextOutlined />,
  clinical_notes: <FileTextOutlined />,
}

const StreamingMessage: React.FC<StreamingMessageProps> = ({
  content,
  isStreaming,
  references,
  confidence,
  skillName,
  skillType: _skillType,
  skills = [],
}) => {
  const contentRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isStreaming && contentRef.current) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight
    }
  }, [content, isStreaming])

  const skill = skills.find(s => s.name === skillName)

  if (skill && skillName) {
    return (
      <SkillCard
        skill={skill}
        content={content}
        references={references}
        confidence={confidence}
      />
    )
  }

  return (
    <div style={{ position: 'relative' }}>
      <div
        ref={contentRef}
        style={{
          padding: '8px 0',
          maxHeight: isStreaming ? 300 : undefined,
          overflowY: isStreaming ? 'auto' : undefined,
        }}
      >
        <div className="markdown-content">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {content}
          </ReactMarkdown>
          {isStreaming && (
            <span
              style={{
                display: 'inline-block',
                width: 6,
                height: 14,
                background: '#1890ff',
                marginLeft: 2,
                verticalAlign: 'middle',
                animation: 'blink 1s infinite',
              }}
            />
          )}
        </div>
      </div>

      {!isStreaming && references && references.length > 0 && (
        <div style={{ marginTop: 8 }}>
          <Space wrap>
            {references.map(ref => (
              <Tooltip key={ref.id} title={`Source: ${ref.type}`}>
                <Tag
                  color={referenceColors[ref.type] || 'default'}
                  icon={referenceIcons[ref.type] || <FileTextOutlined />}
                  style={{ cursor: 'pointer' }}
                >
                  {ref.label}
                </Tag>
              </Tooltip>
            ))}
          </Space>
        </div>
      )}

      {!isStreaming && confidence !== undefined && (
        <div style={{ marginTop: 4 }}>
          <Tag
            icon={<InfoCircleOutlined />}
            color={confidence >= 0.7 ? 'green' : confidence >= 0.5 ? 'orange' : 'red'}
            style={{ fontSize: 10 }}
          >
            {Math.round(confidence * 100)}%
          </Tag>
        </div>
      )}

      {isStreaming && (
        <div style={{ textAlign: 'center', padding: '4px 0' }}>
          <Spin size="small" />
        </div>
      )}

      <style>{`
        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0; }
        }
        .markdown-content {
          line-height: 1.6;
        }
        .markdown-content p {
          margin: 0 0 8px 0;
        }
        .markdown-content p:last-child {
          margin-bottom: 0;
        }
        .markdown-content h1, .markdown-content h2, .markdown-content h3,
        .markdown-content h4, .markdown-content h5, .markdown-content h6 {
          margin: 12px 0 8px 0;
          font-weight: 600;
        }
        .markdown-content h1 { font-size: 1.4em; }
        .markdown-content h2 { font-size: 1.2em; }
        .markdown-content h3 { font-size: 1.1em; }
        .markdown-content ul, .markdown-content ol {
          margin: 8px 0;
          padding-left: 20px;
        }
        .markdown-content li {
          margin: 4px 0;
        }
        .markdown-content code {
          background: #f0f0f0;
          padding: 2px 6px;
          border-radius: 4px;
          font-family: 'Monaco', 'Menlo', monospace;
          font-size: 0.9em;
        }
        .markdown-content pre {
          background: #282c34;
          color: #abb2bf;
          padding: 12px;
          border-radius: 8px;
          overflow-x: auto;
          margin: 8px 0;
        }
        .markdown-content pre code {
          background: transparent;
          padding: 0;
          color: inherit;
        }
        .markdown-content blockquote {
          border-left: 3px solid #1890ff;
          padding-left: 12px;
          margin: 8px 0;
          color: #666;
        }
        .markdown-content table {
          border-collapse: collapse;
          width: 100%;
          margin: 8px 0;
        }
        .markdown-content th, .markdown-content td {
          border: 1px solid #d9d9d9;
          padding: 8px;
          text-align: left;
        }
        .markdown-content th {
          background: #fafafa;
          font-weight: 600;
        }
        .markdown-content a {
          color: #1890ff;
        }
        .markdown-content hr {
          border: none;
          border-top: 1px solid #d9d9d9;
          margin: 12px 0;
        }
      `}</style>
    </div>
  )
}

export default StreamingMessage
