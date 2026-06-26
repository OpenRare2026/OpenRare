import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

import en from './locales/en.json'
import zh from './locales/zh.json'

const resources = {
  en: { translation: en },
  zh: { translation: zh },
}

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: false,
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: ['navigator', 'htmlTag', 'localStorage', 'cookie'],
      caches: ['localStorage', 'cookie'],
    },
  })

export default i18n

export function getCurrentLanguage(): 'en' | 'zh' {
  const lng = i18n.language
  if (lng.startsWith('zh')) return 'zh'
  return 'en'
}
