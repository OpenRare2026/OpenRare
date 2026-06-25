import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Card,
  Descriptions,
  Tag,
  Progress,
  Collapse,
  Empty,
  Spin,
  Button,
  Space,
  Alert,
  Typography,
  Divider,
  Tooltip,
  Badge,
} from 'antd'
import {
  InfoCircleOutlined,
  SyncOutlined,
} from '@ant-design/icons'
import type { Variant, ACMGClassification, CriterionResult, EvidenceStrength } from '@/types'
import api from '@/services/api'

const { Panel } = Collapse
const { Text, Title } = Typography

interface ACMGDisplayProps {
  variant: Variant
  onClassify?: (classification: ACMGClassification) => void
}

const STRENGTH_ORDER: EvidenceStrength[] = [
  'pathogenic_very_strong',
  'pathogenic_strong',
  'pathogenic_moderate',
  'pathogenic_supporting',
  'benign_standalone',
  'benign_strong',
  'benign_supporting',
]

const STRENGTH_COLORS: Record<EvidenceStrength, string> = {
  pathogenic_very_strong: 'red',
  pathogenic_strong: 'orange',
  pathogenic_moderate: 'gold',
  pathogenic_supporting: 'blue',
  benign_standalone: 'cyan',
  benign_strong: 'green',
  benign_supporting: 'lime',
}

const CLASSIFICATION_COLORS: Record<string, string> = {
  Pathogenic: '#f5222d',
  'Likely Pathogenic': '#fa8c16',
  'Variant of Uncertain Significance': '#8c8c8c',
  'Likely Benign': '#52c41a',
  Benign: '#13c2c2',
}

