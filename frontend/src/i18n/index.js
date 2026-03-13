import { createI18n } from 'vue-i18n'
import en from './locales/en.js'
import zh from './locales/zh.js'

// Get saved language from localStorage or use browser language
function getDefaultLocale() {
  const saved = localStorage.getItem('videlo_locale')
  if (saved && ['en', 'zh'].includes(saved)) {
    return saved
  }
  
  // Check browser language
  const browserLang = navigator.language.toLowerCase()
  if (browserLang.startsWith('zh')) {
    return 'zh'
  }
  
  return 'en'
}

const i18n = createI18n({
  legacy: false, // Use Composition API
  locale: getDefaultLocale(),
  fallbackLocale: 'en',
  messages: {
    en,
    zh
  }
})

export default i18n

// Helper to change locale and persist
export function setLocale(locale) {
  i18n.global.locale.value = locale
  localStorage.setItem('videlo_locale', locale)
  document.documentElement.lang = locale
}

// Helper to get current locale
export function getLocale() {
  return i18n.global.locale.value
}
