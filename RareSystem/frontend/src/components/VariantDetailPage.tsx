import React, { useState, useEffect, useRef, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Modal,
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
  Input,
  message,
  Tabs,
  Pagination,
} from 'antd'
import {
  InfoCircleOutlined,
  SyncOutlined,
  ArrowLeftOutlined,
  SearchOutlined,
  ExperimentOutlined,
  BookOutlined,
  LoadingOutlined,
  ExportOutlined,
  QuestionCircleOutlined,
  DragOutlined,
} from '@ant-design/icons'
import type { Variant, ACMGClassification, CriterionResult, EvidenceStrength } from '@/types'
import api from '@/services/api'
import ChatInterface from './ChatInterface'

const { Panel } = Collapse
const { Text, Title, Paragraph } = Typography
const { TabPane } = Tabs

interface PubMedArticle {
  pmid: string
  title: string
  authors: string[]
  journal: string
  year: string
  abstract: string
  url: string
  doi: string
}

interface VariantDetailPageProps {
  visible: boolean
  variant: Variant | null
  patientId?: number
  onClose: () => void
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

const VariantDetailPage: React.FC<VariantDetailPageProps> = ({
  visible,
  variant,
  patientId = 1,
  onClose,
  onClassify,
}) => {
  const { t } = useTranslation()
  const [classification, setClassification] = useState<ACMGClassification | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [pubmedArticles, setPubmedArticles] = useState<PubMedArticle[]>([])
  const [pubmedLoading, setPubmedLoading] = useState(false)
  const [pubmedQuery, setPubmedQuery] = useState('')
  const [usedQuery, setUsedQuery] = useState('')
  const [totalResults, setTotalResults] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [activeTab, setActiveTab] = useState('acmg')
  const [leftWidth, setLeftWidth] = useState(60)
  const [isDragging, setIsDragging] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  const fetchClassification = async () => {
    if (!variant) return
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
          setError(t('acmg.classError'))
        }
      } else {
        setError(t('acmg.classError'))
      }
    } finally {
      setLoading(false)
    }
  }

  const runAnalysis = async () => {
    if (!variant) return
    setLoading(true)
    setError(null)
    try {
      const result = await api.runACMGAnalysis(variant.id)
      setClassification(result)
      onClassify?.(result)
    } catch (err) {
      setError(t('acmg.classError'))
    } finally {
      setLoading(false)
    }
  }

  const searchPubMed = async (query?: string) => {
    const searchQuery = query || pubmedQuery || (variant?.gene ? `${variant.gene} mutation` : '')
    if (!searchQuery) {
      message.warning(t('pubmed.placeholder'))
      return
    }

    setPubmedLoading(true)
    setUsedQuery(searchQuery)
    setCurrentPage(1)
    try {
      const result = await api.searchPubmed(searchQuery, 100, true)
      const articlesWithAbstracts = (result.articles || []).filter(
        (article: PubMedArticle) => article.abstract && article.abstract.trim().length > 0
      )
      setPubmedArticles(articlesWithAbstracts)
      setTotalResults(result.total_count || 0)
      if (articlesWithAbstracts.length === 0 && (result.articles || []).length > 0) {
        message.info(t('pubmed.noResults'))
      }
    } catch (err) {
      message.error(t('pubmed.noResults'))
      console.error('PubMed search error:', err)
    } finally {
      setPubmedLoading(false)
    }
  }

  const searchGeneMutation = () => {
    if (variant?.gene) {
      const query = `${variant.gene} gene mutation pathogenic variant`
      setPubmedQuery(query)
      searchPubMed(query)
      setActiveTab('literature')
    }
  }

  useEffect(() => {
    if (visible && variant) {
      fetchClassification()
      if (variant.gene) {
        setPubmedQuery(`${variant.gene} mutation`)
      }
    }
  }, [visible, variant?.id])

  const handleMouseDown = useCallback(() => {
    setIsDragging(true)
  }, [])

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging || !containerRef.current) return
    const containerRect = containerRef.current.getBoundingClientRect()
    const newWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100
    setLeftWidth(Math.min(80, Math.max(30, newWidth)))
  }, [isDragging])

  const handleMouseUp = useCallback(() => {
    setIsDragging(false)
  }, [])

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      return () => {
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isDragging, handleMouseMove, handleMouseUp])

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

  const renderVariantBasicInfo = () => {
    if (!variant) return null

    return (
      <Card title={
        <Space>
          <ExperimentOutlined />
          <span>{t('variantDetail.title')}</span>
        </Space>
      } style={{ marginBottom: 16 }}>
        <Descriptions column={2} bordered size="small">
          <Descriptions.Item label={t('variantDetail.chromosome')}>{variant.chromosome}</Descriptions.Item>
          <Descriptions.Item label={t('variantDetail.position')}>{variant.position?.toLocaleString()}</Descriptions.Item>
          <Descriptions.Item label={t('variantDetail.reference')}>{variant.ref}</Descriptions.Item>
          <Descriptions.Item label={t('variantDetail.alternate')}>{variant.alt}</Descriptions.Item>
          <Descriptions.Item label={t('variantDetail.gene')}>
            <Text strong style={{ color: '#1890ff', fontSize: 16 }}>{variant.gene || '-'}</Text>
            {variant.gene && (
              <Button type="link" size="small" onClick={searchGeneMutation}>
                {t('variantDetail.searchLiterature')}
              </Button>
            )}
          </Descriptions.Item>
          <Descriptions.Item label={t('variantDetail.type')}>
            <Tag color="blue">{variant.variant_type}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label={t('variantDetail.quality')}>
            <Badge
              status={(variant.quality ?? 0) >= 30 ? 'success' : (variant.quality ?? 0) >= 20 ? 'warning' : 'error'}
              text={variant.quality?.toFixed(1) || '-'}
            />
          </Descriptions.Item>
          <Descriptions.Item label="HGVS.p">
            <Text code>{variant.hgvs_p || '-'}</Text>
          </Descriptions.Item>
          <Descriptions.Item label={t('variantDetail.consequence')}>{variant.consequence?.replace(/_/g, ' ') || '-'}</Descriptions.Item>
          <Descriptions.Item label="gnomAD AF">
            {variant.gnomad_af ? (variant.gnomad_af * 100).toFixed(4) + '%' : '-'}
          </Descriptions.Item>
        </Descriptions>
      </Card>
    )
  }

  const renderACMGSection = () => {
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
                      <Text strong>Confidence</Text>
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

        <Card title="Evidence Summary">
          <Collapse defaultActiveKey={['pathogenic', 'benign']}>
            <Panel
              header={
                <Space>
                  <Text strong>Pathogenic Evidence</Text>
                  <Tag color="red">
                    {(classification.pathogenic_criteria ?? []).filter((c) => c.is_met).length} met
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
                  <Text strong>Benign Evidence</Text>
                  <Tag color="green">
                    {(classification.benign_criteria ?? []).filter((c) => c.is_met).length} met
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
          <Card title="Warnings">
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
          title="Evidence Chain"
          extra={
            <Tooltip title="Traceable evidence sources for clinical documentation">
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
          Re-analyze
        </Button>
      </Space>
    )
  }

  const renderLiteratureSection = () => {
    return (
      <Card 
        title={
          <Space>
            <BookOutlined />
            <span>Related Literature (PubMed)</span>
          </Space>
        }
        extra={
          <Space>
            <Input
              placeholder="Search query..."
              value={pubmedQuery}
              onChange={(e) => setPubmedQuery(e.target.value)}
              onPressEnter={() => searchPubMed()}
              style={{ width: 300 }}
              prefix={<SearchOutlined />}
            />
            <Button type="primary" onClick={() => searchPubMed()} loading={pubmedLoading}>
              Search
            </Button>
          </Space>
        }
      >
        {variant?.gene && !usedQuery && (
          <Alert
            message={`Click "Search" to find literature related to ${variant.gene} gene mutations`}
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}

        {usedQuery && (
          <Card 
            size="small" 
            style={{ marginBottom: 16, background: '#fafafa' }}
            bodyStyle={{ padding: '12px 16px' }}
          >
            <Space direction="vertical" style={{ width: '100%' }} size="small">
              <Text type="secondary" style={{ fontSize: 12 }}>
                Search Terms ({totalResults} total results):
              </Text>
              <Space.Compact style={{ width: '100%' }}>
                <Input
                  value={pubmedQuery}
                  onChange={(e) => setPubmedQuery(e.target.value)}
                  onPressEnter={() => searchPubMed()}
                  placeholder="Edit search terms..."
                  prefix={<SearchOutlined />}
                />
                <Button 
                  type="primary" 
                  onClick={() => searchPubMed()} 
                  loading={pubmedLoading}
                  icon={<SyncOutlined />}
                >
                  Re-search
                </Button>
              </Space.Compact>
            </Space>
          </Card>
        )}

        {pubmedLoading ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Spin indicator={<LoadingOutlined style={{ fontSize: 24 }} spin />} />
            <div style={{ marginTop: 16 }}>
              <Text>Searching PubMed...</Text>
            </div>
          </div>
        ) : pubmedArticles.length > 0 ? (
          <>
            <Collapse
              accordion
              style={{ background: '#fff' }}
            >
              {pubmedArticles
                .slice((currentPage - 1) * pageSize, currentPage * pageSize)
                .map((article, index) => {
                  const globalIndex = (currentPage - 1) * pageSize + index + 1
                  return (
                    <Panel
                      key={article.pmid}
                      header={
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', paddingRight: 24 }}>
                          <div style={{ flex: 1, marginRight: 16 }}>
                            <Text strong style={{ fontSize: 14 }}>
                              {globalIndex}. {article.title}
                            </Text>
                          </div>
                          <Space>
                            <Tag color="blue" style={{ margin: 0 }}>PMID: {article.pmid}</Tag>
                            {article.year && <Tag style={{ margin: 0 }}>{article.year}</Tag>}
                          </Space>
                        </div>
                      }
                      style={{ marginBottom: 8 }}
                    >
                      <Space direction="vertical" style={{ width: '100%' }} size="middle">
                        <div>
                          <Space split={<Divider type="vertical" />}>
                            {article.authors?.length > 0 && (
                              <Text type="secondary">
                                {article.authors.slice(0, 3).join(', ')}
                                {article.authors.length > 3 ? ' et al.' : ''}
                              </Text>
                            )}
                            {article.journal && (
                              <Text type="secondary" italic>{article.journal}</Text>
                            )}
                            {article.doi && (
                              <Text type="secondary">DOI: {article.doi}</Text>
                            )}
                          </Space>
                        </div>
                        
                        {article.abstract && (
                          <div style={{ 
                            background: '#fafafa', 
                            padding: 12, 
                            borderRadius: 8,
                            maxHeight: 300,
                            overflowY: 'auto'
                          }}>
                            <Text type="secondary" style={{ fontSize: 12 }}>
                              <strong>Abstract:</strong>
                            </Text>
                            <Paragraph style={{ margin: '8px 0 0 0', fontSize: 13, lineHeight: 1.6 }}>
                              {article.abstract}
                            </Paragraph>
                          </div>
                        )}
                        
                        <div style={{ textAlign: 'right' }}>
                          <Button
                            type="link"
                            href={article.url}
                            target="_blank"
                            icon={<ExportOutlined />}
                          >
                            View on PubMed
                          </Button>
                        </div>
                      </Space>
                    </Panel>
                  )
                })}
            </Collapse>
            {pubmedArticles.length > pageSize && (
              <div style={{ marginTop: 16, textAlign: 'center' }}>
                <Pagination
                  current={currentPage}
                  pageSize={pageSize}
                  total={pubmedArticles.length}
                  onChange={(page, newPageSize) => {
                    setCurrentPage(page)
                    if (newPageSize !== pageSize) {
                      setPageSize(newPageSize)
                      setCurrentPage(1)
                    }
                  }}
                  showSizeChanger
                  showQuickJumper
                  showTotal={(total) => `Total ${total} articles`}
                  pageSizeOptions={['5', '10', '20', '50']}
                />
              </div>
            )}
          </>
        ) : (
          <Empty
            description="No literature found. Click 'Search' to find related articles."
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          >
            {variant?.gene && (
              <Button type="primary" onClick={() => searchPubMed()}>
                Search for {variant.gene} mutations
              </Button>
            )}
          </Empty>
        )}
      </Card>
    )
  }

  return (
    <Modal
      open={visible}
      onCancel={onClose}
      width="95vw"
      style={{ top: 10 }}
      bodyStyle={{ height: 'calc(100vh - 80px)', padding: 0 }}
      footer={null}
      closable={false}
      title={
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', paddingRight: 40 }}>
          <Space>
            <Button icon={<ArrowLeftOutlined />} onClick={onClose}>
              {t('common.back')}
            </Button>
            <Divider type="vertical" />
            <Text strong style={{ fontSize: 18 }}>
              {t('variantDetail.title')}
            </Text>
            {variant && (
              <Text code style={{ fontSize: 14 }}>
                {variant.chromosome}:{variant.position} {variant.gene && `(${variant.gene})`}
              </Text>
            )}
          </Space>
          <Space>
            <QuestionCircleOutlined style={{ color: '#1890ff' }} />
            <Text type="secondary">{t('chat.title')}</Text>
          </Space>
        </div>
      }
    >
      {variant && (
        <div
          ref={containerRef}
          style={{
            display: 'flex',
            height: '100%',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: `${leftWidth}%`,
              minWidth: 400,
              overflow: 'auto',
              padding: '16px 16px 16px 24px',
              background: '#f5f5f5',
            }}
          >
            {renderVariantBasicInfo()}

            <Tabs activeKey={activeTab} onChange={setActiveTab} size="large">
              <TabPane
                tab={
                  <Space>
                    <ExperimentOutlined />
                    <span>{t('acmg.title')}</span>
                  </Space>
                }
                key="acmg"
              >
                {renderACMGSection()}
              </TabPane>

              <TabPane
                tab={
                  <Space>
                    <BookOutlined />
                    <span>{t('variantDetail.literature')}</span>
                  </Space>
                }
                key="literature"
              >
                {renderLiteratureSection()}
              </TabPane>
            </Tabs>
          </div>

          <div
            style={{
              width: 8,
              background: isDragging ? '#1890ff' : '#e8e8e8',
              cursor: 'col-resize',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: isDragging ? 'none' : 'background 0.2s',
              zIndex: 10,
            }}
            onMouseDown={handleMouseDown}
          >
            <DragOutlined style={{ color: isDragging ? '#fff' : '#999', fontSize: 12 }} />
          </div>

          <div
            style={{
              width: `${100 - leftWidth}%`,
              minWidth: 350,
              display: 'flex',
              flexDirection: 'column',
              background: '#fff',
              borderLeft: '1px solid #f0f0f0',
            }}
          >
            <div
              style={{
                padding: '12px 16px',
                borderBottom: '1px solid #f0f0f0',
                background: '#fafafa',
              }}
            >
              <Space>
                <QuestionCircleOutlined style={{ color: '#1890ff', fontSize: 18 }} />
                <Text strong style={{ fontSize: 16 }}>Case Q&A</Text>
              </Space>
            </div>
            <div style={{ flex: 1, overflow: 'hidden' }}>
              <ChatInterface patientId={patientId} />
            </div>
          </div>
        </div>
      )}
    </Modal>
  )
}

export default VariantDetailPage
