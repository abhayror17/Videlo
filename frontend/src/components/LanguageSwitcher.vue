<template>
  <div class="language-switcher" @click="toggleLanguage">
    <span :class="['lang-label', { active: currentLocale === 'en' }]">EN</span>
    <div class="switch-track">
      <div class="switch-thumb" :class="{ right: currentLocale === 'zh' }"></div>
    </div>
    <span :class="['lang-label', { active: currentLocale === 'zh' }]">中文</span>
  </div>
</template>

<script>
import { useI18n } from 'vue-i18n'
import { setLocale } from '../i18n'

export default {
  name: 'LanguageSwitcher',
  setup() {
    const { locale } = useI18n()
    
    const toggleLanguage = () => {
      const newLocale = locale.value === 'en' ? 'zh' : 'en'
      setLocale(newLocale)
    }
    
    return {
      currentLocale: locale,
      toggleLanguage
    }
  }
}
</script>

<style scoped>
.language-switcher {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  background: var(--bg-elevated);
  border-radius: 20px;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s ease;
}

.language-switcher:hover {
  background: var(--bg-input);
}

.lang-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  transition: color 0.2s ease;
}

.lang-label.active {
  color: var(--accent-primary);
}

.switch-track {
  width: 36px;
  height: 20px;
  background: var(--bg-input);
  border-radius: 10px;
  position: relative;
  transition: background 0.2s ease;
}

.switch-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 16px;
  height: 16px;
  background: var(--accent-primary);
  border-radius: 50%;
  transition: transform 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.switch-thumb.right {
  transform: translateX(16px);
}
</style>