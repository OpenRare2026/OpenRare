import React from 'react'
import { useTranslation } from 'react-i18next'
import {
  Card,
  Typography,
  Space,
  Tag,
  Button,
  List,
  Empty,
  Popconfirm,
} from 'antd'
import {
  FileTextOutlined,
  DownloadOutlined,
  DeleteOutlined,
  FilePdfOutlined,
} from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import { useAppStore } from '@/store'
import api from '@/services/api'

const { Text } = Typography

interface DualTrackReportProps {
  sessionId?: string
}

const DualTrackReport: React.FC<DualTrackReportProps> = () => {
  const { t } = useTranslation()
  const { geneAnalysisReports, removeGeneAnalysisReport } = useAppStore()

  const handleDownloadPdf = async (runId: string) => {
    try {
      const blob = await api.downloadReportPdf(runId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `gene_analysis_report_${runId}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Failed to download PDF:', error)
    }
  }

  if (geneAnalysisReports.length === 0) {
    return (
      <Card
        title={
          <Space>
            <FileTextOutlined />
            <span>{t('report.researchTab') || 'Research Reports'}</span>
          </Space>
        }
      >
        <Empty description={t('report.noGeneAnalysis') || 'No gene analysis reports generated yet'}>
          <Text type="secondary">{t('report.generateFromGeneView') || 'Click "Generate Report" in GeneView to create reports'}</Text>
        </Empty>
      </Card>
    )
  }

  return (
    <Card
      title={
        <Space>
          <FileTextOutlined />
          <span>{t('report.researchTab') || 'Research Reports'}</span>
          <Tag color="blue">{geneAnalysisReports.length}</Tag>
        </Space>
      }
    >
      <List
        itemLayout="vertical"
        dataSource={geneAnalysisReports}
        renderItem={(report) => (
          <List.Item
            key={report.id}
            extra={
              <Space direction="vertical">
                <Button 
                  type="primary" 
                  icon={<DownloadOutlined />}
                  onClick={() => handleDownloadPdf(report.run_id)}
                >
                  {t('report.downloadPdf') || 'Download PDF'}
                </Button>
                <Popconfirm
                  title={t('report.confirmDelete') || 'Delete this report?'}
                  onConfirm={() => removeGeneAnalysisReport(report.id)}
                  okText={t('common.yes') || 'Yes'}
                  cancelText={t('common.no') || 'No'}
                >
                  <Button danger icon={<DeleteOutlined />} size="small">
                    {t('common.delete') || 'Delete'}
                  </Button>
                </Popconfirm>
              </Space>
            }
          >
            <List.Item.Meta
              title={
                <Space>
                  <FilePdfOutlined />
                  <Text strong>{t('report.reportId') || 'Report ID'}: {report.run_id}</Text>
                  <Tag color="blue">{report.meta?.genes?.length || 0} genes</Tag>
                </Space>
              }
              description={
                <Space>
                  <Text type="secondary">
                    {new Date(report.created_at).toLocaleString()}
                  </Text>
                  {report.meta?.pheno_coverage !== undefined && report.meta.pheno_coverage > 0 && (
                    <Tag>Pheno: {(report.meta.pheno_coverage * 100).toFixed(0)}%</Tag>
                  )}
                  {report.meta?.ppi_coverage !== undefined && report.meta.ppi_coverage > 0 && (
                    <Tag>PPI: {(report.meta.ppi_coverage * 100).toFixed(0)}%</Tag>
                  )}
                </Space>
              }
            />
            <div style={{ maxHeight: 200, overflow: 'auto', padding: 8, background: '#fafafa', borderRadius: 4 }}>
              <ReactMarkdown>{report.markdown.slice(0, 500) + '...'}</ReactMarkdown>
            </div>
          </List.Item>
        )}
      />
    </Card>
  )
}

export default DualTrackReport
