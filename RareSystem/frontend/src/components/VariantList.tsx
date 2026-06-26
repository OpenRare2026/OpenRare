import React, { useState, useEffect, useMemo } from 'react'
import {
  Table,
  Input,
  Button,
  Space,
  Tooltip,
  Badge,
  Typography,
  Row,
  Col,
  Empty,
} from 'antd'
import {
  SearchOutlined,
  ReloadOutlined,
  ExportOutlined,
} from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import type { ColumnsType } from 'antd/es/table'
import api from '@/services/api'
import type { DynamicVariantListResponse } from '@/types'

const { Text } = Typography

interface VariantListProps {
  vcfFileId: string
  onVariantSelect: (variant: Record<string, string>, rowIndex: number) => void
  initialGeneFilter?: string
}

const VariantList: React.FC<VariantListProps> = ({ vcfFileId, onVariantSelect, initialGeneFilter }) => {
  const { t } = useTranslation()
  const [variants, setVariants] = useState<Record<string, string>[]>([])
  const [columns, setColumns] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [pagination, setPagination] = useState({ current: 1, pageSize: 50, total: 0 })
  const [searchText, setSearchText] = useState('')
  const [vepMessage, setVepMessage] = useState('')

  useEffect(() => {
    fetchVariants()
  }, [vcfFileId, pagination.current, pagination.pageSize])

  useEffect(() => {
    if (initialGeneFilter) {
      setSearchText(initialGeneFilter)
      handleSearch(initialGeneFilter)
    }
  }, [initialGeneFilter])

  const fetchVariants = async () => {
    setLoading(true)
    try {
      const response: DynamicVariantListResponse = await api.getVariants(
        vcfFileId,
        pagination.current,
        pagination.pageSize,
        searchText || undefined,
      )
      setVariants(response.items)
      setColumns(response.columns)
      setPagination(prev => ({ ...prev, total: response.total }))
      setVepMessage(response.message)
    } catch (error) {
      console.error('Failed to fetch variants:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (_value?: string) => {
    setPagination(prev => ({ ...prev, current: 1 }))
  }

  const handleSearchSubmit = () => {
    setPagination(prev => ({ ...prev, current: 1 }))
    fetchVariants()
  }

  const handlePageChange = (page: number, pageSize?: number) => {
    setPagination(prev => ({
      ...prev,
      current: page,
      pageSize: pageSize || prev.pageSize,
    }))
  }

  // Build dynamic table columns from VEP Parquet schema
  const tableColumns: ColumnsType<Record<string, string>> = useMemo(() => {
    if (columns.length === 0) return []

    const getWidth = (col: string): number => {
      const w: Record<string, number> = {
        '#Uploaded variation': 160,
        'Uploaded_variation': 160,
        'Location': 100,
        'Allele': 70,
        'Gene': 90,
        'gene_symbol': 90,
        'Consequence': 200,
        'IMPACT': 80,
        'Feature': 120,
        'HGVSc': 140,
        'HGVSp': 140,
        'CLINVAR_CLNSIG': 120,
        'clinvar_significance': 120,
        'REVEL_score': 80,
        'CADD_phred': 80,
        'gnomAD_popmax_AF': 110,
        'gnomAD_eas_AF': 100,
        'pathogenic_rank': 100,
        'evidence_summary': 200,
        'SPLICEAI_DS_MAX': 80,
        'LoF_info': 100,
        'loftee_lof_flag': 80,
      }
      return w[col] || 120
    }

    const isFixed = (col: string): boolean => {
      return ['#Uploaded variation', 'Uploaded_variation', 'Location', 'Allele', 'Gene', 'gene_symbol'].includes(col)
    }

    return columns.map((col, idx) => ({
      title: col,
      dataIndex: col,
      key: col,
      width: getWidth(col),
      fixed: isFixed(col) && idx < 2 ? ('left' as const) : undefined,
      ellipsis: !isFixed(col),
      sorter: (a: Record<string, string>, b: Record<string, string>) => {
        const va = a[col] || ''
        const vb = b[col] || ''
        const na = parseFloat(va)
        const nb = parseFloat(vb)
        if (!isNaN(na) && !isNaN(nb)) return na - nb
        return va.localeCompare(vb)
      },
      render: (value: string) => {
        if (!value || value === '' || value === '-') {
          return <Text type="secondary">-</Text>
        }

        // IMPACT column styling
        if (col === 'IMPACT') {
          const color = value === 'HIGH' ? 'red' : value === 'MODERATE' ? 'orange' : value === 'LOW' ? 'blue' : 'default'
          return <span style={{ color, fontWeight: 500 }}>{value}</span>
        }

        // ClinVar styling
        if (col === 'CLINVAR_CLNSIG' || col === 'clinvar_significance') {
          const v = value.toLowerCase()
          const color = v.includes('pathogenic') && !v.includes('likely') ? '#f5222d'
            : v.includes('likely pathogenic') ? '#fa8c16'
            : v.includes('benign') && !v.includes('likely') ? '#13c2c2'
            : v.includes('likely benign') ? '#52c41a'
            : undefined
          return <span style={{ color, fontWeight: color ? 500 : undefined }}>{value}</span>
        }

        // LoF flag styling
        if (col === 'loftee_lof_flag' || col === 'LoF_flags') {
          const color = value === 'HC' ? '#f5222d' : value === 'LC' ? '#fa8c16' : undefined
          return <span style={{ color, fontWeight: color ? 500 : undefined }}>{value}</span>
        }

        // Gene styling
        if (col === 'Gene' || col === 'gene_symbol') {
          return <Text strong style={{ color: '#1890ff' }}>{value}</Text>
        }

        // Long text truncation
        if (value.length > 30) {
          return (
            <Tooltip title={value}>
              <Text style={{ fontSize: 12 }}>{value.slice(0, 27)}...</Text>
            </Tooltip>
          )
        }

        return <Text style={{ fontSize: 12 }}>{value}</Text>
      },
    }))
  }, [columns])

  const handleTableChange = (newPagination: any) => {
    setPagination(prev => ({
      ...prev,
      current: newPagination.current || 1,
      pageSize: newPagination.pageSize || 50,
    }))
  }

  const pageSizeOptions = [20, 50, 100, 200]

  if (vepMessage && !loading && columns.length === 0) {
    return (
      <div style={{ padding: 24, textAlign: 'center' }}>
        <Empty description={vepMessage || 'VEP annotation pending or not yet available'} />
        <Button icon={<ReloadOutlined />} onClick={fetchVariants} style={{ marginTop: 16 }}>
          {t('variantList.refresh')}
        </Button>
      </div>
    )
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '12px 16px', borderBottom: '1px solid #f0f0f0', flexShrink: 0 }}>
        <Row gutter={16} align="middle">
          <Col flex="auto">
            <Space>
              <Text strong>{t('variantList.title')}</Text>
              <Badge count={pagination.total} style={{ backgroundColor: '#1890ff' }} />
            </Space>
          </Col>
          <Col>
            <Space>
              <Input
                placeholder="Search..."
                prefix={<SearchOutlined />}
                allowClear
                size="small"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                onPressEnter={handleSearchSubmit}
                style={{ width: 200 }}
              />
              <Button icon={<ReloadOutlined />} onClick={fetchVariants} size="small">
                {t('variantList.refresh')}
              </Button>
              <Button icon={<ExportOutlined />} size="small">{t('variantList.export')}</Button>
            </Space>
          </Col>
        </Row>
      </div>

      <div style={{ flex: 1, overflow: 'hidden' }}>
        <Table
          columns={tableColumns}
          dataSource={variants}
          rowKey={(_, index) => String(index)}
          loading={loading}
          pagination={false}
          onChange={handleTableChange}
          scroll={{ x: Math.max(columns.length * 120, 800), y: 'calc(100vh - 220px)' }}
          size="small"
          onRow={(record, index) => ({
            onClick: () => onVariantSelect(record, (pagination.current - 1) * pagination.pageSize + (index ?? 0)),
            style: { cursor: 'pointer' },
          })}
        />
      </div>

      <div style={{ padding: '12px 16px', borderTop: '1px solid #f0f0f0', background: '#fff', flexShrink: 0 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <Text type="secondary">Show:</Text>
              <select
                value={pagination.pageSize}
                onChange={(e) => handlePageChange(1, Number(e.target.value))}
                style={{ padding: '2px 8px', borderRadius: 4, border: '1px solid #d9d9d9' }}
              >
                {pageSizeOptions.map(size => (
                  <option key={size} value={size}>{size} / page</option>
                ))}
              </select>
              <Text type="secondary">Total: {pagination.total.toLocaleString()}</Text>
            </Space>
          </Col>
          <Col>
            <Space>
              <Button size="small" disabled={pagination.current === 1} onClick={() => handlePageChange(1)}>First</Button>
              <Button size="small" disabled={pagination.current === 1} onClick={() => handlePageChange(pagination.current - 1)}>Prev</Button>
              <Text>{pagination.current} / {Math.max(1, Math.ceil(pagination.total / pagination.pageSize))}</Text>
              <Button size="small" disabled={pagination.current >= Math.ceil(pagination.total / pagination.pageSize)} onClick={() => handlePageChange(pagination.current + 1)}>Next</Button>
              <Button size="small" disabled={pagination.current >= Math.ceil(pagination.total / pagination.pageSize)} onClick={() => handlePageChange(Math.ceil(pagination.total / pagination.pageSize))}>Last</Button>
            </Space>
          </Col>
        </Row>
      </div>
    </div>
  )
}

export default VariantList
