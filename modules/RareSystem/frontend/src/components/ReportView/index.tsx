import React, { useState, useRef, useEffect } from 'react'
import {
  Modal,
  Progress,
  Button,
  Typography,
  Space,
  Alert,
  Spin,
} from 'antd'
import {
  DownloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import api from '@/services/api'
import type { ReportMeta } from '@/types'

const { Text } = Typography

interface ReportViewProps {
  visible: boolean
  onClose: () => void
  vcfFileId: number
  hpoJobUid?: string
  ppiJobId?: string
  hpoTerms: string[]
  symptomText?: string
  selectedGenes?: string[]
  onReportGenerated?: (report: { run_id: string; pdf_url: string; markdown: string; meta?: ReportMeta }) => void
}

type ReportStatus = 'idle' | 'generating' | 'completed' | 'error'

const ReportView: React.FC<ReportViewProps> = ({
  visible,
  onClose,
  vcfFileId,
  hpoJobUid,
  ppiJobId,
  hpoTerms,
  symptomText,
  selectedGenes,
  onReportGenerated,
}) => {
  const [status, setStatus] = useState<ReportStatus>('idle')
  const [progress, setProgress] = useState(0)
  const [markdown, setMarkdown] = useState('')
  const [meta, setMeta] = useState<ReportMeta | null>(null)
  const [runId, setRunId] = useState('')
  const [pdfUrl, setPdfUrl] = useState('')
  const [error, setError] = useState('')
  const abortControllerRef = useRef<AbortController | null>(null)

  useEffect(() => {
    if (visible && status === 'idle') {
      generateReport()
    }
  }, [visible])

  const generateReport = async () => {
    setStatus('generating')
    setProgress(0)
    setMarkdown('')
    setMeta(null)
    setError('')

    abortControllerRef.current = new AbortController()

    await api.streamReport(
      {
        vcf_file_id: vcfFileId,
        hpo_job_uid: hpoJobUid,
        ppi_job_id: ppiJobId,
        hpo_terms: hpoTerms,
        symptom_text: symptomText,
        genes: selectedGenes,
        top_n: 10,
        k: 5,
      },
      (event: unknown) => {
        const e = event as { type: string; [key: string]: unknown }
        
        const eventType = e.type
        
        if (eventType === 'meta') {
          const metaEvent = e as unknown as ReportMeta
          setMeta(metaEvent)
          setRunId(metaEvent.run_id || '')
          setProgress(20)
        } else if (eventType === 'md') {
          const text = (e as unknown as { text: string }).text
          setMarkdown(prev => prev + text)
          setProgress(prev => Math.min(prev + 2, 90))
        } else if (eventType === 'done') {
          const doneEvent = e as unknown as { run_id: string; pdf_url: string }
          setRunId(doneEvent.run_id || runId)
          setPdfUrl(doneEvent.pdf_url || '')
          setProgress(100)
          setStatus('completed')
        } else if (eventType === 'error') {
          const message = (e as unknown as { message: string }).message
          setError(message)
          setStatus('error')
        }
      },
      (err: Error) => {
        setError(err.message)
        setStatus('error')
      },
      () => {
        if (status !== 'completed') {
          setStatus('completed')
        }
      }
    )
  }

  useEffect(() => {
    if (status === 'completed' && runId && onReportGenerated) {
      onReportGenerated({
        run_id: runId,
        pdf_url: pdfUrl,
        markdown: markdown,
        meta: meta || undefined,
      })
    }
  }, [status, runId])

  const handleDownloadPdf = async () => {
    if (!runId) return

    try {
      const blob = await api.downloadReportPdf(runId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `report_${runId}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Failed to download PDF:', err)
    }
  }

  const handleClose = () => {
    abortControllerRef.current?.abort()
    setStatus('idle')
    onClose()
  }

  return (
    <Modal
      title="Gene Prioritization Report"
      open={visible}
      onCancel={handleClose}
      width={900}
      footer={null}
      destroyOnClose
    >
      {status === 'generating' && (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <div style={{ textAlign: 'center', padding: '20px 0' }}>
            <Spin size="large" />
            <div style={{ marginTop: 16 }}>
              <Text>Generating report...</Text>
            </div>
          </div>
          <Progress percent={progress} status="active" />
          {meta && (
            <Alert
              type="info"
              message={
                <Space>
                  <Text>Run ID: {meta.run_id}</Text>
                  <Text>|</Text>
                  <Text>Genes: {meta.genes.length}</Text>
                  {meta.pheno_coverage > 0 && (
                    <>
                      <Text>|</Text>
                      <Text>Pheno Coverage: {(meta.pheno_coverage * 100).toFixed(1)}%</Text>
                    </>
                  )}
                </Space>
              }
            />
          )}
        </Space>
      )}

      {status === 'completed' && (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Alert
            type="success"
            icon={<CheckCircleOutlined />}
            message="Report generated successfully"
            showIcon
          />
          
          {meta && (
            <div style={{ marginBottom: 16 }}>
              <Space split={<Text type="secondary">|</Text>}>
                <Text strong>Run ID: {meta.run_id}</Text>
                <Text>Genes analyzed: {meta.genes.length}</Text>
                {meta.pheno_coverage > 0 && (
                  <Text>Phenotype coverage: {(meta.pheno_coverage * 100).toFixed(1)}%</Text>
                )}
                {meta.ppi_coverage > 0 && (
                  <Text>PPI coverage: {(meta.ppi_coverage * 100).toFixed(1)}%</Text>
                )}
              </Space>
            </div>
          )}

          <div style={{ textAlign: 'right', marginBottom: 16 }}>
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={handleDownloadPdf}
            >
              Download PDF
            </Button>
          </div>

          {markdown && (
            <div
              style={{
                maxHeight: 500,
                overflow: 'auto',
                padding: 16,
                border: '1px solid #f0f0f0',
                borderRadius: 8,
                background: '#fafafa',
              }}
            >
              <ReactMarkdown>{markdown}</ReactMarkdown>
            </div>
          )}
        </Space>
      )}

      {status === 'error' && (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Alert
            type="error"
            icon={<CloseCircleOutlined />}
            message="Report generation failed"
            description={error}
            showIcon
          />
          <Button type="primary" onClick={generateReport}>
            Retry
          </Button>
        </Space>
      )}
    </Modal>
  )
}

export default ReportView
