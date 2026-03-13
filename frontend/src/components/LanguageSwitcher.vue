<template>
  <div class="language-switcher">
    <button 
      v-for="lang in languages" 
      :key="lang.code"
      :class="['lang-btn', { active: currentLocale === lang.code }]"
      @click="switchLanguage(lang.code)"
    >
      {{ lang.label }}
    </button>
  </div>
</template>

<script>
import { useI18n } from 'vue-i18n'
import { setLocale } from '../i18n'

export default {
  name: 'LanguageSwitcher',
  setup() {
    const { locale } = useI18n()
    
    const languages = [
      { code: 'en', label: 'EN' },
      { code: 'zh', label: '中文' }
    ]
    
    const switchLanguage = (langCode) => {
      setLocale(langCode)
    }
    
    return {
      currentLocale: locale,
      languages,
      switchLanguage
    }
  }
}
</script>

<style scoped>
.language-switcher {
  display: flex;
  gap: 2px;
  padding: 2px;
  background: var(--bg-elevated);
  border-radius: 6px;
}

.lang-btn {
  padding: 4px 10px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.lang-btn:hover {
  color: var(--text-secondary);
}

.lang-btn.active {
  background: var(--accent-primary);
  color: #000;
}
</style>
