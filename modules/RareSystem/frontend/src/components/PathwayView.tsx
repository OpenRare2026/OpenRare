import { useState, useEffect, useRef, useMemo, forwardRef, useImperativeHandle } from 'react'
import {
  Table,
  Tag,
  Space,
  Button,
  Typography,
  Tooltip,
  Badge,
  Progress,
  Drawer,
  Descriptions,
  Spin,
  Empty,
  message,
  Divider,
  Collapse,
  List,
} from 'antd'
import {
  ExperimentOutlined,
  LinkOutlined,
  SearchOutlined,
  ReloadOutlined,
  BookOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import api from '@/services/api'
import type { PathwayResult, GeneVariant, PathwayAnalysisResponse, PathwayDetailResponse } from '@/types'

const { Text, Paragraph } = Typography
const { Panel } = Collapse

interface PathwayViewProps {
  vcfFileId: string
  onVariantSelect: (variant: GeneVariant) => void
  genes?: string[]
}

interface PathwayWithVariants extends PathwayResult {
  detail?: PathwayDetailResponse
}

const CACHE_KEY_PREFIX = 'pathway_cache_'

export interface PathwayViewRef {
  reloadPathways: () => void
}

const PathwayView = forwardRef<PathwayViewRef, PathwayViewProps>(({
  vcfFileId,
  onVariantSelect: _onVariantSelect,
  genes: externalGenes,
}, ref) => {
  const [loading, setLoading] = useState(false)
  const [pathways, setPathways] = useState<PathwayWithVariants[]>([])
  const [selectedPathway, setSelectedPathway] = useState<PathwayWithVariants | null>(null)
  const [drawerVisible, setDrawerVisible] = useState(false)
  const [variantsLoading, setVariantsLoading] = useState(false)
  const [analyzedGeneSet, setAnalyzedGeneSet] = useState<Set<string>>(new Set())
  const lastFetchKeyRef = useRef<string>('')

  const currentGenesKey = useMemo(() => {
    if (externalGenes && externalGenes.length > 0) {
      return externalGenes.slice().sort().join(',')
    }
    return vcfFileId
  }, [externalGenes, vcfFileId])

  useEffect(() => {
    loadPathways()
  }, [currentGenesKey])

  useImperativeHandle(ref, () => ({
    reloadPathways: () => loadPathways(true)
  }), [])

  const loadPathways = async (forceReload = false) => {
    if (!forceReload && lastFetchKeyRef.current === currentGenesKey) {
      return
    }

    setLoading(true)
    try {
      let response: PathwayAnalysisResponse
      
      const cacheKey = `${CACHE_KEY_PREFIX}${currentGenesKey}`
      
      if (!forceReload) {
        const cached = localStorage.getItem(cacheKey)
        if (cached) {
          try {
            const parsed = JSON.parse(cached)
            const cacheTime = parsed.timestamp || 0
            const now = Date.now()
            if (now - cacheTime < 30 * 60 * 1000) {
              const filteredPathways = parsed.pathways.filter((p: PathwayResult) => 
                p.mapped_genes && p.mapped_genes.length > 0
              )
              setPathways(filteredPathways.map((p: PathwayResult, idx: number) => ({
                ...p,
                key: idx,
              })))
              setAnalyzedGeneSet(new Set(parsed.genes || []))
              lastFetchKeyRef.current = currentGenesKey
              setLoading(false)
              return
            }
          } catch (e) {
            console.debug('Failed to parse cached pathway data')
          }
        }
      }

      if (externalGenes && externalGenes.length > 0) {
        response = await api.analyzePathways(externalGenes)
      } else {
        response = await api.analyzeVcfPathways(vcfFileId)
      }
      
      const filteredPathways = response.pathways.filter(p => 
        p.mapped_genes && p.mapped_genes.length > 0
      )
      
      const pathwayData = filteredPathways.map((p, idx) => ({
        ...p,
        key: idx,
      }))
      
      const allMappedGenes = new Set<string>()
      filteredPathways.forEach(p => {
        if (p.mapped_genes) {
          p.mapped_genes.forEach(g => allMappedGenes.add(g))
        }
      })
      
      setPathways(pathwayData)
      setAnalyzedGeneSet(allMappedGenes)
      lastFetchKeyRef.current = currentGenesKey

      try {
        localStorage.setItem(cacheKey, JSON.stringify({
          pathways: filteredPathways,
          genes: Array.from(allMappedGenes),
          timestamp: Date.now(),
        }))
      } catch (e) {
        console.debug('Failed to cache pathway data')
      }

      console.log(`Loaded ${filteredPathways.length} pathways with mapped genes (filtered from ${response.pathways.length} total)`)
      console.log(`Total mapped genes: ${allMappedGenes.size}`)
      
    } catch (error) {
      message.error('Failed to load pathway analysis')
      console.error('Pathway analysis error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePathwayClick = async (pathway: PathwayWithVariants) => {
    setSelectedPathway(pathway)
    setDrawerVisible(true)
    setVariantsLoading(true)
    
    try {
      const detail = await api.getPathwayDetail(pathway.st_id)
      setSelectedPathway({
        ...pathway,
        detail,
      })
    } catch (error) {
      console.error('Failed to load pathway details:', error)
    } finally {
      setVariantsLoading(false)
    }
  }

  const formatPValue = (p: number): string => {
    if (p < 0.001) {
      return p.toExponential(2)
    }
    return p.toFixed(4)
  }

  const getPValueColor = (p: number): string => {
    if (p < 0.001) return '#f5222d'
    if (p < 0.01) return '#fa541c'
    if (p < 0.05) return '#fa8c16'
    return '#d9d9d9'
  }

  const columns: ColumnsType<PathwayWithVariants> = [
    {
      title: 'Pathway',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
      render: (name: string, record) => (
        <Space>
          <Tooltip title={name}>
            <Text
              strong
              style={{ color: '#1890ff', cursor: 'pointer' }}
              onClick={() => handlePathwayClick(record)}
            >
              {name}
            </Text>
          </Tooltip>
          <Tooltip title="View in Reactome">
            <Button
              type="link"
              size="small"
              icon={<LinkOutlined />}
              onClick={() => window.open(`https://reactome.org/PathwayBrowser/#/${record.st_id}`, '_blank')}
            />
          </Tooltip>
        </Space>
      ),
    },
    {
      title: 'ID',
      dataIndex: 'st_id',
      key: 'st_id',
      width: 130,
      render: (id: string) => <Text code>{id}</Text>,
    },
    {
      title: 'Mapped Genes',
      dataIndex: 'mapped_genes',
      key: 'mapped_genes',
      width: 250,
      ellipsis: true,
      render: (genes: string[]) => {
        if (!genes || genes.length === 0) {
          return <Text type="secondary">-</Text>
        }
        const displayGenes = genes.slice(0, 6)
        const hasMore = genes.length > 6
        return (
          <Tooltip title={`${genes.length} genes: ${genes.join(', ')}`}>
            <Space size={2} wrap>
              {displayGenes.map((g, idx) => (
                <Tag key={idx} color="blue" style={{ margin: '1px', fontSize: 11 }}>
                  {g}
                </Tag>
              ))}
              {hasMore && (
                <Tag style={{ margin: '1px', fontSize: 11 }}>+{genes.length - 6}</Tag>
              )}
            </Space>
          </Tooltip>
        )
      },
    },
    {
      title: 'Type',
      dataIndex: 'pathway_type',
      key: 'pathway_type',
      width: 100,
      render: (pathwayType: string) => (
        <Tag color={pathwayType === 'Pathway' ? 'purple' : 'cyan'}>
          {pathwayType || 'Pathway'}
        </Tag>
      ),
    },
    {
      title: 'Compartments',
      dataIndex: 'compartments',
      key: 'compartments',
      width: 180,
      ellipsis: true,
      render: (compartments: string[]) => {
        if (!compartments || compartments.length === 0) {
          return <Text type="secondary">-</Text>
        }
        const displayComps = compartments.slice(0, 2)
        const hasMore = compartments.length > 2
        return (
          <Tooltip title={compartments.join(', ')}>
            <Space size={2} wrap>
              {displayComps.map((c, idx) => (
                <Tag key={idx} color="geekblue" style={{ margin: '1px', fontSize: 11 }}>
                  {c}
                </Tag>
              ))}
              {hasMore && (
                <Tag style={{ margin: '1px', fontSize: 11 }}>+{compartments.length - 2}</Tag>
              )}
            </Space>
          </Tooltip>
        )
      },
    },
  ]

  const pathwaysWithGenes = pathways.filter(p => p.mapped_genes && p.mapped_genes.length > 0)

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '12px 16px', borderBottom: '1px solid #f0f0f0', flexShrink: 0 }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Space>
            <ExperimentOutlined />
            <Text strong>Pathway Enrichment</Text>
            {pathways.length > 0 && (
              <Badge count={pathways.length} style={{ backgroundColor: '#1890ff' }} />
            )}
            {analyzedGeneSet.size > 0 && (
              <Text type="secondary" style={{ fontSize: 12 }}>
                ({analyzedGeneSet.size} genes mapped)
              </Text>
            )}
          </Space>
          <Space>
            <Button
              icon={<ReloadOutlined />}
              size="small"
              onClick={() => loadPathways(true)}
              loading={loading}
            >
              Refresh
            </Button>
          </Space>
        </Space>
      </div>

      {analyzedGeneSet.size > 0 && pathwaysWithGenes.length > 0 && (
        <div style={{ padding: '8px 16px', background: '#f6ffed', borderBottom: '1px solid #b7eb8f' }}>
          <Text style={{ fontSize: 12, color: '#52c41a' }}>
            ✓ {pathwaysWithGenes.length} pathways with gene matches from {analyzedGeneSet.size} mapped genes
          </Text>
        </div>
      )}

      <div style={{ flex: 1, overflow: 'auto' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Spin tip="Analyzing pathways..." />
          </div>
        ) : pathways.length > 0 ? (
          <Table
            columns={columns}
            dataSource={pathways}
            rowKey="st_id"
            size="small"
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showTotal: (total) => `${total} pathways`,
            }}
            scroll={{ y: 'calc(100vh - 520px)' }}
          />
        ) : (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="No pathway data available"
            style={{ padding: 40 }}
          >
            <Button type="primary" icon={<SearchOutlined />} onClick={() => loadPathways(true)}>
              Analyze Pathways
            </Button>
          </Empty>
        )}
      </div>

      <Drawer
        title={
          <Space>
            <ExperimentOutlined />
            <span>{selectedPathway?.detail?.display_name || selectedPathway?.name || 'Pathway Details'}</span>
          </Space>
        }
        placement="right"
        width={750}
        open={drawerVisible}
        onClose={() => setDrawerVisible(false)}
      >
        {selectedPathway && (
          <Spin spinning={variantsLoading}>
            {/* 基本信息 */}
            <Divider orientation="left">基本信息</Divider>
            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="数据库ID" span={1}>
                <Text code>{selectedPathway.detail?.db_id}</Text>
              </Descriptions.Item>
              <Descriptions.Item label="稳定标识符" span={1}>
                <Space>
                  <Text code>{selectedPathway.st_id}</Text>
                  {selectedPathway.detail?.st_id_version && (
                    <Text type="secondary">({selectedPathway.detail.st_id_version})</Text>
                  )}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="名称" span={2}>
                <Text strong>{selectedPathway.detail?.display_name || selectedPathway.name}</Text>
              </Descriptions.Item>
              <Descriptions.Item label="类型" span={1}>
                <Space>
                  <Tag color="purple">{selectedPathway.detail?.schema_class || 'Pathway'}</Tag>
                  {selectedPathway.detail?.class_name && (
                    <Text type="secondary">({selectedPathway.detail.class_name})</Text>
                  )}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="物种" span={1}>
                <Space>
                  <Text>{selectedPathway.detail?.species_name || selectedPathway.species}</Text>
                  {selectedPathway.detail?.species?.tax_id && (
                    <Text type="secondary">(TaxID: {selectedPathway.detail.species.tax_id})</Text>
                  )}
                </Space>
              </Descriptions.Item>
              {selectedPathway.detail?.species && (
                <Descriptions.Item label="物种别名" span={2}>
                  <Space size={4} wrap>
                    {selectedPathway.detail.species.name?.map((n, idx) => (
                      <Tag key={idx} style={{ fontSize: 11 }}>{n}</Tag>
                    ))}
                  </Space>
                </Descriptions.Item>
              )}
            </Descriptions>

            {/* 所属GO生物学过程 */}
            {selectedPathway.detail?.go_biological_process && (
              <>
                <Divider orientation="left">所属GO生物学过程</Divider>
                <Descriptions column={1} bordered size="small">
                  <Descriptions.Item label="GO ID">
                    <Space>
                      <Tag color="geekblue">{selectedPathway.detail.go_biological_process.accession}</Tag>
                      <Text>{selectedPathway.detail.go_biological_process.display_name}</Text>
                    </Space>
                  </Descriptions.Item>
                  {selectedPathway.detail.go_biological_process.definition && (
                    <Descriptions.Item label="定义">
                      <Text style={{ whiteSpace: 'pre-wrap' }}>
                        {selectedPathway.detail.go_biological_process.definition}
                      </Text>
                    </Descriptions.Item>
                  )}
                  <Descriptions.Item label="数据库">
                    <Space>
                      <Text>{selectedPathway.detail.go_biological_process.database_name}</Text>
                      <Button
                        type="link"
                        size="small"
                        icon={<LinkOutlined />}
                        onClick={() => window.open(selectedPathway.detail?.go_biological_process?.url, '_blank')}
                      >
                        View in QuickGO
                      </Button>
                    </Space>
                  </Descriptions.Item>
                </Descriptions>
              </>
            )}

            {/* 功能与背景 */}
            {selectedPathway.detail?.summation && selectedPathway.detail.summation.length > 0 && (
              <>
                <Divider orientation="left">功能与背景</Divider>
                {selectedPathway.detail.summation.map((s, idx) => (
                  <Paragraph key={idx} style={{ marginLeft: 16, whiteSpace: 'pre-wrap' }}>
                    {s.text}
                  </Paragraph>
                ))}
              </>
            )}

            {/* 包含的子通路 */}
            {selectedPathway.detail?.has_event && selectedPathway.detail.has_event.length > 0 && (
              <>
                <Divider orientation="left">
                  包含的子通路 ({selectedPathway.detail.has_event.length})
                </Divider>
                <Collapse ghost>
                  <Panel header={`展开查看 ${selectedPathway.detail.has_event.length} 个子事件`} key="events">
                    <List
                      size="small"
                      dataSource={selectedPathway.detail.has_event.slice(0, 50)}
                      renderItem={(event) => (
                        <List.Item>
                          <List.Item.Meta
                            title={
                              <Space>
                                <Tag color={event.schema_class === 'Pathway' ? 'purple' : 'cyan'}>
                                  {event.schema_class}
                                </Tag>
                                <Text code>{event.st_id}</Text>
                                <Text>{event.display_name}</Text>
                              </Space>
                            }
                            description={
                              <Space split={<Text type="secondary">|</Text>} size="small">
                                {event.species_name && <Text type="secondary">{event.species_name}</Text>}
                                {event.category && <Text type="secondary">Category: {event.category}</Text>}
                                {event.release_date && <Text type="secondary">Released: {event.release_date}</Text>}
                                {event.is_inferred && <Tag color="orange" style={{ fontSize: 10 }}>Inferred</Tag>}
                                {event.has_diagram && <Tag color="green" style={{ fontSize: 10 }}>Has Diagram</Tag>}
                              </Space>
                            }
                          />
                        </List.Item>
                      )}
                    />
                    {selectedPathway.detail.has_event.length > 50 && (
                      <Text type="secondary" style={{ marginLeft: 16 }}>
                        ...还有 {selectedPathway.detail.has_event.length - 50} 个子事件
                      </Text>
                    )}
                  </Panel>
                </Collapse>
              </>
            )}

            {/* 其他信息 */}
            <Divider orientation="left">其他信息</Divider>
            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="评审状态" span={1}>
                <Space direction="vertical" size={0}>
                  {selectedPathway.detail?.review_status ? (
                    <>
                      <Space>
                        <Tag color="gold">{selectedPathway.detail.review_status.display_name}</Tag>
                        <Text type="secondary">{selectedPathway.detail.review_status.definition}</Text>
                      </Space>
                    </>
                  ) : (
                    <Text type="secondary">-</Text>
                  )}
                  {selectedPathway.detail?.previous_review_status && (
                    <Text type="secondary" style={{ fontSize: 11 }}>
                      之前: {selectedPathway.detail.previous_review_status.display_name}
                    </Text>
                  )}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="图表状态" span={1}>
                <Space>
                  {selectedPathway.detail?.has_diagram ? (
                    <Tag color="green" icon={<CheckCircleOutlined />}>Has Diagram</Tag>
                  ) : (
                    <Tag color="default" icon={<CloseCircleOutlined />}>No Diagram</Tag>
                  )}
                  {selectedPathway.detail?.has_ehld && (
                    <Tag color="blue">Has EHLD</Tag>
                  )}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="发布日期" span={1}>
                {selectedPathway.detail?.release_date || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="最后更新" span={1}>
                {selectedPathway.detail?.last_updated_date || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="最大深度" span={1}>
                {selectedPathway.detail?.max_depth ?? '-'}
              </Descriptions.Item>
              <Descriptions.Item label="状态标签" span={1}>
                <Space size={4}>
                  {selectedPathway.detail?.is_in_disease && (
                    <Tag color="red">In Disease</Tag>
                  )}
                  {selectedPathway.detail?.is_inferred && (
                    <Tag color="orange">Inferred</Tag>
                  )}
                  {selectedPathway.detail?.release_status && (
                    <Tag>{selectedPathway.detail.release_status}</Tag>
                  )}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="查看" span={2}>
                <Button
                  type="link"
                  size="small"
                  icon={<LinkOutlined />}
                  onClick={() => window.open(selectedPathway.detail?.url || `https://reactome.org/PathwayBrowser/#/${selectedPathway.st_id}`, '_blank')}
                >
                  在 Reactome 中查看
                </Button>
              </Descriptions.Item>
            </Descriptions>

            {/* 跨物种同源事件 */}
            {selectedPathway.detail?.orthologous_event && selectedPathway.detail.orthologous_event.length > 0 && (
              <>
                <Divider orientation="left">
                  跨物种同源事件 ({selectedPathway.detail.orthologous_event.length} 个物种)
                </Divider>
                <Collapse ghost>
                  <Panel header={`展开查看 ${selectedPathway.detail.orthologous_event.length} 个物种的同源通路`} key="orthologs">
                    <List
                      size="small"
                      dataSource={selectedPathway.detail.orthologous_event}
                      renderItem={(ortho) => (
                        <List.Item>
                          <List.Item.Meta
                            title={
                              <Space>
                                <Tag color="blue">{ortho.species_name}</Tag>
                                <Text code>{ortho.st_id}</Text>
                              </Space>
                            }
                            description={
                              <Space split={<Text type="secondary">|</Text>} size="small">
                                {ortho.is_inferred && <Tag color="orange" style={{ fontSize: 10 }}>Inferred</Tag>}
                                {ortho.release_date && <Text type="secondary">Released: {ortho.release_date}</Text>}
                                <Text type="secondary">Max Depth: {ortho.max_depth}</Text>
                              </Space>
                            }
                          />
                        </List.Item>
                      )}
                    />
                  </Panel>
                </Collapse>
              </>
            )}
            
            {/* 主要参考文献 */}
            {selectedPathway.detail?.literature_reference && selectedPathway.detail.literature_reference.length > 0 && (
              <>
                <Divider orientation="left">
                  <BookOutlined /> 主要参考文献 ({selectedPathway.detail.literature_reference.length})
                </Divider>
                <List
                  size="small"
                  dataSource={selectedPathway.detail.literature_reference}
                  renderItem={(ref) => (
                    <List.Item>
                      <List.Item.Meta
                        title={
                          <Space>
                            {ref.pub_med_identifier && (
                              <Button
                                type="link"
                                size="small"
                                onClick={() => window.open(`https://pubmed.ncbi.nlm.nih.gov/${ref.pub_med_identifier}/`, '_blank')}
                              >
                                PMID: {ref.pub_med_identifier}
                              </Button>
                            )}
                            <Text>{ref.title || ref.display_name}</Text>
                          </Space>
                        }
                        description={
                          <Space split={<Text type="secondary">|</Text>}>
                            {ref.journal && <Text type="secondary">{ref.journal}</Text>}
                            {ref.year && <Text type="secondary">{ref.year}</Text>}
                            {ref.volume && <Text type="secondary">Vol {ref.volume}</Text>}
                            {ref.pages && <Text type="secondary">pp {ref.pages}</Text>}
                          </Space>
                        }
                      />
                    </List.Item>
                  )}
                />
              </>
            )}
            
            {/* 细胞区室 */}
            {selectedPathway.detail?.compartment && selectedPathway.detail.compartment.length > 0 && (
              <>
                <Divider orientation="left">细胞区室</Divider>
                <Space size={4} wrap style={{ marginLeft: 16 }}>
                  {selectedPathway.detail.compartment.map((comp, idx) => (
                    <Tooltip key={idx} title={`DB ID: ${comp.db_id}`}>
                      <Tag color="geekblue">
                        {comp.display_name}
                        {comp.accession && <Text type="secondary" style={{ marginLeft: 4, fontSize: 10 }}>({comp.accession})</Text>}
                      </Tag>
                    </Tooltip>
                  ))}
                </Space>
              </>
            )}
            
            {/* 富集分析 */}
            <Divider orientation="left">富集分析</Divider>
            <Descriptions column={1} bordered size="small">
              <Descriptions.Item label="p-value">
                <Tag color={getPValueColor(selectedPathway.p_value)}>
                  {formatPValue(selectedPathway.p_value)}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="FDR">
                <Tag color={selectedPathway.fdr < 0.05 ? 'red' : 'default'}>
                  {formatPValue(selectedPathway.fdr)}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="基因覆盖">
                <Text>{selectedPathway.entities_found} / {selectedPathway.entities_count}</Text>
                <Progress
                  percent={(selectedPathway.entities_found / selectedPathway.entities_count) * 100}
                  size="small"
                  status={selectedPathway.p_value < 0.05 ? 'active' : 'normal'}
                  style={{ marginTop: 8 }}
                />
              </Descriptions.Item>
            </Descriptions>
            
            {/* 相关基因 */}
            {selectedPathway.mapped_genes && selectedPathway.mapped_genes.length > 0 && (
              <>
                <Divider orientation="left">相关基因 ({selectedPathway.mapped_genes.length})</Divider>
                <Space size={4} wrap style={{ marginLeft: 16 }}>
                  {selectedPathway.mapped_genes.map((gene, idx) => (
                    <Tag key={idx} color="blue">{gene}</Tag>
                  ))}
                </Space>
              </>
            )}
          </Spin>
        )}
      </Drawer>
    </div>
  )
})

export default PathwayView
