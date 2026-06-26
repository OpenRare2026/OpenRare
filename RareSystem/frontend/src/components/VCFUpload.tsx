import React, { useState, useEffect, useRef } from 'react'
import { Upload, Button, Card, Alert, Progress, Typography, Space, Collapse, Tag, InputNumber, Input, Spin } from 'antd'
import { InboxOutlined, FileTextOutlined, CheckCircleOutlined, ExperimentOutlined, LoadingOutlined } from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import type { UploadProps, UploadFile } from 'antd/es/upload/interface'
import api from '@/services/api'

const { Dragger } = Upload
const { Text } = Typography
const { Panel } = Collapse

interface PatientInfo {
  name?: string
  age?: number
  sex?: string
  ethnicity?: string
  diagnosis_description?: string
  medical_history?: string
  hpo_terms?: Array<{ phrase: string; hpo_id: string; category?: string; display_category?: string }>
}

interface VCFUploadProps {
  patientId: string
  patientInfo?: PatientInfo
  hpoJobId?: string
  directHpoTerms?: Array<{ phrase: string; hpo_id: string; category?: string; display_category?: string }>
  onUploadComplete: (patientId: string, vcfFileId: string) => void
}

const VCFUpload: React.FC<VCFUploadProps> = ({ patientId, patientInfo, hpoJobId, directHpoTerms, onUploadComplete }) => {
  const { t } = useTranslation()
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [preview, setPreview] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)
  const [vepStatus, setVepStatus] = useState<string | null>(null)
  const [vepChromosomes, setVepChromosomes] = useState('')
  const [vepFork, setVepFork] = useState(16)
  const [vepJobId, setVepJobId] = useState<string | null>(null)
  const [vepPolling, setVepPolling] = useState(false)
  const [vepElapsedSeconds, setVepElapsedSeconds] = useState(0)
  const [vepAnnotatedCount, setVepAnnotatedCount] = useState<number | null>(null)
  const [hpoWaiting, setHpoWaiting] = useState(false)
  const [hpoStatus, setHpoStatus] = useState<string | null>(null)
  const [hpoElapsedSeconds, setHpoElapsedSeconds] = useState(0)
  const pollingRef = useRef<NodeJS.Timeout | null>(null)
  const elapsedRef = useRef<NodeJS.Timeout | null>(null)
  const hpoPollingRef = useRef<NodeJS.Timeout | null>(null)
  const hpoElapsedRef = useRef<NodeJS.Timeout | null>(null)
  const startTimeRef = useRef<number>(0)
  const hpoStartTimeRef = useRef<number>(0)

  const needHpoWait = !!hpoJobId && !directHpoTerms

  const handlePreview = async (file: File) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const text = e.target?.result as string
      const lines = text.split('\n').slice(0, 50)
      setPreview(lines)
    }
    reader.readAsText(file)
  }

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    accept: '.vcf,.vcf.gz',
    fileList,
    beforeUpload: (file) => {
      setFileList([file as unknown as UploadFile])
      handlePreview(file)
      return false
    },
    onRemove: () => {
      setFileList([])
      setPreview([])
    },
  }

  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current)
      if (elapsedRef.current) clearInterval(elapsedRef.current)
      if (hpoPollingRef.current) clearInterval(hpoPollingRef.current)
      if (hpoElapsedRef.current) clearInterval(hpoElapsedRef.current)
    }
  }, [])

  const startVepPolling = (jobId: string, vcfFileId: string, patientId: string) => {
    setVepPolling(true)
    startTimeRef.current = Date.now()
    setVepElapsedSeconds(0)

    elapsedRef.current = setInterval(() => {
      setVepElapsedSeconds(Math.floor((Date.now() - startTimeRef.current) / 1000))
    }, 1000)

    pollingRef.current = setInterval(async () => {
      try {
        const status = await api.getVEPJobStatus(jobId)
        setVepStatus(status.status)
        if (status.vep_annotated_count != null) {
          setVepAnnotatedCount(status.vep_annotated_count)
        }

        const completedStates = ['completed', 'completion', 'success', 'succeeded', 'finished', 'done']
        const failedStates = ['failed', 'timeout', 'error']

        if (completedStates.includes(status.status)) {
          if (pollingRef.current) clearInterval(pollingRef.current)
          if (elapsedRef.current) clearInterval(elapsedRef.current)
          setVepPolling(false)
          setTimeout(() => {
            onUploadComplete(patientId, vcfFileId)
          }, 500)
        } else if (failedStates.includes(status.status)) {
          if (pollingRef.current) clearInterval(pollingRef.current)
          if (elapsedRef.current) clearInterval(elapsedRef.current)
          setVepPolling(false)
          setError(`VEP annotation ${status.status}: ${status.error || 'Unknown error'}`)
        }
      } catch (err) {
        console.error('Failed to poll VEP status:', err)
      }
    }, 10000)
  }

  const waitForHpoAndSubmitVep = async (vcfFileId: string, hpoJobId: string) => {
    setHpoWaiting(true)
    hpoStartTimeRef.current = Date.now()
    setHpoElapsedSeconds(0)

    hpoElapsedRef.current = setInterval(() => {
      setHpoElapsedSeconds(Math.floor((Date.now() - hpoStartTimeRef.current) / 1000))
    }, 1000)

    hpoPollingRef.current = setInterval(async () => {
      try {
        const hpoResult = await api.getHPOJobStatus(hpoJobId)
        setHpoStatus(hpoResult.status)

        if (hpoResult.status === 'completed') {
          if (hpoPollingRef.current) clearInterval(hpoPollingRef.current)
          if (hpoElapsedRef.current) clearInterval(hpoElapsedRef.current)

          const extractedHpoIds = (hpoResult.results || []).map((r: { hpo_id: string }) => r.hpo_id)

          try {
            const vepResult = await api.submitVEPForVcf(Number(vcfFileId), extractedHpoIds, {
              fork: vepFork,
              chromosomes: vepChromosomes || undefined,
            })

            if (vepResult.vep_job_id) {
              setVepJobId(vepResult.vep_job_id)
              setVepStatus(vepResult.vep_status)
              setHpoWaiting(false)
              startVepPolling(vepResult.vep_job_id, vcfFileId, patientId)
            } else {
              setHpoWaiting(false)
              setTimeout(() => {
                onUploadComplete(patientId, vcfFileId)
              }, 500)
            }
          } catch (vepErr) {
            setHpoWaiting(false)
            setError(vepErr instanceof Error ? vepErr.message : 'VEP submission failed after HPO extraction')
          }
        } else if (hpoResult.status === 'failed') {
          if (hpoPollingRef.current) clearInterval(hpoPollingRef.current)
          if (hpoElapsedRef.current) clearInterval(hpoElapsedRef.current)
          setHpoWaiting(false)
          setError(`HPO extraction failed: ${hpoResult.error || 'Unknown error'}`)
        }
      } catch (err) {
        console.error('Failed to poll HPO status:', err)
      }
    }, 5000)
  }

  const handleUpload = async () => {
    if (fileList.length === 0) return

    const file = fileList[0] as unknown as File
    setUploading(true)
    setError(null)
    setProgress(0)
    setVepStatus(null)
    setVepJobId(null)
    setVepPolling(false)
    setVepElapsedSeconds(0)
    setVepAnnotatedCount(null)

    const vepOptions = {
      fork: vepFork,
      chromosomes: vepChromosomes || undefined,
    }

    try {
      if (directHpoTerms && directHpoTerms.length > 0) {
        const hpoTermsForUpload = directHpoTerms
        const result = await api.uploadVCF(file, patientId, setProgress, { ...patientInfo, hpo_terms: hpoTermsForUpload }, vepOptions, undefined)
        setProgress(100)
        if (result.vep_status) setVepStatus(result.vep_status)
        if (result.vep_job_id) {
          setVepJobId(result.vep_job_id)
          setUploading(false)
          startVepPolling(result.vep_job_id, result.vcf_file_id, result.patient_id)
        } else {
          setUploading(false)
          setTimeout(() => {
            onUploadComplete(result.patient_id, result.vcf_file_id)
          }, 500)
        }
      } else if (needHpoWait) {
        const result = await api.uploadVCF(file, patientId, setProgress, patientInfo, vepOptions, hpoJobId)
        setProgress(100)
        setUploading(false)
        waitForHpoAndSubmitVep(result.vcf_file_id, hpoJobId)
      } else {
        const result = await api.uploadVCF(file, patientId, setProgress, patientInfo, vepOptions, hpoJobId)
        setProgress(100)
        if (result.vep_status) setVepStatus(result.vep_status)
        if (result.vep_job_id) {
          setVepJobId(result.vep_job_id)
          setUploading(false)
          startVepPolling(result.vep_job_id, result.vcf_file_id, result.patient_id)
        } else {
          setUploading(false)
          setTimeout(() => {
            onUploadComplete(result.patient_id, result.vcf_file_id)
          }, 500)
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
      setUploading(false)
    }
  }

  const formatElapsedTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`
  }

  const isProcessing = uploading || vepPolling || hpoWaiting

  const headerLines = preview.filter((l) => l.startsWith('#'))
  const dataLines = preview.filter((l) => !l.startsWith('#') && l.trim())

  return (
    <Card
      title={
        <Space>
          <FileTextOutlined />
          <span>{t('vcfUpload.title')}</span>
        </Space>
      }
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {error && (
          <Alert
            message={t('vcfUpload.uploadError')}
            description={error}
            type="error"
            closable
            onClose={() => setError(null)}
          />
        )}

        {directHpoTerms && directHpoTerms.length > 0 && (
          <Alert
            message={t('vcfUpload.hpoDirectLabel')}
            description={
              <Space wrap>
                {directHpoTerms.map((term) => (
                  <Tag key={term.hpo_id} color="processing">{term.hpo_id}</Tag>
                ))}
              </Space>
            }
            type="info"
            showIcon
          />
        )}

        {needHpoWait && !hpoWaiting && (
          <Alert
            message={t('vcfUpload.hpoExtractionPending')}
            description={t('vcfUpload.hpoExtractionPendingDesc')}
            type="info"
            showIcon
          />
        )}

        <Dragger {...uploadProps}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">{t('vcfUpload.dragHint')}</p>
          <p className="ant-upload-hint">
            {t('vcfUpload.supportHint')}
          </p>
        </Dragger>

        <Collapse defaultActiveKey={['vep-options']}>
          <Panel header={<Space><ExperimentOutlined />VEP Annotation Options</Space>} key="vep-options">
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>Parallel forks</span>
                <InputNumber min={1} max={32} value={vepFork} onChange={(v) => setVepFork(v || 16)} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>Chromosomes (optional)</span>
                <Input
                  placeholder="e.g. 1-22,X"
                  value={vepChromosomes}
                  onChange={(e) => setVepChromosomes(e.target.value)}
                  style={{ width: 180 }}
                />
              </div>
            </Space>
          </Panel>
        </Collapse>

        {hpoWaiting && (
          <Card size="small" style={{ background: '#fff7e6', borderColor: '#ffd591' }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Spin indicator={<LoadingOutlined style={{ fontSize: 16 }} spin />} />
                <Text strong>{t('vcfUpload.hpoWaitingTitle')}</Text>
              </div>
              <div>
                <Text type="secondary">{t('vcfUpload.hpoStatus')}: </Text>
                <Tag color={hpoStatus === 'queued' ? 'blue' : hpoStatus === 'processing' ? 'orange' : 'default'}>
                  {hpoStatus || 'queued'}
                </Tag>
              </div>
              <div>
                <Text type="secondary">{t('vcfUpload.elapsed')}: </Text>
                <Text>{formatElapsedTime(hpoElapsedSeconds)}</Text>
              </div>
              <Progress
                percent={100}
                status="active"
                strokeColor={{ '0%': '#fa8c16', '100%': '#52c41a' }}
                format={() => t('vcfUpload.hpoWaitingProgress')}
              />
            </Space>
          </Card>
        )}

        {vepPolling && vepJobId && (
          <Card size="small" style={{ background: '#f0f5ff', borderColor: '#adc6ff' }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Spin indicator={<LoadingOutlined style={{ fontSize: 16 }} spin />} />
                <Text strong>VEP Annotation in Progress</Text>
              </div>
              <div>
                <Text type="secondary">Status: </Text>
                <Tag color={vepStatus === 'queued' || vepStatus === 'queuing' ? 'blue' : vepStatus === 'processing' || vepStatus === 'running' ? 'orange' : 'default'}>
                  {vepStatus || 'queued'}
                </Tag>
              </div>
              <div>
                <Text type="secondary">Elapsed: </Text>
                <Text>{formatElapsedTime(vepElapsedSeconds)}</Text>
              </div>
              {vepAnnotatedCount !== null && vepAnnotatedCount > 0 && (
                <div>
                  <Text type="secondary">Variants annotated: </Text>
                  <Text>{vepAnnotatedCount}</Text>
                </div>
              )}
              <Progress
                percent={100}
                status="active"
                strokeColor={{ '0%': '#108ee9', '100%': '#87d068' }}
                format={() => 'Waiting for VEP...'}
              />
            </Space>
          </Card>
        )}

        {vepStatus && !vepPolling && (
          <Alert
            message={
              vepStatus === 'completed'
                ? 'VEP annotation completed'
                : vepStatus === 'failed'
                ? 'VEP annotation failed, using local annotation'
                : vepStatus === 'timeout'
                ? 'VEP annotation timed out, using local annotation'
                : `VEP status: ${vepStatus}`
            }
            type={vepStatus === 'completed' ? 'success' : vepStatus === 'failed' || vepStatus === 'timeout' ? 'warning' : 'info'}
            showIcon
            closable
            onClose={() => setVepStatus(null)}
          />
        )}

        {preview.length > 0 && (
          <Collapse defaultActiveKey={['info']}>
            <Panel header={t('vcfUpload.preview')} key="info">
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <Text strong>{t('vcfUpload.headerLines')}</Text>
                  <Tag color="blue">{headerLines.length}</Tag>
                </div>

                <div>
                  <Text strong>{t('vcfUpload.sampleLines')}</Text>
                  <div
                    style={{
                      background: '#f5f5f5',
                      padding: 12,
                      borderRadius: 4,
                      fontFamily: 'monospace',
                      fontSize: 12,
                      maxHeight: 200,
                      overflow: 'auto',
                      marginTop: 8,
                    }}
                  >
                    {dataLines.slice(0, 10).map((line, idx) => (
                      <div key={idx} style={{ marginBottom: 4 }}>
                        {line}
                      </div>
                    ))}
                  </div>
                </div>
              </Space>
            </Panel>
          </Collapse>
        )}

        {uploading && (
          <Progress
            percent={progress}
            status={progress < 100 ? 'active' : 'success'}
            strokeColor={{
              '0%': '#108ee9',
              '100%': '#87d068',
            }}
          />
        )}

        <Button
          type="primary"
          onClick={handleUpload}
          disabled={fileList.length === 0 || isProcessing}
          loading={isProcessing}
          icon={progress === 100 && !isProcessing ? <CheckCircleOutlined /> : undefined}
          block
        >
          {uploading
            ? 'Uploading...'
            : hpoWaiting
            ? t('vcfUpload.hpoWaitingBtn')
            : vepPolling
            ? 'VEP processing...'
            : progress === 100
            ? t('vcfUpload.uploadComplete')
            : t('vcfUpload.startUpload')}
        </Button>
      </Space>
    </Card>
  )
}

export default VCFUpload
