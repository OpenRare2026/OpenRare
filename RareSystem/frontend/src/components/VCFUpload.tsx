import React, { useState, useEffect, useRef } from 'react'
import { Upload, Button, Card, Alert, Progress, Typography, Space, Collapse, Tag, Switch, InputNumber, Select, Spin } from 'antd'
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
  hpo_terms?: Array<{ phrase: string; hpo_id: string }>
}

interface VCFUploadProps {
  patientId: string
  patientInfo?: PatientInfo
  hpoJobId?: string
  onUploadComplete: (patientId: string, vcfFileId: string) => void
}

const VCFUpload: React.FC<VCFUploadProps> = ({ patientId, patientInfo, hpoJobId, onUploadComplete }) => {
  const { t } = useTranslation()
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [preview, setPreview] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)
  const [vepStatus, setVepStatus] = useState<string | null>(null)
  const [vepHgvs, setVepHgvs] = useState(true)
  const [vepNoPick, setVepNoPick] = useState(false)
  const [vepFormat, setVepFormat] = useState('vcf')
  const [vepFork, setVepFork] = useState(1)
  const [vepJobId, setVepJobId] = useState<string | null>(null)
  const [vepPolling, setVepPolling] = useState(false)
  const [vepElapsedSeconds, setVepElapsedSeconds] = useState(0)
  const [vepAnnotatedCount, setVepAnnotatedCount] = useState<number | null>(null)
  const pollingRef = useRef<NodeJS.Timeout | null>(null)
  const elapsedRef = useRef<NodeJS.Timeout | null>(null)
  const startTimeRef = useRef<number>(0)

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
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
      }
      if (elapsedRef.current) {
        clearInterval(elapsedRef.current)
      }
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
        if (status.vep_annotated_count !== null) {
          setVepAnnotatedCount(status.vep_annotated_count)
        }

        const completedStates = ['completed', 'completion', 'success', 'finished', 'done']
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

    try {
      const result = await api.uploadVCF(file, patientId, setProgress, patientInfo, {
        hgvs: vepHgvs,
        no_pick: vepNoPick,
        format: vepFormat,
        fork: vepFork,
      }, hpoJobId)
      setProgress(100)
      if (result.vep_status) {
        setVepStatus(result.vep_status)
      }
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
                <span>HGVS notation</span>
                <Switch checked={vepHgvs} onChange={setVepHgvs} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>No pick (all consequences)</span>
                <Switch checked={vepNoPick} onChange={setVepNoPick} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>Output format</span>
                <Select value={vepFormat} onChange={setVepFormat} style={{ width: 120 }}>
                  <Select.Option value="vcf">VCF</Select.Option>
                  <Select.Option value="json">JSON</Select.Option>
                </Select>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>Parallel forks</span>
                <InputNumber min={1} max={8} value={vepFork} onChange={(v) => setVepFork(v || 1)} />
              </div>
            </Space>
          </Panel>
        </Collapse>

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
          disabled={fileList.length === 0 || uploading || vepPolling}
          loading={uploading || vepPolling}
          icon={progress === 100 && !vepPolling ? <CheckCircleOutlined /> : undefined}
          block
        >
          {uploading
            ? 'Uploading...'
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
