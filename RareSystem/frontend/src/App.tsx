import { useState } from 'react'
import { Layout, Menu, Typography, Space, ConfigProvider, theme } from 'antd'
import {
  MedicineBoxOutlined,
  UploadOutlined,
  FileSearchOutlined,
  BarChartOutlined,
  SettingOutlined,
} from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import { UploadPage, AnalysisPage, BrowseCases } from '@/pages'
import { ErrorBoundary } from '@/components'
import Settings from '@/components/Settings'

const { Header, Content, Sider } = Layout
const { Title, Text } = Typography

type PageView = 'upload' | 'analysis' | 'browse' | 'settings'

interface SessionInfo {
  patientId: string
  vcfFileId: string
  hpoJobId?: string
}

function App() {
  const { t } = useTranslation()
  const [currentView, setCurrentView] = useState<PageView>('upload')
  const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null)
  const [siderCollapsed, setSiderCollapsed] = useState(false)

  const handleUploadComplete = (patientId: string, vcfFileId: string, hpoJobId?: string) => {
    setSessionInfo({ patientId, vcfFileId, hpoJobId })
    setCurrentView('analysis')
  }

  const handleBackToUpload = () => {
    setCurrentView('upload')
    setSessionInfo(null)
  }

  const menuItems = [
    {
      key: 'upload',
      icon: <UploadOutlined />,
      label: t('menu.newAnalysis'),
    },
    {
      key: 'browse',
      icon: <FileSearchOutlined />,
      label: t('menu.browseCases'),
    },
    {
      key: 'statistics',
      icon: <BarChartOutlined />,
      label: t('menu.statistics'),
      disabled: true,
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: t('menu.settings'),
    },
  ]

  const handleMenuClick = (key: string) => {
    if (key === 'upload') {
      handleBackToUpload()
    } else if (key === 'browse') {
      setCurrentView('browse')
    } else if (key === 'settings') {
      setCurrentView('settings')
    }
  }

  const handleOpenCase = (patientId: number, vcfFileId: number) => {
    setSessionInfo({ patientId: String(patientId), vcfFileId: String(vcfFileId) })
    setCurrentView('analysis')
  }

  const handleDeleteCase = (patientId: number) => {
    if (sessionInfo && String(patientId) === sessionInfo.patientId) {
      setSessionInfo(null)
      setCurrentView('browse')
    }
  }

  const handleError = (error: Error, errorInfo: React.ErrorInfo) => {
    console.error('Application error:', error, errorInfo)
  }

  return (
    <ConfigProvider
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 6,
        },
      }}
    >
      <ErrorBoundary onError={handleError}>
        <Layout style={{ minHeight: '100vh' }}>
        <Sider
          collapsible
          collapsed={siderCollapsed}
          onCollapse={setSiderCollapsed}
          style={{
            background: '#001529',
          }}
        >
          <div
            style={{
              height: 64,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            }}
          >
            <MedicineBoxOutlined
              style={{
                fontSize: siderCollapsed ? 24 : 32,
                color: '#1890ff',
                transition: 'all 0.2s',
              }}
            />
            {!siderCollapsed && (
              <Title
                level={4}
                style={{
                  color: 'white',
                  margin: '0 0 0 12px',
                  whiteSpace: 'nowrap',
                  fontSize: 14,
                }}
              >
                {t('app.brand')}
              </Title>
            )}
          </div>
          <Menu
            theme="dark"
            mode="inline"
            defaultSelectedKeys={['upload']}
            selectedKeys={[currentView]}
            items={menuItems}
            onClick={({ key }) => handleMenuClick(key)}
          />
        </Sider>

        <Layout>
          <Header
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              background: 'white',
              padding: '0 24px',
              borderBottom: '1px solid #f0f0f0',
              height: 64,
            }}
          >
            <Space>
              <Title level={4} style={{ margin: 0 }}>
                {t('app.title')}
              </Title>
            </Space>
            <Space>
              <Text type="secondary">{t('app.subtitle')}</Text>
            </Space>
          </Header>

          <Content style={{ background: '#f5f5f5', padding: currentView === 'settings' || currentView === 'browse' ? '24px' : 0 }}>
            {currentView === 'upload' && (
              <UploadPage onUploadComplete={handleUploadComplete} />
            )}

            {currentView === 'browse' && (
              <BrowseCases 
                onOpenCase={handleOpenCase}
                activePatientId={sessionInfo?.patientId ? Number(sessionInfo.patientId) : null}
                onDeleteCase={handleDeleteCase}
              />
            )}

            {currentView === 'analysis' && sessionInfo && (
              <AnalysisPage
                patientId={sessionInfo.patientId}
                vcfFileId={sessionInfo.vcfFileId}
                hpoJobId={sessionInfo.hpoJobId}
                onBack={handleBackToUpload}
              />
            )}

            {currentView === 'settings' && (
              <Settings />
            )}
          </Content>
        </Layout>
      </Layout>
      </ErrorBoundary>
    </ConfigProvider>
  )
}

export default App