const ACMGDisplay: React.FC<ACMGDisplayProps> = ({ variant, onClassify }) => {
  const { t } = useTranslation()
  const [classification, setClassification] = useState<ACMGClassification | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchClassification = async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await api.getACMGClassification(variant.id)
      setClassification(result)
      onClassify?.(result)
    } catch (err: any) {
      const isNotFound = err?.status === 404 || err?.code === 'NOT_FOUND'
      if (isNotFound) {
        try {
          const result = await api.runACMGAnalysis(variant.id)
          setClassification(result)
          onClassify?.(result)
        } catch (analysisErr) {
          setError('Failed to run ACMG analysis')
        }
      } else {
        setError('Failed to load classification')
      }
    } finally {
      setLoading(false)
    }
  }

  const runAnalysis = async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await api.runACMGAnalysis(variant.id)
      setClassification(result)
      onClassify?.(result)
    } catch (err) {
      setError('Failed to run ACMG analysis')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchClassification()
  }, [variant.id])

  const renderCriterionCard = (criterion: CriterionResult) => {
    const strengthColor = STRENGTH_COLORS[criterion.evidence_strength]
    const isMet = criterion.is_met

    return (
      <div
        key={criterion.criterion_code}
        style={{
          padding: 12,
          background: isMet ? '#f6ffed' : '#fafafa',
          borderRadius: 8,
          marginBottom: 8,
          borderLeft: `3px solid ${isMet ? strengthColor : '#d9d9d9'}`,
        }}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="small">
          <Space>
            <Badge
              status={isMet ? 'success' : 'default'}
              text={
                <Text strong style={{ fontSize: 14 }}>
                  {criterion.criterion_code}
                </Text>
              }
            />
            <Tag color={strengthColor}>{criterion.evidence_strength.replace(/_/g, ' ')}</Tag>
            <Text type="secondary" style={{ fontSize: 12 }}>
              Score: {criterion.score > 0 ? '+' : ''}
              {criterion.score}
            </Text>
          </Space>

          <Text style={{ fontSize: 12 }}>{criterion.criterion_name}</Text>

          {isMet && (
            <>
              <Text style={{ fontSize: 12, color: '#52c41a' }}>{criterion.description}</Text>
              <Space wrap>
                {criterion.evidence_sources.map((source, idx) => (
                  <Tag key={idx} color="blue" style={{ fontSize: 11 }}>
                    {source}
                  </Tag>
                ))}
              </Space>
              <Progress
                percent={criterion.confidence * 100}
                size="small"
                showInfo={false}
                strokeColor="#52c41a"
              />
            </>
          )}
        </Space>
      </div>
    )
  }

  const groupCriteriaByStrength = (criteria: CriterionResult[], direction: 'pathogenic' | 'benign') => {
    const filtered = criteria.filter((c) => c.direction === direction)
    const grouped: Record<string, CriterionResult[]> = {}

    filtered.forEach((c) => {
      const strength = c.evidence_strength
      if (!grouped[strength]) grouped[strength] = []
      grouped[strength].push(c)
    })

    return STRENGTH_ORDER.filter(
      (s) =>
        (direction === 'pathogenic' && s.startsWith('pathogenic')) ||
        (direction === 'benign' && s.startsWith('benign'))
    ).map((strength) => ({
      strength,
      criteria: grouped[strength] || [],
    }))
  }

  if (loading) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>
            <Text>{t('acmg.analyzing')}</Text>
          </div>
        </div>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <Alert
          message={t('acmg.classError')}
          description={error}
          type="error"
          action={
            <Button size="small" onClick={runAnalysis}>
              {t('common.retry')}
            </Button>
          }
        />
      </Card>
    )
  }

  if (!classification) {
    return (
      <Card>
        <Empty description={t('acmg.noClass')}>
          <Button type="primary" onClick={runAnalysis} icon={<SyncOutlined />}>
            {t('acmg.runAnalysis')}
          </Button>
        </Empty>
      </Card>
    )
  }

  const pathogenicGroups = groupCriteriaByStrength(classification.pathogenic_criteria ?? [], 'pathogenic')
  const benignGroups = groupCriteriaByStrength(classification.benign_criteria ?? [], 'benign')

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      <Card>
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <div style={{ textAlign: 'center' }}>
            <Title level={3} style={{ marginBottom: 8 }}>
              {t('acmg.title')}
            </Title>
            <div
              style={{
                display: 'inline-block',
                padding: '12px 24px',
                borderRadius: 8,
                background: CLASSIFICATION_COLORS[classification.classification] || '#8c8c8c',
                color: 'white',
              }}
            >
              <Text strong style={{ fontSize: 20, color: 'white' }}>
                {classification.classification}
              </Text>
            </div>
          </div>

          <div style={{ textAlign: 'center' }}>
            <Progress
              type="circle"
              percent={(classification.confidence_score ?? 0) * 100}
              format={(percent) => (
                <span>
                  <div>
                    <Text strong>{t('acmg.confidence')}</Text>
                  </div>
                  <div>
                    <Text style={{ fontSize: 20 }}>{percent?.toFixed(1)}%</Text>
                  </div>
                </span>
              )}
              strokeColor={{
                '0%': '#108ee9',
                '100%': '#87d068',
              }}
              size={120}
            />
          </div>

          <Descriptions column={2} bordered size="small">
            <Descriptions.Item label="Variant ID">{classification.variant_id}</Descriptions.Item>
            <Descriptions.Item label="Pathogenic Score">
              <Text type="danger" strong>
                +{(classification.total_pathogenic_score ?? 0).toFixed(1)}
              </Text>
            </Descriptions.Item>
            <Descriptions.Item label="Benign Score">
              <Text type="success" strong>
                {(classification.total_benign_score ?? 0).toFixed(1)}
              </Text>
            </Descriptions.Item>
            <Descriptions.Item label="Total Criteria">
              {(classification.pathogenic_criteria?.length ?? 0) + (classification.benign_criteria?.length ?? 0)}
            </Descriptions.Item>
          </Descriptions>
        </Space>
      </Card>

      <Card title={t('acmg.evidenceSummary')}>
        <Collapse defaultActiveKey={['pathogenic', 'benign']}>
          <Panel
            header={
              <Space>
                <Text strong>{t('acmg.pathEvidence')}</Text>
                <Tag color="red">
                  {(classification.pathogenic_criteria ?? []).filter((c) => c.is_met).length} {t('acmg.met')}
                </Tag>
              </Space>
            }
            key="pathogenic"
          >
            {pathogenicGroups.map(({ strength, criteria }) =>
              criteria.length > 0 ? (
                <div key={strength} style={{ marginBottom: 16 }}>
                  <Divider orientation="left" style={{ margin: '12px 0' }}>
                    <Tag color={STRENGTH_COLORS[strength]}>
                      {strength.replace(/_/g, ' ').toUpperCase()}
                    </Tag>
                  </Divider>
                  {criteria.map(renderCriterionCard)}
                </div>
              ) : null
            )}
          </Panel>

          <Panel
            header={
              <Space>
                <Text strong>{t('acmg.benEvidence')}</Text>
                <Tag color="green">
                  {(classification.benign_criteria ?? []).filter((c) => c.is_met).length} {t('acmg.met')}
                </Tag>
              </Space>
            }
            key="benign"
          >
            {benignGroups.map(({ strength, criteria }) =>
              criteria.length > 0 ? (
                <div key={strength} style={{ marginBottom: 16 }}>
                  <Divider orientation="left" style={{ margin: '12px 0' }}>
                    <Tag color={STRENGTH_COLORS[strength]}>
                      {strength.replace(/_/g, ' ').toUpperCase()}
                    </Tag>
                  </Divider>
                  {criteria.map(renderCriterionCard)}
                </div>
              ) : null
            )}
          </Panel>
        </Collapse>
      </Card>

      {(classification.warnings?.length ?? 0) > 0 && (
        <Card title={t('acmg.warnings')}>
          {(classification.warnings ?? []).map((warning, idx) => (
            <Alert
              key={idx}
              message={warning}
              type="warning"
              showIcon
              style={{ marginBottom: 8 }}
            />
          ))}
        </Card>
      )}

      <Card
        title={t('acmg.evidenceChain')}
        extra={
          <Tooltip title={t('acmg.evidenceTooltip')}>
            <InfoCircleOutlined />
          </Tooltip>
        }
      >
        <div
          style={{
            background: '#fafafa',
            padding: 16,
            borderRadius: 8,
            maxHeight: 300,
            overflow: 'auto',
          }}
        >
          {(classification.evidence_chain ?? []).map((item, idx) => (
            <div key={idx} style={{ marginBottom: 8 }}>
              <Space>
                <Tag color="blue">{item.criterion}</Tag>
                <Text>{item.description}</Text>
                <Text type="secondary">(Score: {item.score ?? 'N/A'})</Text>
              </Space>
            </div>
          ))}
        </div>
      </Card>

      <Button type="primary" onClick={runAnalysis} icon={<SyncOutlined />} block>
        {t('acmg.reanalyze')}
      </Button>
    </Space>
  )
}

export default ACMGDisplay
