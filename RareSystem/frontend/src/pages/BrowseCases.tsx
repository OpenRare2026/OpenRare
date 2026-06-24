import React, { useState, useEffect } from 'react'
import {
  Card,
  Table,
  Button,
  Tag,
  Space,
  Typography,
  Empty,
  Spin,
  Tooltip,
  Popconfirm,
  message,
} from 'antd'
import {
  FolderOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  DeleteOutlined,
} from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import api from '@/services/api'

const { Text, Title } = Typography

interface VCFFileSummary {
  id: number
  file_name: string
  upload_date: string
  variant_count: number
  classified_count: number
}

interface CaseSummary {
  patient_id: number
  patient_name: string | null
  age: number | null
  sex: string | null
  ethnicity: string | null
  diagnosis_description: string | null
  medical_history: string | null
  vcf_files: VCFFileSummary[]
  total_variants: number
  total_classified: number
}

interface CaseListResponse {
  cases: CaseSummary[]
  total: number
}

interface BrowseCasesProps {
  onOpenCase: (patientId: number, vcfFileId: number) => void
  activePatientId: number | null
  onDeleteCase: (patientId: number) => void
}

const BrowseCases: React.FC<BrowseCasesProps> = ({ onOpenCase, activePatientId, onDeleteCase }) => {
  const { t } = useTranslation()
  const [cases, setCases] = useState<CaseSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [deletingId, setDeletingId] = useState<number | null>(null)

  useEffect(() => {
    loadCases()
  }, [])

  const loadCases = async () => {
    setLoading(true)
    try {
      const response: CaseListResponse = await api.getCases()
      setCases(response.cases)
    } catch (error) {
      console.error('Failed to load cases:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (patientId: number) => {
    setDeletingId(patientId)
    try {
      await api.deleteCase(patientId)
      message.success(t('browse.deleteSuccess'))
      await loadCases()
      onDeleteCase(patientId)
    } catch (error) {
      message.error(t('browse.deleteFailed'))
      console.error('Failed to delete case:', error)
    } finally {
      setDeletingId(null)
    }
  }

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleDateString()
  }

  const columns = [
    {
      title: t('browse.caseId'),
      dataIndex: 'patient_id',
      key: 'patient_id',
      width: 80,
      render: (id: number) => <Tag color="blue">#{id}</Tag>,
    },
    {
      title: t('browse.patientName'),
      dataIndex: 'patient_name',
      key: 'patient_name',
      width: 150,
      render: (name: string | null) => name || <Text type="secondary">{t('browse.unnamed')}</Text>,
    },
    {
      title: t('browse.ageSex'),
      key: 'age_sex',
      width: 80,
      render: (_: unknown, record: CaseSummary) => (
        <Text>
          {record.age ? `${record.age}y` : '-'}
          {record.sex ? `/${record.sex}` : ''}
        </Text>
      ),
    },
    {
      title: t('browse.diagnosis'),
      dataIndex: 'diagnosis_description',
      key: 'diagnosis',
      ellipsis: true,
      render: (desc: string | null) => (
        <Tooltip title={desc}>
          <Text style={{ maxWidth: 200 }} ellipsis>
            {desc || <Text type="secondary">{t('browse.noDescription')}</Text>}
          </Text>
        </Tooltip>
      ),
    },
    {
      title: t('browse.vcfFiles'),
      key: 'vcf_files',
      width: 100,
      render: (_: unknown, record: CaseSummary) => (
        <Space>
          <FolderOutlined />
          <Text>{record.vcf_files.length}</Text>
        </Space>
      ),
    },
    {
      title: t('browse.variants'),
      key: 'variants',
      width: 100,
      render: (_: unknown, record: CaseSummary) => (
        <Space>
          <FileTextOutlined />
          <Text>{record.total_variants.toLocaleString()}</Text>
        </Space>
      ),
    },
    {
      title: t('browse.classified'),
      key: 'classified',
      width: 100,
      render: (_: unknown, record: CaseSummary) => (
        <Space>
          <CheckCircleOutlined style={{ color: '#52c41a' }} />
          <Text>{record.total_classified.toLocaleString()}</Text>
        </Space>
      ),
    },
    {
      title: t('browse.uploaded'),
      key: 'upload_date',
      width: 100,
      render: (_: unknown, record: CaseSummary) => {
        const latestDate = record.vcf_files.reduce((latest, vcf) => {
          const date = new Date(vcf.upload_date)
          return date > latest ? date : latest
        }, new Date(0))
        return latestDate.getTime() > 0 ? (
          <Space>
            <ClockCircleOutlined />
            <Text>{formatDate(latestDate.toISOString())}</Text>
          </Space>
        ) : (
          '-'
        )
      },
    },
    {
      title: t('browse.action'),
      key: 'action',
      width: 140,
      fixed: 'right' as const,
      render: (_: unknown, record: CaseSummary) => {
        const latestVcf = record.vcf_files[0]
        const isActive = record.patient_id === activePatientId
        const isDeleting = deletingId === record.patient_id

        return (
          <Space>
            <Button
              type="primary"
              size="small"
              onClick={() => onOpenCase(record.patient_id, latestVcf?.id || 0)}
              disabled={record.vcf_files.length === 0}
            >
              {t('browse.open')}
            </Button>
            <Tooltip title={isActive ? t('browse.cannotDelete') : ''}>
              <Popconfirm
                title={t('browse.deleteCase')}
                description={t('browse.deleteConfirm')}
                onConfirm={() => handleDelete(record.patient_id)}
                okText={t('browse.delete')}
                cancelText={t('browse.cancel')}
                okButtonProps={{ danger: true }}
                disabled={isActive}
              >
                <Button
                  danger
                  size="small"
                  icon={<DeleteOutlined />}
                  loading={isDeleting}
                  disabled={isActive}
                >
                  {t('browse.delete')}
                </Button>
              </Popconfirm>
            </Tooltip>
          </Space>
        )
      },
    },
  ]

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <Spin size="large" tip={t('browse.loading')} />
      </div>
    )
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', padding: 24 }}>
      <Card style={{ flex: 1, display: 'flex', flexDirection: 'column' }} styles={{ body: { flex: 1, overflow: 'auto', padding: 0 } }}>
        <div style={{ padding: '16px 24px', borderBottom: '1px solid #f0f0f0' }}>
          <Title level={4} style={{ margin: 0 }}>
            <FolderOutlined style={{ marginRight: 8 }} />
            {t('browse.title')}
          </Title>
          <Text type="secondary">
            {t('browse.subtitle', { count: cases.length })}
          </Text>
        </div>
        {cases.length === 0 ? (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={t('browse.noCases')}
            style={{ margin: 'auto' }}
          >
            <Text type="secondary">
              {t('browse.noCasesDesc')}
            </Text>
          </Empty>
        ) : (
          <Table
            columns={columns}
            dataSource={cases}
            rowKey="patient_id"
            pagination={{ pageSize: 20, showSizeChanger: true, showTotal: (total) => t('browse.totalCases', { count: total }) }}
            scroll={{ x: 1100 }}
            size="small"
          />
        )}
      </Card>
    </div>
  )
}

export default BrowseCases
