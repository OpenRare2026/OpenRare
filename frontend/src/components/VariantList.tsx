import React, { useState, useEffect } from 'react'
import {
  Table,
  Input,
  Select,
  Tag,
  Space,
  Button,
  Tooltip,
  Badge,
  Typography,
  Row,
  Col,
  Drawer,
  Form,
  InputNumber,
  Collapse,
  Divider,
} from 'antd'
import {
  SearchOutlined,
  FilterOutlined,
  ExportOutlined,
  ReloadOutlined,
  CloseOutlined,
} from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import type { ColumnsType, TablePaginationConfig } from 'antd/es/table'
import type { FilterValue, SorterResult } from 'antd/es/table/interface'
import type { Variant } from '@/types'
import api from '@/services/api'

const { Text } = Typography
const { Option } = Select
const { Panel } = Collapse

interface VariantListProps {
  vcfFileId: string
  onVariantSelect: (variant: Variant) => void
  initialGeneFilter?: string
}

const VariantList: React.FC<VariantListProps> = ({ vcfFileId, onVariantSelect, initialGeneFilter }) => {
  const { t } = useTranslation()
  const [variants, setVariants] = useState<Variant[]>([])
  const [loading, setLoading] = useState(false)
  const [pagination, setPagination] = useState({ current: 1, pageSize: 50, total: 0 })
  const [filters, setFilters] = useState<Record<string, string | number | undefined>>(() =>
    initialGeneFilter ? { gene: initialGeneFilter } : {}
  )
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
  const [filterDrawerVisible, setFilterDrawerVisible] = useState(false)
  const [geneSearch, setGeneSearch] = useState<string>(() => initialGeneFilter || '')

  useEffect(() => {
    fetchVariants()
  }, [vcfFileId, pagination.current, pagination.pageSize])

  useEffect(() => {
    if (Object.keys(filters).length > 0 || geneSearch === '') {
      setPagination(prev => ({ ...prev, current: 1 }))
      fetchVariants()
    }
  }, [filters])

  const fetchVariants = async () => {
    setLoading(true)
    try {
      const apiFilters: Record<string, string | undefined> = {}
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          apiFilters[key] = String(value)
        }
      })
      const response = await api.getVariants(vcfFileId, apiFilters, {
        page: pagination.current,
        page_size: pagination.pageSize,
      })
      setVariants(response.items)
      setPagination((prev) => ({ ...prev, total: response.total }))
    } catch (error) {
      console.error('Failed to fetch variants:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleTableChange = (
    newPagination: TablePaginationConfig,
    _filters: Record<string, FilterValue | null>,
    _sorter: SorterResult<Variant> | SorterResult<Variant>[]
  ) => {
    setPagination((prev) => ({
      ...prev,
      current: newPagination.current || 1,
      pageSize: newPagination.pageSize || 50,
    }))
  }

  const handlePageChange = (page: number, pageSize?: number) => {
    setPagination((prev) => ({
      ...prev,
      current: page,
      pageSize: pageSize || prev.pageSize,
    }))
  }

  const columns: ColumnsType<Variant> = [
    {
      title: 'Chrom',
      dataIndex: 'chromosome',
      key: 'chromosome',
      width: 70,
      fixed: 'left',
      sorter: (a, b) => {
        const chrA = a.chromosome?.replace('chr', '') || ''
        const chrB = b.chromosome?.replace('chr', '') || ''
        const numA = parseInt(chrA, 10) || (chrA === 'X' ? 23 : chrA === 'Y' ? 24 : chrA === 'M' ? 25 : 99)
        const numB = parseInt(chrB, 10) || (chrB === 'X' ? 23 : chrB === 'Y' ? 24 : chrB === 'M' ? 25 : 99)
        return numA - numB
      },
      render: (chr: string) => <Text code>{chr}</Text>,
    },
    {
      title: 'Pos',
      dataIndex: 'position',
      key: 'position',
      width: 100,
      fixed: 'left',
      sorter: (a, b) => (a.position || 0) - (b.position || 0),
      render: (pos: number) => pos?.toLocaleString() ?? '-',
    },
    {
      title: 'Ref',
      dataIndex: 'ref',
      key: 'ref',
      width: 70,
      sorter: (a, b) => (a.ref || '').localeCompare(b.ref || ''),
      render: (ref: string) => (
        <Tooltip title={ref}>
          <Text code>{ref?.length > 8 ? `${ref.slice(0, 5)}...` : ref}</Text>
        </Tooltip>
      ),
    },
    {
      title: 'Alt',
      dataIndex: 'alt',
      key: 'alt',
      width: 70,
      sorter: (a, b) => (a.alt || '').localeCompare(b.alt || ''),
      render: (alt: string) => (
        <Tooltip title={alt}>
          <Text code>{alt?.length > 8 ? `${alt.slice(0, 5)}...` : alt}</Text>
        </Tooltip>
      ),
    },
    {
      title: 'Gene',
      dataIndex: 'gene',
      key: 'gene',
      width: 80,
      sorter: (a, b) => (a.gene || '').localeCompare(b.gene || ''),
      render: (gene: string) => (
        <Text strong style={{ color: '#1890ff' }}>{gene || '-'}</Text>
      ),
    },
    {
      title: 'All Genes',
      dataIndex: 'all_genes',
      key: 'all_genes',
      width: 120,
      ellipsis: true,
      sorter: (a, b) => (a.all_genes || '').localeCompare(b.all_genes || ''),
      render: (genes: string) => (
        <Tooltip title={genes}>
          <Text style={{ fontSize: 12 }}>{genes || '-'}</Text>
        </Tooltip>
      ),
    },
    {
      title: 'Transcript',
      dataIndex: 'transcript',
      key: 'transcript',
      width: 120,
      ellipsis: true,
      sorter: (a, b) => (a.transcript || '').localeCompare(b.transcript || ''),
      render: (t: string) => (
        <Tooltip title={t}>
          <Text code style={{ fontSize: 11 }}>{t || '-'}</Text>
        </Tooltip>
      ),
    },
    {
      title: 'Consequence',
      dataIndex: 'consequence',
      key: 'consequence',
      width: 140,
      ellipsis: true,
      sorter: (a, b) => (a.consequence || '').localeCompare(b.consequence || ''),
      render: (c: string) => (
        <Tooltip title={c}>
          <Text style={{ fontSize: 12 }}>{c?.replace(/_/g, ' ') || '-'}</Text>
        </Tooltip>
      ),
    },
    {
      title: 'Impact',
      dataIndex: 'impact',
      key: 'impact',
      width: 80,
      sorter: (a, b) => {
        const order: Record<string, number> = { HIGH: 1, MODERATE: 2, LOW: 3, MODIFIER: 4 }
        return (order[a.impact || ''] || 99) - (order[b.impact || ''] || 99)
      },
      render: (impact: string) =>
        impact ? (
          <Tag color={impact === 'HIGH' ? 'red' : impact === 'MODERATE' ? 'orange' : impact === 'LOW' ? 'blue' : 'default'}>
            {impact}
          </Tag>
        ) : (
          <Text type="secondary">-</Text>
        ),
    },
    {
      title: 'HGVSc',
      dataIndex: 'hgvs_c',
      key: 'hgvs_c',
      width: 120,
      ellipsis: true,
      sorter: (a, b) => (a.hgvs_c || '').localeCompare(b.hgvs_c || ''),
      render: (h: string) => (
        <Tooltip title={h}>
          <Text code style={{ fontSize: 11 }}>{h || '-'}</Text>
        </Tooltip>
      ),
    },
    {
      title: 'HGVSp',
      dataIndex: 'hgvs_p',
      key: 'hgvs_p',
      width: 120,
      ellipsis: true,
      sorter: (a, b) => (a.hgvs_p || '').localeCompare(b.hgvs_p || ''),
      render: (h: string) => (
        <Tooltip title={h}>
          <Text code style={{ fontSize: 11 }}>{h || '-'}</Text>
        </Tooltip>
      ),
    },
    {
      title: 'cDNA Pos',
      dataIndex: 'cdna_position',
      key: 'cdna_position',
      width: 80,
      sorter: (a, b) => (parseInt(a.cdna_position || '0', 10)) - (parseInt(b.cdna_position || '0', 10)),
      render: (v: string) => v || <Text type="secondary">-</Text>,
    },
    {
      title: 'CDS Pos',
      dataIndex: 'cds_position',
      key: 'cds_position',
      width: 80,
      sorter: (a, b) => (parseInt(a.cds_position || '0', 10)) - (parseInt(b.cds_position || '0', 10)),
      render: (v: string) => v || <Text type="secondary">-</Text>,
    },
    {
      title: 'Prot Pos',
      dataIndex: 'protein_position',
      key: 'protein_position',
      width: 80,
      sorter: (a, b) => (parseInt(a.protein_position || '0', 10)) - (parseInt(b.protein_position || '0', 10)),
      render: (v: string) => v || <Text type="secondary">-</Text>,
    },
    {
      title: 'AA',
      dataIndex: 'amino_acids',
      key: 'amino_acids',
      width: 70,
      sorter: (a, b) => (a.amino_acids || '').localeCompare(b.amino_acids || ''),
      render: (v: string) => v || <Text type="secondary">-</Text>,
    },
    {
      title: 'Codons',
      dataIndex: 'codons',
      key: 'codons',
      width: 80,
      sorter: (a, b) => (a.codons || '').localeCompare(b.codons || ''),
      render: (v: string) => v || <Text type="secondary">-</Text>,
    },
    {
      title: 'Exon',
      dataIndex: 'exon',
      key: 'exon',
      width: 60,
      sorter: (a, b) => (parseInt(a.exon || '0', 10)) - (parseInt(b.exon || '0', 10)),
      render: (v: string) => v || <Text type="secondary">-</Text>,
    },
    {
      title: 'Intron',
      dataIndex: 'intron',
      key: 'intron',
      width: 60,
      sorter: (a, b) => (parseInt(a.intron || '0', 10)) - (parseInt(b.intron || '0', 10)),
      render: (v: string) => v || <Text type="secondary">-</Text>,
    },
    {
      title: 'Strand',
      dataIndex: 'strand',
      key: 'strand',
      width: 60,
      sorter: (a, b) => (a.strand || '').localeCompare(b.strand || ''),
      render: (v: string) => v || <Text type="secondary">-</Text>,
    },
    {
      title: 'Protein Domains',
      dataIndex: 'protein_domains',
      key: 'protein_domains',
      width: 120,
      ellipsis: true,
      sorter: (a, b) => (a.protein_domains || '').localeCompare(b.protein_domains || ''),
      render: (v: string) => (
        <Tooltip title={v}>
          <Text style={{ fontSize: 12 }}>{v || '-'}</Text>
        </Tooltip>
      ),
    },
    {
      title: 'REVEL',
      dataIndex: 'revel_score',
      key: 'revel_score',
      width: 70,
      sorter: (a, b) => (a.revel_score || 0) - (b.revel_score || 0),
      render: (v: number) =>
        v != null ? (
          <Text style={{ color: v >= 0.5 ? '#f5222d' : undefined }}>{v.toFixed(3)}</Text>
        ) : (
          <Text type="secondary">-</Text>
        ),
    },
    {
      title: 'CADD',
      dataIndex: 'cadd',
      key: 'cadd',
      width: 70,
      sorter: (a, b) => (a.cadd || 0) - (b.cadd || 0),
      render: (v: number) =>
        v != null ? (
          <Text style={{ color: v >= 20 ? '#f5222d' : undefined }}>{v.toFixed(1)}</Text>
        ) : (
          <Text type="secondary">-</Text>
        ),
    },
    {
      title: 'gnomAD PopMax',
      dataIndex: 'gnomad_popmax_af',
      key: 'gnomad_popmax_af',
      width: 110,
      sorter: (a, b) => (a.gnomad_popmax_af || 0) - (b.gnomad_popmax_af || 0),
      render: (v: number) =>
        v != null ? (
          <Text style={{ color: v > 0.01 ? '#faad14' : undefined }}>{(v * 100).toFixed(3)}%</Text>
        ) : (
          <Text type="secondary">-</Text>
        ),
    },
    {
      title: 'gnomAD EAS',
      dataIndex: 'gnomad_eas_af',
      key: 'gnomad_eas_af',
      width: 100,
      sorter: (a, b) => (a.gnomad_eas_af || 0) - (b.gnomad_eas_af || 0),
      render: (v: number) =>
        v != null ? (
          <Text style={{ color: v > 0.01 ? '#faad14' : undefined }}>{(v * 100).toFixed(3)}%</Text>
        ) : (
          <Text type="secondary">-</Text>
        ),
    },
    {
      title: 'gnomAD nhomalt',
      dataIndex: 'gnomad_nhomalt',
      key: 'gnomad_nhomalt',
      width: 110,
      sorter: (a, b) => (a.gnomad_nhomalt || 0) - (b.gnomad_nhomalt || 0),
      render: (v: number) =>
        v != null ? v.toLocaleString() : <Text type="secondary">-</Text>,
    },
    {
      title: 'SpliceAI',
      dataIndex: 'spliceai_ds_max',
      key: 'spliceai_ds_max',
      width: 70,
      sorter: (a, b) => (a.spliceai_ds_max || 0) - (b.spliceai_ds_max || 0),
      render: (v: number) =>
        v != null ? (
          <Text style={{ color: v >= 0.5 ? '#f5222d' : undefined }}>{v.toFixed(3)}</Text>
        ) : (
          <Text type="secondary">-</Text>
        ),
    },
    {
      title: 'SpliceAI Type',
      dataIndex: 'spliceai_type',
      key: 'spliceai_type',
      width: 90,
      sorter: (a, b) => (a.spliceai_type || '').localeCompare(b.spliceai_type || ''),
      render: (v: string) => v || <Text type="secondary">-</Text>,
    },
    {
      title: 'LOFTEE',
      dataIndex: 'loftee_lof_flag',
      key: 'loftee_lof_flag',
      width: 80,
      sorter: (a, b) => (a.loftee_lof_flag || '').localeCompare(b.loftee_lof_flag || ''),
      render: (v: string) =>
        v ? (
          <Tag color={v === 'HC' ? 'red' : v === 'LC' ? 'orange' : 'default'}>{v}</Tag>
        ) : (
          <Text type="secondary">-</Text>
        ),
    },
    {
      title: 'LOF Filter',
      dataIndex: 'loftee_lof_filter',
      key: 'loftee_lof_filter',
      width: 100,
      ellipsis: true,
      sorter: (a, b) => (a.loftee_lof_filter || '').localeCompare(b.loftee_lof_filter || ''),
      render: (v: string) => v || <Text type="secondary">-</Text>,
    },
    {
      title: 'ClinVar',
      dataIndex: 'clinvar_significance',
      key: 'clinvar',
      width: 110,
      sorter: (a, b) => (a.clinvar_significance || '').localeCompare(b.clinvar_significance || ''),
      render: (sig: string) =>
        sig ? (
          <Tag color={
            sig.includes('Pathogenic') && !sig.includes('Likely') ? 'red' :
            sig.includes('Likely pathogenic') || sig.includes('Likely Pathogenic') ? 'orange' :
            sig.includes('Benign') && !sig.includes('Likely') ? 'cyan' :
            sig.includes('Likely benign') || sig.includes('Likely Benign') ? 'green' :
            'default'
          }>
            {sig}
          </Tag>
        ) : (
          <Text type="secondary">-</Text>
        ),
    },
    {
      title: 'ClinVar Rev',
      dataIndex: 'clinvar_review_status',
      key: 'clinvar_review',
      width: 100,
      ellipsis: true,
      sorter: (a, b) => (a.clinvar_review_status || '').localeCompare(b.clinvar_review_status || ''),
      render: (v: string) => (
        <Tooltip title={v}>
          <Text style={{ fontSize: 12 }}>{v || '-'}</Text>
        </Tooltip>
      ),
    },
    {
      title: 'ClinVar ★',
      dataIndex: 'clinvar_star_rating',
      key: 'clinvar_star',
      width: 80,
      sorter: (a, b) => (a.clinvar_star_rating || 0) - (b.clinvar_star_rating || 0),
      render: (v: number) =>
        v != null ? (
          <Text>{'★'.repeat(v)}{'☆'.repeat(Math.max(0, 4 - v))}</Text>
        ) : (
          <Text type="secondary">-</Text>
        ),
    },
    {
      title: 'Pathogenic Rank',
      dataIndex: 'pathogenic_rank',
      key: 'pathogenic_rank',
      width: 120,
      defaultSortOrder: 'ascend',
      sorter: (a, b) => (a.pathogenic_rank || 999) - (b.pathogenic_rank || 999),
      render: (v: number | null) => v != null ? v : <Text type="secondary">-</Text>,
    },
    {
      title: 'Evidence Summary',
      dataIndex: 'evidence_summary',
      key: 'evidence_summary',
      width: 200,
      ellipsis: true,
      sorter: (a, b) => (a.evidence_summary || '').localeCompare(b.evidence_summary || ''),
      render: (v: string) => (
        <Tooltip title={v}>
          <Text style={{ fontSize: 12 }}>{v || '-'}</Text>
        </Tooltip>
      ),
    },
    {
      title: 'SIFT',
      dataIndex: 'sift',
      key: 'sift',
      width: 100,
      ellipsis: true,
      sorter: (a, b) => (a.sift || '').localeCompare(b.sift || ''),
      render: (v: string) => v || <Text type="secondary">-</Text>,
    },
    {
      title: 'PolyPhen',
      dataIndex: 'polyphen',
      key: 'polyphen',
      width: 100,
      ellipsis: true,
      sorter: (a, b) => (a.polyphen || '').localeCompare(b.polyphen || ''),
      render: (v: string) => v || <Text type="secondary">-</Text>,
    },
    {
      title: 'VEP',
      dataIndex: 'vep_annotated',
      key: 'vep_annotated',
      width: 50,
      sorter: (a, b) => (a.vep_annotated ? 1 : 0) - (b.vep_annotated ? 1 : 0),
      render: (vep: boolean) =>
        vep ? <Tag color="green" style={{ fontSize: 10 }}>VEP</Tag> : null,
    },
    {
      title: t('variantList.colAction'),
      key: 'action',
      width: 70,
      fixed: 'right',
      render: (_, record) => (
        <Button type="link" size="small" onClick={() => onVariantSelect(record)}>
          {t('variantList.details')}
        </Button>
      ),
    },
  ]

  const handleSearchGene = (value: string) => {
    setGeneSearch(value)
    setFilters((prev) => ({ ...prev, gene: value || undefined }))
  }

  const handleFilterChange = (key: string, value: string | number | undefined) => {
    setFilters((prev) => ({ ...prev, [key]: value }))
  }

  const clearAllFilters = () => {
    setFilters({})
    setGeneSearch('')
    setPagination((prev) => ({ ...prev, current: 1 }))
  }

  const activeFilterCount = Object.values(filters).filter(v => v !== undefined && v !== '').length

  const pageSizeOptions = [20, 50, 100, 200]

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
              <Button icon={<ReloadOutlined />} onClick={fetchVariants} size="small">
                {t('variantList.refresh')}
              </Button>
              <Button icon={<ExportOutlined />} size="small">{t('variantList.export')}</Button>
            </Space>
          </Col>
        </Row>
      </div>

      <div style={{ padding: '12px 16px', background: '#fafafa', flexShrink: 0 }}>
        <Row gutter={12} align="middle">
          <Col span={4}>
            <Input
              placeholder="Search gene..."
              prefix={<SearchOutlined />}
              allowClear
              size="small"
              value={geneSearch}
              onChange={(e) => handleSearchGene(e.target.value)}
            />
          </Col>
          <Col span={3}>
            <Select
              placeholder="Chromosome"
              allowClear
              size="small"
              style={{ width: '100%' }}
              value={filters.chromosome as string}
              onChange={(value) => handleFilterChange('chromosome', value)}
            >
              {Array.from({ length: 22 }, (_, i) => (
                <Option key={i + 1} value={`chr${i + 1}`}>chr{i + 1}</Option>
              ))}
              <Option value="chrX">chrX</Option>
              <Option value="chrY">chrY</Option>
              <Option value="chrM">chrM</Option>
            </Select>
          </Col>
          <Col span={3}>
            <Select
              placeholder="Impact"
              allowClear
              size="small"
              style={{ width: '100%' }}
              value={filters.impact as string}
              onChange={(value) => handleFilterChange('impact', value)}
            >
              <Option value="HIGH">HIGH</Option>
              <Option value="MODERATE">MODERATE</Option>
              <Option value="LOW">LOW</Option>
              <Option value="MODIFIER">MODIFIER</Option>
            </Select>
          </Col>
          <Col span={3}>
            <Select
              placeholder="ClinVar"
              allowClear
              size="small"
              style={{ width: '100%' }}
              value={filters.clinvar_significance as string}
              onChange={(value) => handleFilterChange('clinvar_significance', value)}
            >
              <Option value="Pathogenic">Pathogenic</Option>
              <Option value="Likely pathogenic">Likely pathogenic</Option>
              <Option value="Uncertain significance">Uncertain significance</Option>
              <Option value="Likely benign">Likely benign</Option>
              <Option value="Benign">Benign</Option>
            </Select>
          </Col>
          <Col span={3}>
            <Select
              placeholder="LOFTEE"
              allowClear
              size="small"
              style={{ width: '100%' }}
              value={filters.loftee_lof_flag as string}
              onChange={(value) => handleFilterChange('loftee_lof_flag', value)}
            >
              <Option value="HC">HC (High Confidence)</Option>
              <Option value="LC">LC (Low Confidence)</Option>
            </Select>
          </Col>
          <Col span={2}>
            <Button 
              icon={<FilterOutlined />} 
              size="small"
              onClick={() => setFilterDrawerVisible(true)}
            >
              More {activeFilterCount > 0 && <Badge count={activeFilterCount} style={{ marginLeft: 4 }} />}
            </Button>
          </Col>
          <Col span={2}>
            <Button 
              icon={<CloseOutlined />} 
              size="small"
              onClick={clearAllFilters}
              disabled={activeFilterCount === 0}
            >
              Clear
            </Button>
          </Col>
          <Col span={4} style={{ textAlign: 'right' }}>
            <Space>
              <Text type="secondary">Page:</Text>
              <Select
                value={pagination.current}
                onChange={(page) => handlePageChange(page)}
                size="small"
                style={{ width: 70 }}
              >
                {Array.from({ length: Math.min(20, Math.ceil(pagination.total / pagination.pageSize)) }, (_, i) => (
                  <Option key={i + 1} value={i + 1}>{i + 1}</Option>
                ))}
              </Select>
              <Text type="secondary">of {Math.ceil(pagination.total / pagination.pageSize)}</Text>
            </Space>
          </Col>
        </Row>
      </div>

      <div style={{ flex: 1, overflow: 'hidden' }}>
        <Table
          columns={columns}
          dataSource={variants}
          rowKey="id"
          loading={loading}
          pagination={false}
          onChange={handleTableChange}
          scroll={{ x: 4200, y: 'calc(100vh - 220px)' }}
          size="small"
          rowSelection={{
            selectedRowKeys,
            onChange: setSelectedRowKeys,
          }}
          onRow={(record) => ({
            onClick: () => onVariantSelect(record),
            style: { cursor: 'pointer' },
          })}
        />
      </div>

      <div style={{ padding: '12px 16px', borderTop: '1px solid #f0f0f0', background: '#fff', flexShrink: 0 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <Text type="secondary">Show:</Text>
              <Select
                value={pagination.pageSize}
                onChange={(size) => handlePageChange(1, size)}
                size="small"
                style={{ width: 90 }}
              >
                {pageSizeOptions.map(size => (
                  <Option key={size} value={size}>{size} / page</Option>
                ))}
              </Select>
              <Text type="secondary">Total: {pagination.total.toLocaleString()}</Text>
            </Space>
          </Col>
          <Col>
            <Space>
              <Button
                size="small"
                disabled={pagination.current === 1}
                onClick={() => handlePageChange(1)}
              >
                First
              </Button>
              <Button
                size="small"
                disabled={pagination.current === 1}
                onClick={() => handlePageChange(pagination.current - 1)}
              >
                Prev
              </Button>
              <InputNumber
                min={1}
                max={Math.ceil(pagination.total / pagination.pageSize)}
                value={pagination.current}
                onChange={(value) => value && handlePageChange(value)}
                size="small"
                style={{ width: 60 }}
              />
              <Button
                size="small"
                disabled={pagination.current >= Math.ceil(pagination.total / pagination.pageSize)}
                onClick={() => handlePageChange(pagination.current + 1)}
              >
                Next
              </Button>
              <Button
                size="small"
                disabled={pagination.current >= Math.ceil(pagination.total / pagination.pageSize)}
                onClick={() => handlePageChange(Math.ceil(pagination.total / pagination.pageSize))}
              >
                Last
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      <Drawer
        title="Advanced Filters"
        placement="right"
        width={400}
        onClose={() => setFilterDrawerVisible(false)}
        open={filterDrawerVisible}
      >
        <Form layout="vertical" size="small">
          <Collapse defaultActiveKey={['position', 'frequency', 'annotation', 'clinical']}>
            <Panel header="Position" key="position">
              <Row gutter={12}>
                <Col span={12}>
                  <Form.Item label="Position Min">
                    <InputNumber
                      style={{ width: '100%' }}
                      placeholder="Min"
                      value={filters.position_min as number}
                      onChange={(v) => handleFilterChange('position_min', v ?? undefined)}
                    />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item label="Position Max">
                    <InputNumber
                      style={{ width: '100%' }}
                      placeholder="Max"
                      value={filters.position_max as number}
                      onChange={(v) => handleFilterChange('position_max', v ?? undefined)}
                    />
                  </Form.Item>
                </Col>
              </Row>
            </Panel>

            <Panel header="Population Frequency" key="frequency">
              <Form.Item label="gnomAD PopMax AF (max)">
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="e.g. 0.01"
                  min={0}
                  max={1}
                  step={0.001}
                  value={filters.gnomad_popmax_af_max as number}
                  onChange={(v) => handleFilterChange('gnomad_popmax_af_max', v ?? undefined)}
                />
              </Form.Item>
              <Form.Item label="gnomAD EAS AF (max)">
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="e.g. 0.01"
                  min={0}
                  max={1}
                  step={0.001}
                  value={filters.gnomad_eas_af_max as number}
                  onChange={(v) => handleFilterChange('gnomad_eas_af_max', v ?? undefined)}
                />
              </Form.Item>
            </Panel>

            <Panel header="Annotation" key="annotation">
              <Form.Item label="Consequence">
                <Select
                  placeholder="Select consequence"
                  allowClear
                  style={{ width: '100%' }}
                  value={filters.consequence as string}
                  onChange={(v) => handleFilterChange('consequence', v)}
                >
                  <Option value="missense_variant">missense_variant</Option>
                  <Option value="synonymous_variant">synonymous_variant</Option>
                  <Option value="stop_gained">stop_gained</Option>
                  <Option value="frameshift_variant">frameshift_variant</Option>
                  <Option value="splice_acceptor_variant">splice_acceptor_variant</Option>
                  <Option value="splice_donor_variant">splice_donor_variant</Option>
                  <Option value="intron_variant">intron_variant</Option>
                  <Option value="upstream_gene_variant">upstream_gene_variant</Option>
                  <Option value="downstream_gene_variant">downstream_gene_variant</Option>
                </Select>
              </Form.Item>
              <Form.Item label="REVEL Score (min)">
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="e.g. 0.5"
                  min={0}
                  max={1}
                  step={0.01}
                  value={filters.revel_score_min as number}
                  onChange={(v) => handleFilterChange('revel_score_min', v ?? undefined)}
                />
              </Form.Item>
              <Form.Item label="CADD Score (min)">
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="e.g. 20"
                  min={0}
                  max={100}
                  step={1}
                  value={filters.cadd_min as number}
                  onChange={(v) => handleFilterChange('cadd_min', v ?? undefined)}
                />
              </Form.Item>
              <Form.Item label="SpliceAI Score (min)">
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="e.g. 0.5"
                  min={0}
                  max={1}
                  step={0.01}
                  value={filters.spliceai_ds_max_min as number}
                  onChange={(v) => handleFilterChange('spliceai_ds_max_min', v ?? undefined)}
                />
              </Form.Item>
              <Form.Item label="VEP Annotated">
                <Select
                  placeholder="Any"
                  allowClear
                  style={{ width: '100%' }}
                  value={filters.vep_annotated as string}
                  onChange={(v) => handleFilterChange('vep_annotated', v)}
                >
                  <Option value="true">Yes</Option>
                  <Option value="false">No</Option>
                </Select>
              </Form.Item>
            </Panel>

            <Panel header="Clinical" key="clinical">
              <Form.Item label="ClinVar Significance">
                <Select
                  placeholder="Select"
                  allowClear
                  style={{ width: '100%' }}
                  value={filters.clinvar_significance as string}
                  onChange={(v) => handleFilterChange('clinvar_significance', v)}
                >
                  <Option value="Pathogenic">Pathogenic</Option>
                  <Option value="Likely pathogenic">Likely pathogenic</Option>
                  <Option value="Uncertain significance">Uncertain significance</Option>
                  <Option value="Likely benign">Likely benign</Option>
                  <Option value="Benign">Benign</Option>
                </Select>
              </Form.Item>
              <Form.Item label="ClinVar Stars (min)">
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  max={4}
                  step={1}
                  value={filters.clinvar_star_rating_min as number}
                  onChange={(v) => handleFilterChange('clinvar_star_rating_min', v ?? undefined)}
                />
              </Form.Item>
              <Form.Item label="Pathogenic Rank">
                <Select
                  placeholder="Select"
                  allowClear
                  style={{ width: '100%' }}
                  value={filters.pathogenic_rank as string}
                  onChange={(v) => handleFilterChange('pathogenic_rank', v)}
                >
                  <Option value="High">High</Option>
                  <Option value="Medium">Medium</Option>
                  <Option value="Low">Low</Option>
                </Select>
              </Form.Item>
            </Panel>
          </Collapse>

          <Divider />

          <Space style={{ width: '100%' }} direction="vertical">
            <Button type="primary" block onClick={() => setFilterDrawerVisible(false)}>
              Apply Filters
            </Button>
            <Button block onClick={clearAllFilters}>
              Clear All Filters
            </Button>
          </Space>
        </Form>
      </Drawer>
    </div>
  )
}

export default VariantList
