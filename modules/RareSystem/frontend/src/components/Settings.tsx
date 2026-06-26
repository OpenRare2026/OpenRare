import React, { useState, useEffect } from 'react'
import {
  Card,
  Form,
  Input,
  Select,
  Slider,
  InputNumber,
  Button,
  Space,
  message,
  Divider,
  Typography,
  Spin,
  Alert,
  Tabs,
  Table,
  Switch,
  Tag,
  Modal,
  Collapse,
  Tooltip,
} from 'antd'
import { SaveOutlined, ReloadOutlined, ExperimentOutlined, SearchOutlined, MedicineBoxOutlined, BookOutlined, ApartmentOutlined, SettingOutlined, QuestionCircleOutlined } from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import api from '@/services/api'
import type { LLMSettings, ProviderInfo } from '@/store'
import type { Skill, ConfigSchemaField } from '@/types'

const { Title, Text } = Typography
const { Option } = Select
const { Password } = Input
const { Panel } = Collapse

interface SettingsFormValues {
  provider: string
  api_key: string
  model: string
  base_url?: string
  temperature: number
  max_tokens: number
}

const NUMERIC_PATIENT_ID = 1

const Settings: React.FC = () => {
  const { t } = useTranslation()
  const [form] = Form.useForm()
  const [skillConfigForm] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [providers, setProviders] = useState<ProviderInfo[]>([])
  const [currentSettings, setCurrentSettings] = useState<LLMSettings | null>(null)
  const [selectedProvider, setSelectedProvider] = useState<string>('openai')
  const [skills, setSkills] = useState<Skill[]>([])
  const [skillsLoading, setSkillsLoading] = useState(false)
  const [configModalVisible, setConfigModalVisible] = useState(false)
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null)
  const [savingSkillConfig, setSavingSkillConfig] = useState(false)

  useEffect(() => {
    loadProviders()
    loadSettings()
    loadSkills()
  }, [])

  const loadSkills = async () => {
    setSkillsLoading(true)
    try {
      const skillList = await api.getSkills()
      setSkills(skillList)
      const configs = await api.getSkillConfigs()
      void configs
    } catch {
      // Skills may not be available yet
    } finally {
      setSkillsLoading(false)
    }
  }

  const handleSkillToggle = async (skillName: string, enabled: boolean) => {
    try {
      await api.updateSkillConfig(skillName, { is_enabled: enabled })
      setSkills(prev => prev.map(s =>
        s.name === skillName ? { ...s, is_enabled: enabled } : s
      ))
      message.success(`${skillName} ${enabled ? 'enabled' : 'disabled'}`)
    } catch {
      message.error('Failed to update skill config')
    }
  }

  const openSkillConfig = (skill: Skill) => {
    setSelectedSkill(skill)
    skillConfigForm.setFieldsValue(skill.config || {})
    setConfigModalVisible(true)
  }

  const handleSaveSkillConfig = async (values: Record<string, string | number | boolean>) => {
    if (!selectedSkill) return
    
    setSavingSkillConfig(true)
    try {
      await api.updateSkillConfig(selectedSkill.name, { 
        is_enabled: selectedSkill.is_enabled,
        config: values 
      })
      setSkills(prev => prev.map(s =>
        s.name === selectedSkill.name ? { ...s, config: values } : s
      ))
      message.success(`${selectedSkill.name} configuration saved`)
      setConfigModalVisible(false)
    } catch {
      message.error('Failed to save skill configuration')
    } finally {
      setSavingSkillConfig(false)
    }
  }

  const renderConfigField = (fieldName: string, field: ConfigSchemaField) => {
    const labelWithTooltip = (
      <Space size={4}>
        {field.label}
        {field.description && (
          <Tooltip title={field.description}>
            <QuestionCircleOutlined style={{ color: '#999', fontSize: 12 }} />
          </Tooltip>
        )}
      </Space>
    )

    switch (field.type) {
      case 'string':
        return (
          <Form.Item
            key={fieldName}
            name={fieldName}
            label={labelWithTooltip}
            rules={[{ required: field.required, message: `Please enter ${field.label}` }]}
          >
            <Input placeholder={field.placeholder} />
          </Form.Item>
        )
      case 'integer':
        return (
          <Form.Item
            key={fieldName}
            name={fieldName}
            label={labelWithTooltip}
            rules={[{ required: field.required, message: `Please enter ${field.label}` }]}
          >
            <InputNumber 
              min={field.min} 
              max={field.max} 
              style={{ width: '100%' }} 
              placeholder={field.placeholder}
            />
          </Form.Item>
        )
      case 'float':
        return (
          <Form.Item
            key={fieldName}
            name={fieldName}
            label={labelWithTooltip}
            rules={[{ required: field.required, message: `Please enter ${field.label}` }]}
          >
            <InputNumber 
              min={field.min} 
              max={field.max} 
              step={field.step || 0.1}
              style={{ width: '100%' }} 
              placeholder={field.placeholder}
            />
          </Form.Item>
        )
      case 'select':
        return (
          <Form.Item
            key={fieldName}
            name={fieldName}
            label={labelWithTooltip}
            rules={[{ required: field.required, message: `Please select ${field.label}` }]}
          >
            <Select placeholder={`Select ${field.label}`}>
              {field.options?.map(opt => (
                <Option key={opt.value} value={opt.value}>{opt.label}</Option>
              ))}
            </Select>
          </Form.Item>
        )
      case 'textarea':
        return (
          <Form.Item
            key={fieldName}
            name={fieldName}
            label={labelWithTooltip}
            rules={[{ required: field.required, message: `Please enter ${field.label}` }]}
          >
            <Input.TextArea 
              rows={field.rows || 4} 
              placeholder={field.placeholder}
            />
          </Form.Item>
        )
      default:
        return null
    }
  }

  const renderConfigFieldsGrouped = () => {
    if (!selectedSkill?.config_schema) return null

    const groups: Record<string, { label: string; fields: [string, ConfigSchemaField][] }> = {}
    
    Object.entries(selectedSkill.config_schema).forEach(([fieldName, field]) => {
      const groupKey = field.group || 'general'
      if (!groups[groupKey]) {
        groups[groupKey] = {
          label: field.group_label || 'General',
          fields: []
        }
      }
      groups[groupKey].fields.push([fieldName, field])
    })

    return Object.entries(groups).map(([groupKey, group]) => (
      <Panel header={group.label} key={groupKey}>
        {group.fields.map(([fieldName, field]) => renderConfigField(fieldName, field))}
      </Panel>
    ))
  }

  const loadProviders = async () => {
    try {
      const response = await api.getProviders()
      setProviders(response)
    } catch (error) {
      console.error('Failed to load providers:', error)
    }
  }

  const loadSettings = async () => {
    setLoading(true)
    try {
      const settings = await api.getLLMSettings(NUMERIC_PATIENT_ID)
      setCurrentSettings(settings)
      form.setFieldsValue({
        provider: settings.provider,
        api_key: '********',
        model: settings.model,
        base_url: settings.base_url || '',
        temperature: settings.temperature,
        max_tokens: settings.max_tokens,
      })
      setSelectedProvider(settings.provider)
    } catch (error: any) {
      if (error?.status !== 404) {
        message.error('Failed to load settings')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleProviderChange = (provider: string) => {
    setSelectedProvider(provider)
    const providerInfo = providers.find((p) => p.code === provider)
    if (provider !== 'custom' && providerInfo && providerInfo.models.length > 0) {
      form.setFieldsValue({ model: providerInfo.models[0] })
    } else {
      form.setFieldsValue({ model: '' })
    }
    if (provider !== 'custom') {
      form.setFieldsValue({ base_url: undefined })
    }
  }

  const handleSave = async (values: SettingsFormValues) => {
    setSaving(true)
    try {
      await api.saveLLMSettings(NUMERIC_PATIENT_ID, {
        provider: values.provider,
        api_key: values.api_key,
        model: values.model,
        base_url: values.base_url || null,
        temperature: values.temperature,
        max_tokens: values.max_tokens,
      })
      message.success('Settings saved successfully')
      loadSettings()
    } catch (error) {
      message.error('Failed to save settings')
    } finally {
      setSaving(false)
    }
  }

  const handleReset = () => {
    form.resetFields()
    loadSettings()
  }

  const selectedProviderInfo = providers.find((p) => p.code === selectedProvider)
  const showBaseUrl = selectedProvider === 'custom' || selectedProvider === 'openai'

  if (loading) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>
            <Text>Loading settings...</Text>
          </div>
        </div>
      </Card>
    )
  }

  const skillIconMap: Record<string, React.ReactNode> = {
    experiment: <ExperimentOutlined />,
    search: <SearchOutlined />,
    'medicine-box': <MedicineBoxOutlined />,
    book: <BookOutlined />,
    apartment: <ApartmentOutlined />,
  }

  const skillColumns = [
    {
      title: 'Skill',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: Skill) => (
        <Space>
          <span style={{ fontSize: 16 }}>{skillIconMap[record.icon] || <ExperimentOutlined />}</span>
          <div>
            <div><Text strong>{name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</Text></div>
            <Text type="secondary" style={{ fontSize: 11 }}>{record.description}</Text>
          </div>
        </Space>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'skill_type',
      key: 'skill_type',
      width: 100,
      render: (type: string) => (
        <Tag color={type === 'prompt_injection' ? 'blue' : 'green'}>
          {type === 'prompt_injection' ? t('settings.aiAnalysis') : t('settings.dataQuery')}
        </Tag>
      ),
    },
    {
      title: 'Enabled',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      width: 80,
      render: (enabled: boolean, record: Skill) => (
        <Switch checked={enabled} onChange={(v) => handleSkillToggle(record.name, v)} size="small" />
      ),
    },
    {
      title: 'Config',
      key: 'config',
      width: 80,
      render: (_: unknown, record: Skill) => (
        <Button 
          type="link" 
          size="small"
          icon={<SettingOutlined />}
          onClick={() => openSkillConfig(record)}
          disabled={Object.keys(record.config_schema || {}).length === 0}
        >
          Configure
        </Button>
      ),
    },
  ]

  return (
    <>
    <Tabs
      defaultActiveKey="llm"
      items={[
        {
          key: 'llm',
          label: 'LLM Settings',
          children: (
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <Card>
                <Title level={3} style={{ marginBottom: 24 }}>
                  LLM Settings
        </Title>

        <Alert
          message="Configure Large Language Model for Case Q&A"
          description="Select your preferred LLM provider and enter your API key. The model will be used to answer questions about genetic variants and patient cases."
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
          initialValues={{
            provider: 'openai',
            model: 'gpt-4o-mini',
            temperature: 0.7,
            max_tokens: 1024,
          }}
        >
          <Form.Item
            name="provider"
            label="LLM Provider"
            rules={[{ required: true, message: 'Please select a provider' }]}
          >
            <Select onChange={handleProviderChange} placeholder="Select provider">
              {providers.map((p) => (
                <Option key={p.code} value={p.code}>
                  {p.name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="api_key"
            label="API Key"
            rules={[{ required: selectedProvider !== 'ollama' && selectedProvider !== 'custom', message: 'Please enter your API key' }]}
          >
            <Password placeholder={selectedProvider === 'ollama' ? 'Not required for Ollama' : 'Enter your API key'} />
          </Form.Item>

          <Form.Item
            name="model"
            label="Model"
            rules={[{ required: true, message: selectedProvider === 'custom' ? 'Please enter a model name' : 'Please select a model' }]}
          >
            {selectedProvider === 'custom' ? (
              <Input placeholder="Enter model name (e.g., deepseek-chat, qwen2.5-72b)" />
            ) : (
              <Select placeholder="Select model">
                {selectedProviderInfo?.models.map((m) => (
                  <Option key={m} value={m}>
                    {m}
                  </Option>
                ))}
              </Select>
            )}
          </Form.Item>

          {showBaseUrl && (
            <Form.Item
              name="base_url"
              label="Base URL (Optional)"
              extra="Custom API endpoint URL (e.g., for OpenAI Enterprise or self-hosted models)"
            >
              <Input placeholder="https://api.openai.com/v1" />
            </Form.Item>
          )}

          <Divider />

          <Form.Item name="temperature" label="Temperature">
            <Slider min={0} max={2} step={0.1} marks={{ 0: '0', 1: '1', 2: '2' }} />
          </Form.Item>

          <Form.Item name="max_tokens" label="Max Tokens">
            <InputNumber min={1} max={32768} style={{ width: '100%' }} />
          </Form.Item>

          <Divider />

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={saving}>
                Save Settings
              </Button>
              <Button icon={<ReloadOutlined />} onClick={handleReset}>
                Reset
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      {currentSettings && (
        <Card title="Current Configuration">
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <Text strong>Provider: </Text>
              <Text>{currentSettings.provider_name || currentSettings.provider}</Text>
            </div>
            <div>
              <Text strong>Model: </Text>
              <Text>{currentSettings.model}</Text>
            </div>
            <div>
              <Text strong>Temperature: </Text>
              <Text>{currentSettings.temperature}</Text>
            </div>
            <div>
              <Text strong>Max Tokens: </Text>
              <Text>{currentSettings.max_tokens}</Text>
            </div>
            <div>
              <Text strong>Last Updated: </Text>
              <Text>{new Date(currentSettings.updated_at).toLocaleString()}</Text>
            </div>
          </Space>
        </Card>
      )}
    </Space>
          ),
        },
        {
          key: 'skills',
          label: 'Skills',
          children: (
            <Card>
              <Title level={3} style={{ marginBottom: 24 }}>Skills Configuration</Title>
              <Alert
                message="Skills are global settings that apply to all patients"
                type="info"
                showIcon
                style={{ marginBottom: 16 }}
              />
              <Table
                dataSource={skills}
                columns={skillColumns}
                rowKey="name"
                loading={skillsLoading}
                pagination={false}
                size="middle"
              />
            </Card>
          ),
        },
      ]}
    />

    <Modal
      title={
        <Space>
          <SettingOutlined />
          {selectedSkill?.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} Configuration
        </Space>
      }
      open={configModalVisible}
      onCancel={() => setConfigModalVisible(false)}
      footer={null}
      width={700}
      destroyOnClose
    >
      <Alert
        message="Configure skill parameters"
        description={selectedSkill?.description}
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />
      
      <Form
        form={skillConfigForm}
        layout="vertical"
        onFinish={handleSaveSkillConfig}
      >
        <Collapse defaultActiveKey={Object.keys(selectedSkill?.config_schema || {}).map(f => 
          selectedSkill?.config_schema[f]?.group || 'general'
        ).filter((v, i, a) => a.indexOf(v) === i)}>
          {renderConfigFieldsGrouped()}
        </Collapse>

        <Divider />

        <Form.Item style={{ marginBottom: 0, marginTop: 16 }}>
          <Space>
            <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={savingSkillConfig}>
              Save Configuration
            </Button>
            <Button onClick={() => setConfigModalVisible(false)}>
              Cancel
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Modal>
  </>
  )
}

export default Settings
