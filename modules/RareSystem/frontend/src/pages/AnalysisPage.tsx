import React, { useState, useEffect, useRef, useCallback } from 'react'
import { Button, Space, Tabs, Spin, message, Segmented } from 'antd'
import { ArrowLeftOutlined } from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import VariantList from '@/components/VariantList'
import GeneView from '@/components/GeneView'
import PathwayView, { PathwayViewRef } from '@/components/PathwayView'
import DualTrackReport from '@/components/DualTrackReport'
import ChatInterface from '@/components/ChatInterface'
import VariantVisualization from '@/components/VariantVisualization'
import BasicInfoPanel from '@/components/BasicInfoPanel'
import VariantDetailPage from '@/components/VariantDetailPage'
import { useAppStore } from '@/store'
import api from '@/services/api'
import type { Variant, ChatMessage, ACMGClassification, GeneVariant, PathwayAnalysisResponse } from '@/types'

const { TabPane } = Tabs

interface AnalysisPageProps {
  patientId: string
  vcfFileId: string
  hpoJobId?: string
  onBack: () => void
}

const MIN_LEFT_WIDTH = 30
const MAX_LEFT_WIDTH = 80
const DIVIDER_WIDTH = 6
const MIN_BASIC_INFO_HEIGHT = 60
const MAX_BASIC_INFO_HEIGHT = 600
const DEFAULT_BASIC_INFO_HEIGHT = 280
const VERTICAL_DIVIDER_HEIGHT = 6

