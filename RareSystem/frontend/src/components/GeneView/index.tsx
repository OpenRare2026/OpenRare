import React, { useState, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Table,
  Tag,
  Space,
  Button,
  Typography,
  Spin,
  Empty,
  Tooltip,
  Descriptions,
  Segmented,
  Pagination,
} from 'antd'
import {
  DownOutlined,
  RightOutlined,
  InfoCircleOutlined,
  ExperimentOutlined,
  ApiOutlined,
  FilePdfOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import api from '@/services/api'
import type { GeneSummary, GeneInfo, GeneVariant, Variant, GenePhenotypeScore, PpiGeneScore, GeneAnalysisReport, ReportMeta } from '@/types'
import ReportView from '@/components/ReportView'
import { useAppStore } from '@/store'

const { Text } = Typography

interface GeneViewProps {
  vcfFileId: string
  patientId: number
  onVariantSelect: (variant: GeneVariant | Variant) => void
  onGeneFilter: (gene: string) => void
}

const CLASSIFICATION_COLORS: Record<string, string> = {
  Pathogenic: 'red',
  'Likely Pathogenic': 'orange',
  VUS: 'default',
  'Likely Benign': 'green',
  Benign: 'cyan',
}

const VARIANT_TYPE_COLORS: Record<string, string> = {
  SNV: 'blue',
  INDEL: 'purple',
  STR: 'magenta',
  CNV: 'gold',
}

const CONCLUSION_CODE_COLORS: Record<string, string> = {
  PHENOTYPE_MATCH_STRONG: 'red',
  PHENOTYPE_MATCH_MODERATE: 'orange',
  PHENOTYPE_MATCH_WEAK: 'blue',
  PHENOTYPE_MATCH_NONE: 'default',
  NO_GENE_DISEASE_MODEL: 'default',
  NO_VALID_SCORING_HPO: 'default',
  NO_GENE_ANNOTATION: 'default',
}

const GeneView: React.FC<GeneViewProps> = ({ vcfFileId, patientId, onVariantSelect, onGeneFilter }) => {
  const { t } = useTranslation()
  const { addGeneAnalysisReport } = useAppStore()
  const [genes, setGenes] = useState<GeneSummary[]>([])
  const [loading, setLoading] = useState(false)
  const [expandedGene, setExpandedGene] = useState<string | null>(null)
  const [geneVariants, setGeneVariants] = useState<Record<string, GeneVariant[]>>({})
  const [geneInfo, setGeneInfo] = useState<Record<string, GeneInfo | null>>({})
  const [loadingVariants, setLoadingVariants] = useState<Record<string, boolean>>({})
  
  const [primaryHpoTerms, setPrimaryHpoTerms] = useState<string[]>([])
  const [hpoLoading, setHpoLoading] = useState(false)
  const [hpoJobStatus, setHpoJobStatus] = useState<string>('')
  const [hpoJobUid, setHpoJobUid] = useState<string | null>(null)
  const [hpoScores, setHpoScores] = useState<GenePhenotypeScore[]>([])
  
  const [ppiLoading, setPpiLoading] = useState(false)
  const [ppiJobStatus, setPpiJobStatus] = useState<string>('')
  const [ppiJobId, setPpiJobId] = useState<string | null>(null)
  const [ppiScores, setPpiScores] = useState<PpiGeneScore[]>([])
  
  const [viewMode, setViewMode] = useState<'genes' | 'hpo' | 'ppi'>('genes')
  
  const [reportModalVisible, setReportModalVisible] = useState(false)
  
  const [genePage, setGenePage] = useState(1)
  const [genePageSize, setGenePageSize] = useState(20)
  const [hpoPage, setHpoPage] = useState(1)
  const [hpoPageSize, setHpoPageSize] = useState(20)
  const [ppiPage, setPpiPage] = useState(1)
  const [ppiPageSize, setPpiPageSize] = useState(20)

  const HPO_CACHE_KEY = `hpo_scores_${vcfFileId}`
  const PPI_CACHE_KEY = `ppi_scores_${vcfFileId}`

  const handleReportGenerated = useCallback((report: { run_id: string; pdf_url: string; markdown: string; meta?: ReportMeta }) => {
    const newReport: GeneAnalysisReport = {
      id: report.run_id,
      run_id: report.run_id,
      pdf_url: report.pdf_url,
      markdown: report.markdown,
      meta: report.meta,
      created_at: new Date().toISOString(),
      vcf_file_id: parseInt(vcfFileId),
    }
    addGeneAnalysisReport(newReport)
  }, [vcfFileId, addGeneAnalysisReport])

  useEffect(() => {
    fetchGenes()
    fetchPrimaryHpoTerms()
    loadCachedHpoScores()
    loadCachedPpiScores()
  }, [vcfFileId, patientId])

  const loadCachedHpoScores = () => {
    try {
      const cached = localStorage.getItem(HPO_CACHE_KEY)
      if (cached) {
        const { scores, timestamp, hpoJobUid } = JSON.parse(cached)
        if (scores && timestamp && Date.now() - timestamp < 24 * 60 * 60 * 1000) {
          setHpoScores(scores)
          if (hpoJobUid) setHpoJobUid(hpoJobUid)
        }
      }
    } catch (error) {
      console.error('Failed to load cached HPO scores:', error)
    }
  }

  const saveHpoScoresToCache = (scores: GenePhenotypeScore[], uid: string) => {
    try {
      localStorage.setItem(HPO_CACHE_KEY, JSON.stringify({
        scores,
        timestamp: Date.now(),
        hpoJobUid: uid,
      }))
    } catch (error) {
      console.error('Failed to cache HPO scores:', error)
    }
  }

  const loadCachedPpiScores = () => {
    try {
      const cached = localStorage.getItem(PPI_CACHE_KEY)
      if (cached) {
        const { scores, timestamp } = JSON.parse(cached)
        if (scores && timestamp && Date.now() - timestamp < 24 * 60 * 60 * 1000) {
          setPpiScores(scores)
        }
      }
    } catch (error) {
      console.error('Failed to load cached PPI scores:', error)
    }
  }

  const savePpiScoresToCache = (scores: PpiGeneScore[]) => {
    try {
      localStorage.setItem(PPI_CACHE_KEY, JSON.stringify({
        scores,
        timestamp: Date.now(),
      }))
    } catch (error) {
      console.error('Failed to cache PPI scores:', error)
    }
  }

  const fetchGenes = async () => {
    setLoading(true)
    try {
      const response = await api.getGenes(vcfFileId)
      setGenes(response.genes || [])
    } catch (error) {
      console.error('Failed to fetch genes:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchPrimaryHpoTerms = async () => {
    try {
      const caseData = await api.getCase(patientId)
      const primary = caseData?.hpo_terms
        ?.filter((term: any) => term.display_category !== 'secondary')
        ?.map((term: any) => term.hpo_id) || []
      setPrimaryHpoTerms(primary)
    } catch (error) {
      console.error('Failed to fetch HPO terms:', error)
    }
  }

  const fetchGeneVariants = useCallback(async (geneName: string) => {
    if (geneVariants[geneName]) return
    
    setLoadingVariants(prev => ({ ...prev, [geneName]: true }))
    try {
      const response = await api.getGeneVariants(vcfFileId, geneName)
      setGeneVariants(prev => ({ ...prev, [geneName]: response.variants || [] }))
    } catch (error) {
      console.error('Failed to fetch gene variants:', error)
    } finally {
      setLoadingVariants(prev => ({ ...prev, [geneName]: false }))
    }
  }, [vcfFileId, geneVariants])

  const fetchGeneInfo = useCallback(async (geneName: string) => {
    if (geneInfo[geneName] !== undefined) return
    
    try {
      const info = await api.getGeneInfo(geneName)
      setGeneInfo(prev => ({ ...prev, [geneName]: info }))
    } catch (error) {
      console.error('Failed to fetch gene info:', error)
      setGeneInfo(prev => ({ ...prev, [geneName]: null }))
    }
  }, [geneInfo])

  const handleExpand = (geneName: string) => {
    const newExpanded = expandedGene === geneName ? null : geneName
    setExpandedGene(newExpanded)
    
    if (newExpanded) {
      fetchGeneVariants(geneName)
      fetchGeneInfo(geneName)
    }
  }

  const handleRunHpoScoring = async () => {
    if (primaryHpoTerms.length === 0) return
    
    setHpoLoading(true)
    setHpoJobStatus('submitting')
    
    try {
      const result = await api.submitPhenotypeHpoJob(parseInt(vcfFileId), primaryHpoTerms)
      setHpoJobUid(result.uid)
      setHpoJobStatus(result.status)
      
      pollHpoJobStatus(result.uid)
    } catch (error: any) {
      console.error('Failed to submit HPO job:', error)
      setHpoJobStatus('failed')
      setHpoLoading(false)
    }
  }

  const pollHpoJobStatus = async (uid: string) => {
    let attempts = 0
    const maxAttempts = 180
    
    const poll = async () => {
      try {
        const status = await api.getPhenotypeHpoJobStatus(uid)
        setHpoJobStatus(status.status)
        
        if (status.status === 'completion') {
          const results = await api.getPhenotypeHpoResults(uid)
          setHpoScores(results.scores)
          saveHpoScoresToCache(results.scores, uid)
          setViewMode('hpo')
          setHpoLoading(false)
          return
        }
        
        if (status.status === 'failure') {
          console.error('HPO job failed:', status.message)
          setHpoLoading(false)
          return
        }
        
        attempts++
        if (attempts < maxAttempts) {
          setTimeout(poll, 10000)
        } else {
          setHpoLoading(false)
        }
      } catch (error: any) {
        console.error('Poll error:', error)
        attempts++
        if (attempts < maxAttempts) {
          setTimeout(poll, 10000)
        } else {
          setHpoLoading(false)
        }
      }
    }
    
    poll()
  }

  const handleRunPpiScoring = async () => {
    if (!hpoJobUid) return
    
    setPpiLoading(true)
    setPpiJobStatus('submitting')
    
    try {
      const result = await api.submitPpiJob(parseInt(vcfFileId), hpoJobUid, primaryHpoTerms)
      setPpiJobId(result.job_id)
      setPpiJobStatus(result.status)
      
      pollPpiJobStatus(result.job_id)
    } catch (error: any) {
      console.error('Failed to submit PPI job:', error)
      setPpiJobStatus('failed')
      setPpiLoading(false)
    }
  }

  const pollPpiJobStatus = async (jobId: string) => {
    let attempts = 0
    const maxAttempts = 180
    
    const poll = async () => {
      try {
        const status = await api.getPpiJobStatus(jobId)
        setPpiJobStatus(status.status)
        
        if (status.status === 'completed' || status.status === 'done' || status.status === 'success') {
          const results = await api.getPpiResults(jobId)
          setPpiScores(results.scores)
          savePpiScoresToCache(results.scores)
          setViewMode('ppi')
          setPpiLoading(false)
          return
        }
        
        if (status.status === 'failed') {
          console.error('PPI job failed:', status.message)
          setPpiLoading(false)
          return
        }
        
        try {
          const results = await api.getPpiResults(jobId)
          if (results.scores && results.scores.length > 0) {
            setPpiScores(results.scores)
            savePpiScoresToCache(results.scores)
            setViewMode('ppi')
            setPpiLoading(false)
            return
          }
        } catch {
        }
        
        attempts++
        if (attempts < maxAttempts) {
          setTimeout(poll, 10000)
        } else {
          setPpiLoading(false)
        }
      } catch (error: any) {
        console.error('PPI poll error:', error)
        attempts++
        if (attempts < maxAttempts) {
          setTimeout(poll, 10000)
        } else {
          setPpiLoading(false)
        }
      }
    }
    
    poll()
  }

  const formatPosition = (chr: string, pos: number) => `${chr}:${pos.toLocaleString()}`
  
  const formatAF = (af: number | null | undefined) => {
    if (af === null || af === undefined) return '-'
    if (af === 0) return '0'
    if (af < 0.0001) return af.toExponential(2)
    return (af * 100).toFixed(4) + '%'
  }

  const renderTypes = (types: Record<string, number>) => {
    return Object.entries(types).map(([type, count]) => (
      <Tag key={type} color={VARIANT_TYPE_COLORS[type] || 'default'} style={{ marginBottom: 2 }}>
        {type}({count})
      </Tag>
    ))
  }

  const renderClassifications = (classifications: Record<string, number>) => {
    const entries = Object.entries(classifications)
    if (entries.length === 0) return <Text type="secondary">-</Text>
    
    return entries.map(([cls, count]) => (
      <Tag key={cls} color={CLASSIFICATION_COLORS[cls] || 'default'} style={{ marginBottom: 2 }}>
        {cls}({count})
      </Tag>
    ))
  }

  const renderGeneInfo = (geneName: string) => {
    const info = geneInfo[geneName]
    
    if (!info) {
      return (
        <div style={{ padding: '12px 16px', color: '#999' }}>
          <Text type="secondary">{t('geneView.loading')}</Text>
        </div>
      )
    }
    
    return (
      <div style={{ padding: '12px 16px', background: '#fafafa', borderBottom: '1px solid #f0f0f0' }}>
        <Descriptions size="small" column={2}>
          <Descriptions.Item label={t('geneView.fullName')}>{info.name || '-'}</Descriptions.Item>
          <Descriptions.Item label={t('geneView.chromosome')}>{info.chromosome || '-'}</Descriptions.Item>
          {info.inheritance && info.inheritance.length > 0 && (
            <Descriptions.Item label="Inheritance">
              {info.inheritance.map(i => <Tag key={i} color="blue">{i}</Tag>)}
            </Descriptions.Item>
          )}
          {info.omim_id && (
            <Descriptions.Item label="OMIM">
              <a href={`https://omim.org/entry/${info.omim_id}`} target="_blank" rel="noopener noreferrer">
                {info.omim_id}
              </a>
            </Descriptions.Item>
          )}
          {info.diseases && info.diseases.length > 0 && (
            <Descriptions.Item label="Diseases" span={2}>
              <Text style={{ fontSize: 12 }}>{info.diseases.slice(0, 3).join(', ')}{info.diseases.length > 3 ? '...' : ''}</Text>
            </Descriptions.Item>
          )}
        </Descriptions>
      </div>
    )
  }

  const renderVariantsTable = (geneName: string) => {
    const variants = geneVariants[geneName] || []
    const isLoading = loadingVariants[geneName]
    
    if (isLoading) {
      return (
        <div style={{ padding: 24, textAlign: 'center' }}>
          <Spin size="small" />
        </div>
      )
    }
    
    if (variants.length === 0) {
      return <Empty description={t('geneView.noVariants')} image={Empty.PRESENTED_IMAGE_SIMPLE} />
    }
    
    const columns: ColumnsType<GeneVariant> = [
      {
        title: t('geneView.colPosition'),
        dataIndex: 'chromosome',
        key: 'position',
        width: 130,
        render: (_, record) => (
          <Text code style={{ fontSize: 11 }}>
            {formatPosition(record.chromosome, record.position)}
          </Text>
        ),
      },
      {
        title: t('geneView.colChange'),
        key: 'change',
        width: 100,
        render: (_, record) => (
          <Text code style={{ fontSize: 11 }}>
            {record.ref.length > 8 ? `${record.ref.slice(0, 4)}...` : record.ref} → {record.alt.length > 8 ? `${record.alt.slice(0, 4)}...` : record.alt}
          </Text>
        ),
      },
      {
        title: t('geneView.colType'),
        dataIndex: 'variant_type',
        key: 'variant_type',
        width: 70,
        render: (type: string) => <Tag color={VARIANT_TYPE_COLORS[type]}>{type}</Tag>,
      },
      {
        title: t('geneView.colClass'),
        key: 'classification',
        width: 120,
        render: (_, record) => {
          const cls = record.acmg_classification || record.clinvar_significance
          if (!cls) return <Text type="secondary">-</Text>
          return <Tag color={CLASSIFICATION_COLORS[cls]}>{cls}</Tag>
        },
      },
      {
        title: 'gnomAD AF',
        dataIndex: 'gnomad_af',
        key: 'gnomad_af',
        width: 80,
        render: (af: number | null) => <Text type={af && af > 0.01 ? 'secondary' : undefined}>{formatAF(af)}</Text>,
      },
      {
        title: t('geneView.colAction'),
        key: 'action',
        width: 70,
        render: (_, record) => (
          <Button type="link" size="small" onClick={() => onVariantSelect(record)}>
            {t('geneView.details')}
          </Button>
        ),
      },
    ]
    
    return (
      <Table
        columns={columns}
        dataSource={variants}
        rowKey="id"
        size="small"
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          pageSizeOptions: ['10', '20', '50'],
          showTotal: (total) => t('geneView.totalVariants', { count: total }),
        }}
        scroll={{ x: 600, y: 400 }}
      />
    )
  }

  const hpoScoreColumns: ColumnsType<GenePhenotypeScore> = [
    {
      title: 'Rank',
      dataIndex: 'gene_rank',
      key: 'gene_rank',
      width: 60,
      sorter: (a, b) => a.gene_rank - b.gene_rank,
    },
    {
      title: 'Gene',
      dataIndex: 'gene_symbol',
      key: 'gene_symbol',
      width: 100,
      render: (gene: string) => (
        <Button type="link" size="small" onClick={() => onGeneFilter(gene)} style={{ padding: 0 }}>
          {gene}
        </Button>
      ),
    },
    {
      title: 'Score',
      dataIndex: 'gene_score',
      key: 'gene_score',
      width: 80,
      sorter: (a, b) => a.gene_score - b.gene_score,
      defaultSortOrder: 'descend',
      render: (score: number) => (
        <Text strong={score >= 0.8} style={{ color: score >= 0.8 ? '#cf1322' : score >= 0.5 ? '#d46b08' : undefined }}>
          {score.toFixed(3)}
        </Text>
      ),
    },
    {
      title: 'Conclusion',
      dataIndex: 'conclusion_code',
      key: 'conclusion_code',
      width: 150,
      render: (code: string) => (
        <Tag color={CONCLUSION_CODE_COLORS[code] || 'default'}>
          {code.replace(/_/g, ' ')}
        </Tag>
      ),
    },
    {
      title: 'Best Disease',
      dataIndex: 'best_disease_name',
      key: 'best_disease_name',
      width: 200,
      ellipsis: true,
    },
    {
      title: 'OMIM',
      dataIndex: 'best_omim_id',
      key: 'best_omim_id',
      width: 90,
      render: (id: string) => id ? (
        <a href={`https://omim.org/entry/${id}`} target="_blank" rel="noopener noreferrer">
          {id}
        </a>
      ) : '-',
    },
    {
      title: 'Variants',
      dataIndex: 'candidate_variant_count_in_gene',
      key: 'candidate_variant_count_in_gene',
      width: 70,
      render: (count: number) => <Tag color="blue">{count}</Tag>,
    },
    {
      title: 'Matched HPO',
      key: 'matched_hpo',
      width: 100,
      render: (_, record) => (
        <Text>
          {record.matched_hpo_count}/{record.input_hpo_count}
        </Text>
      ),
    },
    {
      title: 'Gap to 2nd',
      dataIndex: 'score_gap_to_second_best',
      key: 'score_gap_to_second_best',
      width: 90,
      render: (gap: number) => gap > 0 ? gap.toFixed(3) : '-',
    },
  ]

  const ppiScoreColumns: ColumnsType<PpiGeneScore> = [
    {
      title: 'Rank',
      dataIndex: 'rank',
      key: 'rank',
      width: 60,
      sorter: (a, b) => a.rank - b.rank,
    },
    {
      title: 'Gene',
      dataIndex: 'gene',
      key: 'gene',
      width: 100,
      render: (gene: string) => (
        <Button type="link" size="small" onClick={() => onGeneFilter(gene)} style={{ padding: 0 }}>
          {gene}
        </Button>
      ),
    },
    {
      title: 'Final Score',
      dataIndex: 'final_score',
      key: 'final_score',
      width: 100,
      sorter: (a, b) => a.final_score - b.final_score,
      defaultSortOrder: 'descend',
      render: (score: number) => (
        <Text strong={score >= 0.7} style={{ color: score >= 0.7 ? '#cf1322' : score >= 0.5 ? '#d46b08' : undefined }}>
          {score.toFixed(3)}
        </Text>
      ),
    },
    {
      title: 'Disease',
      dataIndex: 'disease_score',
      key: 'disease_score',
      width: 80,
      render: (score: number) => score.toFixed(3),
    },
    {
      title: 'Tissue',
      dataIndex: 'tissue_score',
      key: 'tissue_score',
      width: 80,
      render: (score: number) => score.toFixed(3),
    },
    {
      title: 'Topology',
      dataIndex: 'topology_score',
      key: 'topology_score',
      width: 80,
      render: (score: number) => score.toFixed(3),
    },
    {
      title: 'HPO Match',
      dataIndex: 'hpo_match_count',
      key: 'hpo_match_count',
      width: 90,
      render: (count: number) => <Tag color="blue">{count}</Tag>,
    },
    {
      title: 'Neighbors',
      dataIndex: 'neighbor_genes',
      key: 'neighbor_genes',
      width: 150,
      ellipsis: true,
      render: (genes: string) => genes ? genes.slice(0, 50) + (genes.length > 50 ? '...' : '') : '-',
    },
    {
      title: 'Disease Evidence',
      dataIndex: 'disease_evidence',
      key: 'disease_evidence',
      width: 200,
      ellipsis: true,
    },
    {
      title: 'Tissue Evidence',
      dataIndex: 'tissue_evidence',
      key: 'tissue_evidence',
      width: 200,
      ellipsis: true,
    },
  ]

  const geneColumns: ColumnsType<GeneSummary> = [
    {
      title: t('geneView.gene'),
      dataIndex: 'gene',
      key: 'gene',
      width: 120,
      render: (gene: string) => (
        <Space>
          <Button 
            type="link" 
            size="small" 
            onClick={(e) => { e.stopPropagation(); onGeneFilter(gene) }}
            style={{ padding: 0, fontWeight: 'bold' }}
          >
            {gene}
          </Button>
          <Tooltip title={t('geneView.viewGeneInfo')}>
            <InfoCircleOutlined style={{ color: '#999', fontSize: 12 }} />
          </Tooltip>
        </Space>
      ),
    },
    {
      title: 'Variants',
      dataIndex: 'variant_count',
      key: 'variant_count',
      width: 80,
      sorter: (a, b) => a.variant_count - b.variant_count,
      render: (count: number) => <Tag color="blue">{count}</Tag>,
    },
    {
      title: 'Types',
      dataIndex: 'variant_types',
      key: 'variant_types',
      width: 180,
      render: (types: Record<string, number>) => renderTypes(types),
    },
    {
      title: 'Classifications',
      dataIndex: 'classifications',
      key: 'classifications',
      width: 180,
      render: (classifications: Record<string, number>) => renderClassifications(classifications),
    },
    {
      title: 'Max AF',
      dataIndex: 'max_gnomad_af',
      key: 'max_gnomad_af',
      width: 80,
      render: (af: number | null) => (
        <Text type={af && af > 0.01 ? 'secondary' : undefined}>
          {formatAF(af)}
        </Text>
      ),
    },
    {
      title: t('geneView.colAction'),
      key: 'action',
      width: 80,
      render: (_, record) => (
        <Button 
          type="text" 
          size="small"
          icon={expandedGene === record.gene ? <DownOutlined /> : <RightOutlined />}
          onClick={() => handleExpand(record.gene)}
        >
          {expandedGene === record.gene ? t('geneView.collapse') : t('geneView.expand')}
        </Button>
      ),
    },
  ]

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
        <Spin tip={t('geneView.loadingGenes')} />
      </div>
    )
  }

  if (genes.length === 0) {
    return (
      <Empty 
        description={t('geneView.noGenes')} 
        style={{ marginTop: 48 }}
      />
    )
  }

  const canRunHpo = primaryHpoTerms.length > 0
  const canRunPpi = hpoJobUid !== null
  
  const geneStart = (genePage - 1) * genePageSize
  const geneEnd = geneStart + genePageSize
  const paginatedGenes = genes.slice(geneStart, geneEnd)
  
  const hpoStart = (hpoPage - 1) * hpoPageSize
  const hpoEnd = hpoStart + hpoPageSize
  const paginatedHpoScores = hpoScores.slice(hpoStart, hpoEnd)
  
  const ppiStart = (ppiPage - 1) * ppiPageSize
  const ppiEnd = ppiStart + ppiPageSize
  const paginatedPpiScores = ppiScores.slice(ppiStart, ppiEnd)

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ 
        marginBottom: 12, 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        flexShrink: 0,
      }}>
        <Space>
          <Segmented
            value={viewMode}
            onChange={(value) => setViewMode(value as 'genes' | 'hpo' | 'ppi')}
            options={[
              { label: `Genes (${genes.length})`, value: 'genes' },
              { label: hpoScores.length > 0 ? `HPO (${hpoScores.length})` : 'HPO', value: 'hpo' },
              { label: ppiScores.length > 0 ? `PPI (${ppiScores.length})` : 'PPI', value: 'ppi' },
            ]}
          />
          {viewMode === 'genes' && genes.length > 0 && (
            <Pagination
              current={genePage}
              pageSize={genePageSize}
              total={genes.length}
              onChange={(page, pageSize) => {
                setGenePage(page)
                setGenePageSize(pageSize)
              }}
              showSizeChanger
              showTotal={(total) => `${total} genes`}
              pageSizeOptions={['10', '20', '50', '100']}
              size="small"
            />
          )}
          {viewMode === 'hpo' && hpoScores.length > 0 && (
            <Pagination
              current={hpoPage}
              pageSize={hpoPageSize}
              total={hpoScores.length}
              onChange={(page, pageSize) => {
                setHpoPage(page)
                setHpoPageSize(pageSize)
              }}
              showSizeChanger
              showTotal={(total) => `${total} genes`}
              pageSizeOptions={['10', '20', '50', '100']}
              size="small"
            />
          )}
          {viewMode === 'ppi' && ppiScores.length > 0 && (
            <Pagination
              current={ppiPage}
              pageSize={ppiPageSize}
              total={ppiScores.length}
              onChange={(page, pageSize) => {
                setPpiPage(page)
                setPpiPageSize(pageSize)
              }}
              showSizeChanger
              showTotal={(total) => `${total} genes`}
              pageSizeOptions={['10', '20', '50', '100']}
              size="small"
            />
          )}
        </Space>
        <Space>
          {(hpoLoading || ppiLoading) && (
            <Space>
              <Spin size="small" />
              <Text type="secondary">{hpoLoading ? hpoJobStatus : ppiJobStatus}...</Text>
            </Space>
          )}
          <Button 
            icon={<FilePdfOutlined />}
            onClick={() => setReportModalVisible(true)}
          >
            Generate Report
          </Button>
          <Tooltip title={!canRunPpi ? 'Run HPO Scoring first' : ''}>
            <Button 
              icon={<ApiOutlined />}
              onClick={handleRunPpiScoring}
              disabled={!canRunPpi || ppiLoading}
            >
              Run PPI Scoring
            </Button>
          </Tooltip>
          <Tooltip title={!canRunHpo ? 'No primary HPO terms available' : ''}>
            <Button 
              type="primary" 
              icon={<ExperimentOutlined />}
              onClick={handleRunHpoScoring}
              disabled={!canRunHpo || hpoLoading}
            >
              Run HPO Scoring
              {primaryHpoTerms.length > 0 && ` (${primaryHpoTerms.length})`}
            </Button>
          </Tooltip>
        </Space>
      </div>
      
      {viewMode === 'genes' ? (
        <div style={{ flex: 1, overflow: 'hidden' }}>
          <Table
            columns={geneColumns}
            dataSource={paginatedGenes}
            rowKey="gene"
            size="small"
            pagination={false}
            scroll={{ y: 'calc(100vh - 380px)' }}
            expandable={{
              expandedRowKeys: expandedGene ? [expandedGene] : [],
              expandedRowRender: (record) => (
                <div style={{ margin: -8, background: '#fff' }}>
                  {renderGeneInfo(record.gene)}
                  <div style={{ padding: 8 }}>
                    {renderVariantsTable(record.gene)}
                  </div>
                </div>
              ),
              expandIcon: () => null,
              rowExpandable: () => true,
            }}
            onRow={(record) => ({
              onClick: () => handleExpand(record.gene),
              style: { cursor: 'pointer' },
            })}
          />
        </div>
      ) : viewMode === 'hpo' ? (
        <div style={{ flex: 1, overflow: 'hidden' }}>
          {hpoScores.length > 0 ? (
            <Table
              columns={hpoScoreColumns}
              dataSource={paginatedHpoScores}
              rowKey="gene_symbol"
              size="small"
              pagination={false}
              scroll={{ x: 1200, y: 'calc(100vh - 380px)' }}
            />
          ) : (
            <Empty
              description={hpoLoading ? 'Running HPO scoring...' : 'No HPO scores yet. Click "Run HPO Scoring" to start.'}
              style={{ marginTop: 48 }}
            />
          )}
        </div>
      ) : (
        <div style={{ flex: 1, overflow: 'hidden' }}>
          {ppiScores.length > 0 ? (
            <Table
              columns={ppiScoreColumns}
              dataSource={paginatedPpiScores}
              rowKey="gene"
              size="small"
              pagination={false}
              scroll={{ x: 1200, y: 'calc(100vh - 380px)' }}
            />
          ) : (
            <Empty
              description={ppiLoading ? 'Running PPI scoring...' : 'No PPI scores yet. Run HPO Scoring first, then click "Run PPI Scoring".'}
              style={{ marginTop: 48 }}
            />
          )}
        </div>
      )}
      
      <ReportView
        visible={reportModalVisible}
        onClose={() => setReportModalVisible(false)}
        vcfFileId={parseInt(vcfFileId)}
        hpoJobUid={hpoJobUid || undefined}
        ppiJobId={ppiJobId || undefined}
        hpoTerms={primaryHpoTerms}
        onReportGenerated={handleReportGenerated}
      />
    </div>
  )
}

export default GeneView
