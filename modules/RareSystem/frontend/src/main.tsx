import { createRoot } from 'react-dom/client'
import { ConfigProvider } from 'antd'
import enUS from 'antd/locale/en_US'
import zhCN from 'antd/locale/zh_CN'
import App from './App.tsx'
import './i18n' // Initialize i18n
import i18n from './i18n'

// Get Ant Design locale based on current language
const getAntdLocale = () => {
  const lng = i18n.language
  if (lng.startsWith('zh')) return zhCN
  return enUS
}

createRoot(document.getElementById('root')!).render(
  <ConfigProvider locale={getAntdLocale()}>
    <App />
  </ConfigProvider>,
)
