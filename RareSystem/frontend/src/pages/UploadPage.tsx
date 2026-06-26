import React, { useState } from 'react'
import {
  Layout,
  Typography,
  Steps,
  Card,
  Form,
  Input,
  Select,
  Button,
  Space,
  Row,
  Col,
  Divider,
  Alert,
  Tooltip,
} from 'antd'
import {
  UserOutlined,
  FileTextOutlined,
  MedicineBoxOutlined,
  QuestionCircleOutlined,
} from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import VCFUpload from '@/components/VCFUpload'
import api from '@/services/api'
import type { Patient } from '@/types'

const { Content } = Layout
const { Title, Text, Paragraph } = Typography
const { Step } = Steps
const { TextArea } = Input

interface HpoTermItem {
  phrase: string
  hpo_id: string
  category?: string
  display_category?: string
}

interface UploadPageProps {
  onUploadComplete: (patientId: string, vcfFileId: string, hpoJobId?: string) => void
}

const UploadPage: React.FC<UploadPageProps> = ({ onUploadComplete }) => {
  const { t } = useTranslation()
  const [currentStep, setCurrentStep] = useState(0)
  const [patientForm] = Form.useForm()
  const [patientId, setPatientId] = useState<string | null>(null)
  const [patientInfo, setPatientInfo] = useState<Partial<Patient> & { hpo_terms?: HpoTermItem[] }>({})
  const [vcfFileId, setVcfFileId] = useState<string | null>(null)
  const [hpoJobId, setHpoJobId] = useState<string | null>(null)
  const [directHpoTerms, setDirectHpoTerms] = useState<HpoTermItem[]>([])

  const handlePatientSubmit = async (values: Partial<Patient> & { hpo_input?: string[] }) => {
    const id = `patient_${Date.now()}`
    setPatientId(id)

    const hpoInputIds: string[] = values.hpo_input || []
    const builtHpoTerms: HpoTermItem[] = []

    if (hpoInputIds.length > 0) {
      for (const rawId of hpoInputIds) {
        const formattedId = rawId.toUpperCase().startsWith('HP:') ? rawId.toUpperCase() : `HP:${rawId}`
        builtHpoTerms.push({
          phrase: formattedId,
          hpo_id: formattedId,
          category: 'phenotype',
          display_category: 'primary',
        })
      }
      setDirectHpoTerms(builtHpoTerms)
      setHpoJobId(null)
    } else {
      setDirectHpoTerms([])
      if (values.diagnosis_description) {
        try {
          const result = await api.extractHPOAsync(id, values.diagnosis_description)
          if (result.job_id) {
            setHpoJobId(result.job_id)
          }
        } catch (err) {
          console.error('HPO extraction request failed:', err)
        }
      }
    }

    const patientInfoData = {
      ...values,
      hpo_terms: builtHpoTerms.length > 0 ? builtHpoTerms : undefined,
    }
    setPatientInfo(patientInfoData)

    setCurrentStep(1)
  }

  const handleUploadComplete = (backendPatientId: string, fileId: string) => {
    setPatientId(backendPatientId)
    setVcfFileId(fileId)
    setCurrentStep(2)
  }

  const handleStartAnalysis = () => {
    if (patientId && vcfFileId) {
      onUploadComplete(patientId, vcfFileId, hpoJobId ?? undefined)
    }
  }

  return (
    <Content style={{ padding: '24px 48px' }}>
      <Row justify="center">
        <Col span={20}>
          <Card>
            <Title level={2} style={{ textAlign: 'center', marginBottom: 32 }}>
              {t('upload.title')}
            </Title>

            <Steps current={currentStep} style={{ marginBottom: 32 }}>
              <Step title={t('upload.step1')} icon={<UserOutlined />} />
              <Step title={t('upload.step2')} icon={<FileTextOutlined />} />
              <Step title={t('upload.step3')} icon={<MedicineBoxOutlined />} />
            </Steps>

            {currentStep === 0 && (
              <Card title={t('upload.patientInfoTitle')} style={{ maxWidth: 800, margin: '0 auto' }}>
                <Alert
                  message={t('upload.deidentNotice')}
                  description={t('upload.deidentDesc')}
                  type="info"
                  showIcon
                  style={{ marginBottom: 24 }}
                />

                <Form
                  form={patientForm}
                  layout="vertical"
                  onFinish={handlePatientSubmit}
                  initialValues={{ sex: 'M' }}
                >
                  <Row gutter={16}>
                    <Col span={12}>
                      <Form.Item
                        name="name"
                        label={t('upload.patientId')}
                        rules={[{ required: true, message: t('upload.patientIdRequired') }]}
                      >
                        <Input placeholder={t('upload.patientIdPlaceholder')} />
                      </Form.Item>
                    </Col>
                    <Col span={6}>
                      <Form.Item name="age" label={t('upload.age')}>
                        <Input type="number" placeholder={t('upload.agePlaceholder')} />
                      </Form.Item>
                    </Col>
                    <Col span={6}>
                      <Form.Item name="sex" label={t('upload.sex')}>
                        <Select>
                          <Select.Option value="M">{t('upload.male')}</Select.Option>
                          <Select.Option value="F">{t('upload.female')}</Select.Option>
                          <Select.Option value="Other">{t('upload.other')}</Select.Option>
                        </Select>
                      </Form.Item>
                    </Col>
                  </Row>

                  <Row gutter={16}>
                    <Col span={12}>
                      <Form.Item name="ethnicity" label={t('upload.ethnicity')}>
                        <Input placeholder={t('upload.ethnicityPlaceholder')} />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item
                    name="diagnosis_description"
                    label={t('upload.phenotypeLabel')}
                    rules={[{ required: false }]}
                  >
                    <TextArea
                      rows={4}
                      placeholder={t('upload.phenotypePlaceholder')}
                    />
                  </Form.Item>

                  <Form.Item
                    name="hpo_input"
                    label={
                      <Space>
                        <span>{t('upload.hpoInputLabel')}</span>
                        <Tooltip title={t('upload.hpoInputTooltip')}>
                          <QuestionCircleOutlined style={{ color: '#1890ff' }} />
                        </Tooltip>
                      </Space>
                    }
                    extra={t('upload.hpoInputExtra')}
                  >
                    <Select
                      mode="tags"
                      placeholder={t('upload.hpoInputPlaceholder')}
                      tokenSeparators={[',', ' ', ';']}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>

                  <Form.Item name="medical_history" label={t('upload.historyLabel')}>
                    <TextArea
                      rows={3}
                      placeholder={t('upload.historyPlaceholder')}
                    />
                  </Form.Item>

                  <Form.Item>
                    <Button type="primary" htmlType="submit" block>
                      {t('upload.continueBtn')}
                    </Button>
                  </Form.Item>
                </Form>
              </Card>
            )}

            {currentStep === 1 && (
              <VCFUpload
                patientId={patientId!}
                patientInfo={patientInfo}
                hpoJobId={hpoJobId ?? undefined}
                directHpoTerms={directHpoTerms.length > 0 ? directHpoTerms : undefined}
                onUploadComplete={handleUploadComplete}
              />
            )}

            {currentStep === 2 && (
              <Card style={{ textAlign: 'center', maxWidth: 600, margin: '0 auto' }}>
                <MedicineBoxOutlined style={{ fontSize: 64, color: '#52c41a', marginBottom: 24 }} />
                <Title level={3}>{t('upload.readyTitle')}</Title>
                <Paragraph>
                  {t('upload.readyDesc')}
                </Paragraph>
                <Divider />
                <Space direction="vertical" style={{ width: '100%' }} size="large">
                  <div>
                    <Text strong>{t('upload.patientIdLabel')}</Text>
                    <Text>{patientId}</Text>
                  </div>
                  <div>
                    <Text strong>{t('upload.vcfFileIdLabel')}</Text>
                    <Text>{vcfFileId}</Text>
                  </div>
                  <Button type="primary" size="large" onClick={handleStartAnalysis} block>
                    {t('upload.startAnalysisBtn')}
                  </Button>
                </Space>
              </Card>
            )}
          </Card>
        </Col>
      </Row>
    </Content>
  )
}

export default UploadPage