const AnalysisPage: React.FC<AnalysisPageProps> = ({ patientId, vcfFileId, hpoJobId, onBack }) => {
  const { t } = useTranslation()
  const patientIdNum = parseInt(patientId, 10) || 1
  const [variantDetailVisible, setVariantDetailVisible] = useState(false)
  const [loading, setLoading] = useState(true)
  const [chatMessages] = useState<ChatMessage[]>([])
  const [leftWidth, setLeftWidth] = useState(70)
  const [basicInfoHeight, setBasicInfoHeight] = useState(DEFAULT_BASIC_INFO_HEIGHT)
  const [basicInfoCollapsed, setBasicInfoCollapsed] = useState(false)
  const [viewMode, setViewMode] = useState<'variant' | 'gene' | 'pathway'>('variant')
  const [geneFilter, setGeneFilter] = useState<string | undefined>(undefined)
  const [hpoStatus, setHpoStatus] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)
  const [pathwayPreloading, setPathwayPreloading] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const leftPanelRef = useRef<HTMLDivElement>(null)
  const draggingRef = useRef(false)
  const verticalDraggingRef = useRef(false)
  const pathwayViewRef = useRef<PathwayViewRef>(null)

  const {
    variants,
    selectedVariant,
    setVariants,
    setSelectedVariant,
    setClassification,
  } = useAppStore()

  useEffect(() => {
    loadVariants()
  }, [vcfFileId])

  useEffect(() => {
    if (!hpoJobId) return

    let mounted = true
    const pollInterval = 3000

    const pollHpoStatus = async () => {
      try {
        const status = await api.getHPOJobStatus(hpoJobId)
        if (!mounted) return

        setHpoStatus(status.status)

        if (status.status === 'completed') {
          setRefreshKey(k => k + 1)
        } else if (status.status === 'queued' || status.status === 'processing') {
          setTimeout(pollHpoStatus, pollInterval)
        }
      } catch (err) {
        console.error('Failed to poll HPO status:', err)
        if (mounted) {
          setTimeout(pollHpoStatus, pollInterval * 2)
        }
      }
    }

    pollHpoStatus()

    return () => {
      mounted = false
    }
  }, [hpoJobId])

  const loadVariants = async () => {
    setLoading(true)
    try {
      const response = await api.getVariants(vcfFileId)
      setVariants(response.items)
      preloadPathwayAnalysis()
    } catch (error) {
      message.error(t('analysis.loadVariantsFailed'))
    } finally {
      setLoading(false)
    }
  }

  const preloadPathwayAnalysis = async () => {
    const cacheKey = `pathway_cache_${vcfFileId}`
    const cached = localStorage.getItem(cacheKey)
    if (cached) return
    
    setPathwayPreloading(true)
    try {
      const response: PathwayAnalysisResponse = await api.analyzeVcfPathways(vcfFileId)
      const filteredPathways = response.pathways.filter(p => 
        p.mapped_genes && p.mapped_genes.length > 0
      )
      
      localStorage.setItem(cacheKey, JSON.stringify({
        pathways: filteredPathways,
        genes: Array.from(new Set(filteredPathways.flatMap(p => p.mapped_genes || []))),
        timestamp: Date.now()
      }))
      
      if (pathwayViewRef.current?.reloadPathways) {
        pathwayViewRef.current.reloadPathways()
      }
    } catch (error) {
      console.error('Failed to preload pathway analysis:', error)
    } finally {
      setPathwayPreloading(false)
    }
  }

  const handleVariantSelect = (variant: Variant | GeneVariant) => {
    const fullVariant: Variant = 'vcf_file_id' in variant 
      ? variant 
      : {
          id: variant.id,
          chromosome: variant.chromosome,
          position: variant.position,
          ref: variant.ref,
          alt: variant.alt,
          variant_type: variant.variant_type as any,
          quality: variant.quality ?? undefined,
          vcf_file_id: vcfFileId,
          info_field: {},
          gnomad_af: variant.gnomad_af,
        }
    setSelectedVariant(fullVariant)
    setVariantDetailVisible(true)
  }

  const handleVariantDetailClose = () => {
    setVariantDetailVisible(false)
  }

  const handleClassificationUpdate = (classification: ACMGClassification) => {
    setClassification(classification)
  }

  const handleGeneFilter = (gene: string) => {
    setGeneFilter(gene)
    setViewMode('variant')
  }

  const handleClearGeneFilter = () => {
    setGeneFilter(undefined)
  }

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    draggingRef.current = true
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
  }, [])

  const handleVerticalMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    verticalDraggingRef.current = true
    document.body.style.cursor = 'row-resize'
    document.body.style.userSelect = 'none'
  }, [])

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (draggingRef.current && containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect()
        const percent = ((e.clientX - rect.left) / rect.width) * 100
        const clamped = Math.max(MIN_LEFT_WIDTH, Math.min(MAX_LEFT_WIDTH, percent))
        setLeftWidth(clamped)
      }
      if (verticalDraggingRef.current && leftPanelRef.current) {
        const rect = leftPanelRef.current.getBoundingClientRect()
        const newHeight = e.clientY - rect.top
        const clamped = Math.max(MIN_BASIC_INFO_HEIGHT, Math.min(MAX_BASIC_INFO_HEIGHT, newHeight))
        setBasicInfoHeight(clamped)
      }
    }

    const handleMouseUp = () => {
      if (draggingRef.current) {
        draggingRef.current = false
        document.body.style.cursor = ''
        document.body.style.userSelect = ''
      }
      if (verticalDraggingRef.current) {
        verticalDraggingRef.current = false
        document.body.style.cursor = ''
        document.body.style.userSelect = ''
      }
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [])

  const classifications: ACMGClassification[] = []

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" tip={t('analysis.loading')} />
      </div>
    )
  }

  const rightWidth = 100 - leftWidth

  return (
    <div
      ref={containerRef}
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: 'calc(100vh - 64px)',
        overflow: 'hidden',
        background: '#f5f5f5',
      }}
    >
      <div
        style={{
          padding: '8px 16px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexShrink: 0,
          background: 'white',
          borderBottom: '1px solid #f0f0f0',
        }}
      >
        <Button icon={<ArrowLeftOutlined />} onClick={onBack}>
          {t('analysis.backToUpload')}
        </Button>
      </div>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden', padding: '8px' }}>
        <div
          ref={leftPanelRef}
          style={{
            width: `calc(${leftWidth}% - ${DIVIDER_WIDTH / 2}px)`,
            minWidth: 400,
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
            background: 'white',
            borderRadius: 8,
          }}
        >
          <BasicInfoPanel
            key={refreshKey}
            patientId={patientIdNum}
            collapsed={basicInfoCollapsed}
            onCollapse={setBasicInfoCollapsed}
            style={{
              height: basicInfoCollapsed ? 48 : basicInfoHeight,
              flexShrink: 0,
              overflow: 'hidden',
            }}
          />
          {hpoJobId && hpoStatus && hpoStatus !== 'completed' && (
            <div style={{ 
              padding: '4px 16px', 
              background: '#e6f7ff', 
              borderBottom: '1px solid #91d5ff',
              fontSize: 12,
              color: '#1890ff'
            }}>
              {hpoStatus === 'processing' ? 'Extracting HPO terms...' : 'HPO extraction queued...'}
            </div>
          )}
          
          <div
            onMouseDown={handleVerticalMouseDown}
            style={{
              height: VERTICAL_DIVIDER_HEIGHT,
              cursor: 'row-resize',
              background: '#e8e8e8',
              borderRadius: 3,
              margin: '2px 0',
              flexShrink: 0,
              transition: 'background 0.2s',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#1890ff'
            }}
            onMouseLeave={(e) => {
              if (!verticalDraggingRef.current) {
                e.currentTarget.style.background = '#e8e8e8'
              }
            }}
          />
          
          <Tabs
            defaultActiveKey="variants"
            size="large"
            style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}
            tabBarStyle={{ margin: 0, padding: '0 12px', flexShrink: 0 }}
          >
            <TabPane tab={t('analysis.tabVariants')} key="variants" style={{ flex: 1, overflow: 'auto' }}>
              <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                <div style={{ 
                  padding: '8px 16px', 
                  borderBottom: '1px solid #f0f0f0', 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center' 
                }}>
                  <Segmented
                    value={viewMode}
                    onChange={(value) => setViewMode(value as 'variant' | 'gene' | 'pathway')}
                    options={[
                      { label: t('analysis.byVariant'), value: 'variant' },
                      { label: t('analysis.byGene'), value: 'gene' },
                      { label: t('analysis.byPathway'), value: 'pathway' },
                    ]}
                  />
                  {pathwayPreloading && (
                    <Space>
                      <Spin size="small" />
                      <span style={{ color: '#999', fontSize: 12 }}>{t('analysis.preloadingPathways')}</span>
                    </Space>
                  )}
                  {geneFilter && (
                    <Space>
                      <span style={{ color: '#666' }}>{t('analysis.filteredByGene')}</span>
                      <Button size="small" onClick={handleClearGeneFilter}>
                        {t('analysis.clear', { gene: geneFilter })}
                      </Button>
                    </Space>
                  )}
                </div>
                <div style={{ flex: 1, overflow: 'auto' }}>
                  {viewMode === 'variant' ? (
                    <VariantList
                      vcfFileId={vcfFileId}
                      onVariantSelect={handleVariantSelect}
                      initialGeneFilter={geneFilter}
                    />
                  ) : viewMode === 'gene' ? (
                    <GeneView
                      vcfFileId={vcfFileId}
                      patientId={patientIdNum}
                      onVariantSelect={handleVariantSelect}
                      onGeneFilter={handleGeneFilter}
                    />
                  ) : (
                    <PathwayView
                      ref={pathwayViewRef}
                      vcfFileId={vcfFileId}
                      onVariantSelect={handleVariantSelect}
                    />
                  )}
                </div>
              </div>
            </TabPane>
            <TabPane tab={t('analysis.tabVisualization')} key="visualization" style={{ flex: 1, overflow: 'auto' }}>
              <VariantVisualization
                variants={variants}
                classifications={classifications}
              />
            </TabPane>
            <TabPane tab={t('analysis.tabReports')} key="reports" style={{ flex: 1, overflow: 'auto' }}>
              <DualTrackReport />
            </TabPane>
          </Tabs>
        </div>

        <div
          onMouseDown={handleMouseDown}
          style={{
            width: DIVIDER_WIDTH,
            cursor: 'col-resize',
            background: '#e8e8e8',
            borderRadius: 3,
            margin: '0 2px',
            flexShrink: 0,
            transition: 'background 0.2s',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = '#1890ff'
          }}
          onMouseLeave={(e) => {
            if (!draggingRef.current) {
              e.currentTarget.style.background = '#e8e8e8'
            }
          }}
        />

        <div
          style={{
            width: `calc(${rightWidth}% - ${DIVIDER_WIDTH / 2}px)`,
            minWidth: 300,
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <ChatInterface
            patientId={patientIdNum}
            initialMessages={chatMessages}
          />
        </div>
      </div>

      <VariantDetailPage
        visible={variantDetailVisible}
        variant={selectedVariant}
        patientId={patientIdNum}
        onClose={handleVariantDetailClose}
        onClassify={handleClassificationUpdate}
      />
    </div>
  )
}

export default AnalysisPage
