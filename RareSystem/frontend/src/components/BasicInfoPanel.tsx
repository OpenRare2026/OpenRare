import React, { useState, useEffect } from 'react'
import {
  Card,
  Descriptions,
  Tag,
  Collapse,
  Spin,
  Alert,
  Badge,
  Button,
  Space,
  Typography,
  Tooltip,
  Empty,
  message,
  Popconfirm,
  Input,
  Divider,
} from 'antd'
import {
  UserOutlined,
  DownOutlined,
  RightOutlined,
  FileTextOutlined,
  MedicineBoxOutlined,
  TagOutlined,
  ExperimentOutlined,
  LinkOutlined,
  CloseOutlined,
  PlusOutlined,
  ArrowDownOutlined,
  ArrowUpOutlined,
} from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import api from '@/services/api'
import type { CaseSummary } from '@/types'

const { Text } = Typography
const { Panel } = Collapse

interface BasicInfoPanelProps {
  patientId: number
  collapsed?: boolean
  onCollapse?: (collapsed: boolean) => void
  style?: React.CSSProperties
}

const BasicInfoPanel: React.FC<BasicInfoPanelProps> = ({
  patientId,
  collapsed: externalCollapsed,
  onCollapse,
  style,
}) => {
  const { t } = useTranslation()
  const [patientData, setPatientData] = useState<CaseSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [internalCollapsed, setInternalCollapsed] = useState(false)
  const [deletingTerm, setDeletingTerm] = useState<string | null>(null)
  const [hpoInput, setHpoInput] = useState('')
  const [addingHpo, setAddingHpo] = useState(false)
  const [movingTerm, setMovingTerm] = useState<string | null>(null)

  const isCollapsed = externalCollapsed ?? internalCollapsed

  useEffect(() => {
    loadPatientData()
  }, [patientId])

  const loadPatientData = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getCase(patientId)
      setPatientData(data)
    } catch (err: any) {
      setError(err?.message || t('basicInfo.loadError'))
    } finally {
      setLoading(false)
    }
  }

  const handleToggleCollapse = () => {
    const newState = !isCollapsed
    setInternalCollapsed(newState)
    onCollapse?.(newState)
  }

  const getSexLabel = (sex?: string) => {
    switch (sex) {
      case 'M':
        return t('upload.male')
      case 'F':
        return t('upload.female')
      default:
        return sex || '-'
    }
  }

  const primaryTerms = patientData?.hpo_terms?.filter((term: any) => 
    term.display_category !== 'secondary'
  ) || []

  const secondaryTerms = patientData?.hpo_terms?.filter((term: any) => 
    term.display_category === 'secondary'
  ) || []

  const handleDeleteHpoTerm = async (hpoId: string) => {
    if (!patientData?.hpo_terms) return
    
    setDeletingTerm(hpoId)
    try {
      const updatedTerms = patientData.hpo_terms.filter((term: any) => term.hpo_id !== hpoId)
      await api.updatePatientHpoTerms(patientId, updatedTerms)
      setPatientData({
        ...patientData,
        hpo_terms: updatedTerms
      })
      message.success('HPO term removed')
    } catch (err) {
      message.error('Failed to remove HPO term')
      console.error('Delete HPO term error:', err)
    } finally {
      setDeletingTerm(null)
    }
  }

  const handleAddHpoTerm = async () => {
    const hpoId = hpoInput.trim().toUpperCase()
    if (!hpoId) {
      message.warning('Please enter an HPO ID')
      return
    }

    const formattedId = hpoId.startsWith('HP:') ? hpoId : `HP:${hpoId}`
    
    if (patientData?.hpo_terms?.some((term: any) => term.hpo_id === formattedId)) {
      message.warning('This HPO term already exists')
      return
    }

    setAddingHpo(true)
    try {
      const result = await api.lookupHpoTerm(formattedId)
      
      const newTerm = {
        phrase: result.name,
        hpo_id: result.hpo_id,
        category: result.category || 'phenotype',
        display_category: 'primary'
      }

      const updatedTerms = [...(patientData?.hpo_terms || []), newTerm]
      await api.updatePatientHpoTerms(patientId, updatedTerms)
      
      setPatientData({
        ...patientData!,
        hpo_terms: updatedTerms
      })
      
      setHpoInput('')
      message.success(`Added: ${result.name}`)
    } catch (err: any) {
      if (err?.response?.status === 404) {
        message.error('HPO ID not found')
      } else {
        message.error('Failed to add HPO term')
      }
      console.error('Add HPO term error:', err)
    } finally {
      setAddingHpo(false)
    }
  }

  const handleMoveTerm = async (hpoId: string, targetCategory: string) => {
    if (!patientData?.hpo_terms) return
    
    setMovingTerm(hpoId)
    try {
      await api.updateHpoTermCategory(patientId, hpoId, targetCategory)
      
      const updatedTerms = patientData.hpo_terms.map((term: any) => {
        if (term.hpo_id === hpoId) {
          return { ...term, display_category: targetCategory }
        }
        return term
      })
      
      setPatientData({
        ...patientData,
        hpo_terms: updatedTerms
      })
      
      message.success(targetCategory === 'primary' 
        ? t('hpo.movedToPrimary') 
        : t('hpo.movedToSecondary'))
    } catch (err) {
      message.error('Failed to move HPO term')
      console.error('Move HPO term error:', err)
    } finally {
      setMovingTerm(null)
    }
  }

  const renderHpoTag = (term: any, isSecondary: boolean) => {
    const targetCategory = isSecondary ? 'primary' : 'secondary'
    const moveIcon = isSecondary ? <ArrowUpOutlined /> : <ArrowDownOutlined />
    const moveTooltip = isSecondary 
      ? t('hpo.moveToPrimary')
      : t('hpo.moveToSecondary')

    return (
      <Tag
        key={term.hpo_id}
        color={isSecondary ? 'default' : 'processing'}
        style={{ 
          cursor: 'pointer', 
          margin: '2px',
          paddingRight: 4,
        }}
      >
        <Tooltip title={`${term.hpo_id} - Click to view in HPO database`}>
          <span
            style={{ marginRight: 4 }}
            onClick={() => window.open(`https://hpo.jax.org/app/browse/term/${term.hpo_id}`, '_blank')}
          >
            <TagOutlined style={{ marginRight: 4 }} />
            {term.phrase || term.hpo_id}
            <LinkOutlined style={{ marginLeft: 4, fontSize: 10 }} />
          </span>
        </Tooltip>
        <Tooltip title={moveTooltip}>
          <Button
            type="text"
            size="small"
            icon={moveIcon}
            onClick={() => handleMoveTerm(term.hpo_id, targetCategory)}
            loading={movingTerm === term.hpo_id}
            style={{ 
              fontSize: 10, 
              padding: '0 2px',
              height: 'auto',
              lineHeight: 1,
            }}
          />
        </Tooltip>
        <Popconfirm
          title="Remove this HPO term?"
          onConfirm={() => handleDeleteHpoTerm(term.hpo_id)}
          okText="Yes"
          cancelText="No"
        >
          <CloseOutlined 
            style={{ 
              fontSize: 10, 
              marginLeft: 2,
              opacity: deletingTerm === term.hpo_id ? 0.5 : 1,
            }} 
            spin={deletingTerm === term.hpo_id}
          />
        </Popconfirm>
      </Tag>
    )
  }

  if (loading) {
    return (
      <Card style={style} bodyStyle={{ padding: 16 }}>
        <div style={{ textAlign: 'center', padding: 20 }}>
          <Spin />
          <div style={{ marginTop: 8 }}>
            <Text type="secondary">{t('basicInfo.loading')}</Text>
          </div>
        </div>
      </Card>
    )
  }

  if (error) {
    return (
      <Card style={style} bodyStyle={{ padding: 16 }}>
        <Alert
          message={t('basicInfo.errorTitle')}
          description={error}
          type="error"
          showIcon
          action={
            <Button size="small" onClick={loadPatientData}>
              {t('basicInfo.retry')}
            </Button>
          }
        />
      </Card>
    )
  }

  if (!patientData) {
    return null
  }

  if (isCollapsed) {
    return (
      <Card
        style={style}
        bodyStyle={{ padding: '8px 16px' }}
        size="small"
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            <UserOutlined />
            <Text strong>{patientData.patient_name || `Patient ${patientData.patient_id}`}</Text>
            {patientData.age && <Tag>{patientData.age} years</Tag>}
            {patientData.sex && <Tag color="blue">{getSexLabel(patientData.sex)}</Tag>}
            {patientData.hpo_terms && patientData.hpo_terms.length > 0 && (
              <Tag color="processing">
                <ExperimentOutlined style={{ marginRight: 4 }} />
                {patientData.hpo_terms.length} HPO
              </Tag>
            )}
          </Space>
          <Button
            type="text"
            size="small"
            icon={<RightOutlined />}
            onClick={handleToggleCollapse}
          >
            {t('basicInfo.expand')}
          </Button>
        </div>
      </Card>
    )
  }

  return (
    <Card
      style={{ ...style, display: 'flex', flexDirection: 'column' }}
      bodyStyle={{ padding: 0, flex: 1, overflow: 'auto', display: 'flex', flexDirection: 'column' }}
      title={
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            <UserOutlined />
            <span>{t('basicInfo.title')}</span>
          </Space>
          <Button
            type="text"
            size="small"
            icon={<DownOutlined />}
            onClick={handleToggleCollapse}
          >
            {t('basicInfo.collapse')}
          </Button>
        </div>
      }
    >
      <div style={{ flexShrink: 0 }}>
        <Descriptions
          column={4}
          size="small"
          style={{ padding: '12px 16px', borderBottom: '1px solid #f0f0f0' }}
        >
          <Descriptions.Item label={t('basicInfo.patientId')}>
            <Text strong>{patientData.patient_name || `Patient ${patientData.patient_id}`}</Text>
          </Descriptions.Item>
          <Descriptions.Item label={t('basicInfo.age')}>
            {patientData.age ? `${patientData.age} years` : '-'}
          </Descriptions.Item>
          <Descriptions.Item label={t('basicInfo.sex')}>
            <Tag color={patientData.sex === 'M' ? 'blue' : patientData.sex === 'F' ? 'pink' : 'default'}>
              {getSexLabel(patientData.sex)}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label={t('basicInfo.ethnicity')}>
            {patientData.ethnicity || '-'}
          </Descriptions.Item>
        </Descriptions>
      </div>

      <div style={{ flex: 1, overflow: 'auto', minHeight: 0 }}>
        <Collapse
          defaultActiveKey={['phenotype', 'history', 'hpo']}
          ghost
          style={{ borderBottom: '1px solid #f0f0f0' }}
        >
        <Panel
          header={
            <Space>
              <MedicineBoxOutlined />
              <Text strong>{t('basicInfo.phenotype')}</Text>
            </Space>
          }
          key="phenotype"
        >
          <Text style={{ whiteSpace: 'pre-wrap' }}>
            {patientData.diagnosis_description || t('browse.noDescription')}
          </Text>
        </Panel>

        <Panel
          header={
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', paddingRight: 8 }}>
              <Space>
                <ExperimentOutlined />
                <Text strong>HPO Terms</Text>
                {patientData.hpo_terms && patientData.hpo_terms.length > 0 && (
                  <Badge count={patientData.hpo_terms.length} style={{ marginLeft: 8 }} />
                )}
              </Space>
              <Space.Compact size="small" onClick={(e) => e.stopPropagation()}>
                <Input
                  placeholder="HP:0001250"
                  value={hpoInput}
                  onChange={(e) => setHpoInput(e.target.value)}
                  onPressEnter={handleAddHpoTerm}
                  style={{ width: 120 }}
                />
                <Button
                  type="primary"
                  size="small"
                  icon={<PlusOutlined />}
                  onClick={handleAddHpoTerm}
                  loading={addingHpo}
                >
                  Add
                </Button>
              </Space.Compact>
            </div>
          }
          key="hpo"
        >
          {patientData.hpo_terms && patientData.hpo_terms.length > 0 ? (
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <div>
                <Text strong style={{ marginBottom: 8, display: 'block' }}>
                  {t('hpo.primary')} ({primaryTerms.length})
                </Text>
                {primaryTerms.length > 0 ? (
                  <Space wrap>
                    {primaryTerms.map((term: any) => renderHpoTag(term, false))}
                  </Space>
                ) : (
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {t('hpo.noPrimary')}
                  </Text>
                )}
              </div>

              <Divider style={{ margin: '8px 0' }} />

              <div>
                <Text strong style={{ marginBottom: 8, display: 'block' }}>
                  {t('hpo.secondary')} ({secondaryTerms.length})
                </Text>
                {secondaryTerms.length > 0 ? (
                  <Space wrap>
                    {secondaryTerms.map((term: any) => renderHpoTag(term, true))}
                  </Space>
                ) : (
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {t('hpo.noSecondary')}
                  </Text>
                )}
              </div>

              <Text type="secondary" style={{ fontSize: 12 }}>
                {t('hpo.hint')}
              </Text>
            </Space>
          ) : (
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description="No HPO terms extracted"
              style={{ padding: '12px 0' }}
            >
              <Text type="secondary">Enter an HPO ID above or extract from clinical notes during upload</Text>
            </Empty>
          )}
        </Panel>

        <Panel
          header={
            <Space>
              <FileTextOutlined />
              <Text strong>{t('basicInfo.history')}</Text>
            </Space>
          }
          key="history"
        >
          <Text style={{ whiteSpace: 'pre-wrap' }}>
            {patientData.medical_history || t('browse.noDescription')}
          </Text>
        </Panel>
      </Collapse>
      </div>

      <div
        style={{
          padding: '8px 16px',
          background: '#fafafa',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexShrink: 0,
          borderTop: '1px solid #f0f0f0',
        }}
      >
        <Space size="large">
          <span>
            <Text type="secondary">{t('browse.vcfFiles')}: </Text>
            <Badge count={patientData.vcf_files?.length || 0} showZero color="#1890ff" />
          </span>
          <span>
            <Text type="secondary">{t('basicInfo.variants')}: </Text>
            <Text strong>{patientData.total_variants?.toLocaleString() || 0}</Text>
          </span>
          <span>
            <Text type="secondary">{t('basicInfo.classified')}: </Text>
            <Text strong style={{ color: patientData.total_classified > 0 ? '#52c41a' : undefined }}>
              {patientData.total_classified?.toLocaleString() || 0}
            </Text>
          </span>
        </Space>
      </div>
    </Card>
  )
}

export default BasicInfoPanel
