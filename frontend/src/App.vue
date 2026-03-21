<template>
  <div id="app">
    <div class="app-layout">
      <!-- Left Sidebar -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <router-link to="/" class="logo">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"/>
              <path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
            </svg>
            <span>Videlo</span>
          </router-link>
        </div>
        
        <nav class="nav-menu">
          <div class="nav-section">
            <span class="nav-section-title">{{ $t('nav.generate') }}</span>
            <router-link to="/text2img" class="nav-item" active-class="active">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <path d="M21 15l-5-5L5 21"/>
              </svg>
              <span>{{ $t('nav.text2img') }}</span>
            </router-link>
            <router-link to="/imgedit" class="nav-item" active-class="active">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
              <span>{{ $t('nav.imgedit') }}</span>
            </router-link>
            <router-link to="/txt2video" class="nav-item" active-class="active">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="4" width="20" height="16" rx="2"/>
                <path d="M10 9l5 3-5 3V9z"/>
              </svg>
              <span>{{ $t('nav.txt2video') }}</span>
            </router-link>
            <router-link to="/img2video" class="nav-item" active-class="active">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <path d="M21 15l-5-5L5 21"/>
                <path d="M17 11l4 4-4 4"/>
              </svg>
              <span>{{ $t('nav.img2video') }}</span>
            </router-link>
            <router-link to="/ads" class="nav-item" active-class="active">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="4" width="20" height="16" rx="2"/>
                <path d="M10 9l5 3-5 3V9z"/>
                <circle cx="17" cy="7" r="2"/>
                <path d="M17 7l2-2"/>
              </svg>
              <span>{{ $t('nav.ads') }}</span>
            </router-link>
            <router-link to="/ads-img-gen" class="nav-item" active-class="active">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <path d="M21 15l-5-5L5 21"/>
                <path d="M12 2v4m0 12v4"/>
              </svg>
              <span>{{ $t('nav.adsImgGen') }}</span>
            </router-link>
          </div>
          
          <div class="nav-section">
            <span class="nav-section-title">{{ $t('nav.library') }}</span>
            <router-link to="/gallery" class="nav-item" active-class="active">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="7" height="7" rx="1"/>
                <rect x="14" y="3" width="7" height="7" rx="1"/>
                <rect x="3" y="14" width="7" height="7" rx="1"/>
                <rect x="14" y="14" width="7" height="7" rx="1"/>
              </svg>
              <span>{{ $t('nav.gallery') }}</span>
            </router-link>
            <router-link to="/prompts" class="nav-item" active-class="active">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14.5 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V7.5L14.5 2z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <line x1="10" y1="9" x2="8" y2="9"/>
              </svg>
              <span>{{ $t('nav.prompts') }}</span>
            </router-link>
            <router-link to="/workflow" class="nav-item" active-class="active">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="7" height="7"/>
                <rect x="14" y="3" width="7" height="7"/>
                <rect x="3" y="14" width="7" height="7"/>
                <path d="M14 17h3v3"/>
                <path d="M17 17l-4 4"/>
                <path d="M21 17v3a1 1 0 01-1 1h-3"/>
              </svg>
              <span>{{ $t('nav.workflow') }}</span>
            </router-link>
          </div>
        </nav>
        
        <div class="sidebar-footer">
          <div class="api-balance">
            <span class="balance-label">{{ $t('nav.credits') }}</span>
            <span class="balance-value">{{ balance !== null ? '$' + balance.toFixed(2) : '--' }}</span>
          </div>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="main-content">
        <!-- Top Header -->
        <header class="top-header">
          <div class="breadcrumbs">
            <span class="breadcrumb-item">{{ $t('header.home') }}</span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
            <span class="breadcrumb-item active">{{ currentRouteTitle }}</span>
          </div>
          <div class="header-actions">
            <LanguageSwitcher />
            <button class="icon-btn settings-icon-btn" :title="$t('header.settings')" @click="showSettingsModal = true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/>
              </svg>
              <span v-if="hasCustomApiKey" class="settings-badge">✓</span>
            </button>
          </div>
        </header>

        <!-- Page Content -->
        <div class="page-content" :class="{ 'workflow-page': $route.name === 'workflow' }">
          <router-view 
            ref="pageComponent"
            :current-view="currentMode"
            :generation-options="generationOptions"
            @update-options="updateOptions"
          />
        </div>
      </main>

      <!-- Right Settings Panel -->
      <aside v-if="showSettingsPanel" class="settings-panel">
        <div class="settings-tabs">
          <button 
            :class="['tab', { active: settingsTab === 'form' }]"
            @click="settingsTab = 'form'"
          >{{ $t('settings.form') }}</button>
          <button 
            :class="['tab', { active: settingsTab === 'json' }]"
            @click="settingsTab = 'json'"
          >{{ $t('settings.json') }}</button>
        </div>

        <div v-if="settingsTab === 'form'" class="settings-form">
          <!-- Model Selection -->
          <div class="setting-group">
            <label>{{ $t('settings.model') }}</label>
            <select v-model="generationOptions.model" class="setting-select">
              <optgroup v-if="currentMode === 'text2img'" :label="$t('settings.imageModels')">
                <option value="Flux_2_Klein_4B_BF16">Flux 2 Klein</option>
                <option value="ZImageTurbo_INT8">ZImage Turbo</option>
              </optgroup>
              <optgroup v-else-if="currentMode === 'imgedit'" :label="$t('settings.imageEditModels')">
                <option value="QwenImageEdit_Plus_NF4">Qwen Image Edit</option>
                <option value="Flux_2_Klein_4B_BF16">Flux 2 Klein</option>
              </optgroup>
              <optgroup v-else :label="$t('settings.videoModels')">
                <option value="Ltx2_3_22B_Dist_INT8">LTX-2.3 22B (Recommended)</option>
                <option value="Ltx2_19B_Dist_FP8">LTX-2 19B</option>
                <option value="Ltxv_13B_0_9_8_Distilled_FP8">LTX-Video 13B</option>
                <option value="Wan2_1_14B_T2V_BF16">Wan 2.1 T2V</option>
                <option value="HunyuanVideo_BF16">Hunyuan Video</option>
              </optgroup>
            </select>
          </div>

          <!-- Dimensions (hide for imgedit) -->
          <div v-if="currentMode !== 'imgedit'" class="setting-group">
            <label>{{ $t('settings.dimensions') }}</label>
            <div class="dimension-inputs">
              <div class="dim-input">
                <input 
                  type="number" 
                  v-model.number="generationOptions.width"
                  min="256"
                  max="2048"
                  step="64"
                >
                <span>W</span>
              </div>
              <div class="dim-input">
                <input 
                  type="number" 
                  v-model.number="generationOptions.height"
                  min="256"
                  max="2048"
                  step="64"
                >
                <span>H</span>
              </div>
            </div>
            <div class="aspect-presets">
              <button 
                v-for="preset in aspectPresets" 
                :key="preset.label"
                :class="['preset-btn', { active: activeAspectPreset === preset.label }]"
                @click="setAspectPreset(preset)"
              >{{ preset.label }}</button>
            </div>
          </div>

          <!-- Steps -->
          <div class="setting-group">
            <div class="setting-header">
              <label>{{ $t('settings.steps') }}</label>
              <span class="setting-value">{{ generationOptions.steps }}</span>
            </div>
            <input 
              v-if="generationOptions.model !== 'Flux_2_Klein_4B_BF16'"
              type="range" 
              v-model.number="generationOptions.steps"
              :min="currentMode === 'text2img' ? 1 : 10"
              :max="currentMode === 'text2img' ? 30 : 50"
              class="setting-slider"
            >
            <div v-else class="steps-fixed">
              <span class="fixed-label">{{ $t('settings.fixedAtFlux') }}</span>
            </div>
            <div class="slider-labels" v-if="generationOptions.model !== 'Flux_2_Klein_4B_BF16'">
              <span>{{ $t('settings.fast') }}</span>
              <span>{{ $t('settings.quality') }}</span>
            </div>
          </div>

          <!-- Guidance -->
          <div class="setting-group">
            <div class="setting-header">
              <label>{{ $t('settings.guidanceScale') }}</label>
              <span class="setting-value">{{ generationOptions.guidance }}</span>
            </div>
            <input 
              type="range" 
              v-model.number="generationOptions.guidance"
              min="1"
              max="10"
              step="0.5"
              class="setting-slider"
            >
          </div>

          <!-- Seed -->
          <div class="setting-group">
            <label>{{ $t('settings.seed') }}</label>
            <div class="seed-input-wrapper">
              <input 
                type="number" 
                v-model.number="generationOptions.seed"
                :placeholder="$t('settings.random')"
                class="setting-input"
              >
              <button class="seed-random-btn" @click="generationOptions.seed = -1" :title="$t('settings.random')">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="2" y="2" width="8" height="8" rx="1"/>
                  <rect x="14" y="2" width="8" height="8" rx="1"/>
                  <rect x="2" y="14" width="8" height="8" rx="1"/>
                  <rect x="14" y="14" width="8" height="8" rx="1"/>
                  <circle cx="5" cy="5" r="1" fill="currentColor"/>
                  <circle cx="19" cy="5" r="1" fill="currentColor"/>
                  <circle cx="5" cy="19" r="1" fill="currentColor"/>
                  <circle cx="17" cy="17" r="1" fill="currentColor"/>
                  <circle cx="19" cy="19" r="1" fill="currentColor"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Video Options -->
          <template v-if="currentMode === 'txt2video' || currentMode === 'img2video'">
            <div class="setting-divider"></div>
            
            <div class="setting-group">
              <label>{{ $t('settings.duration') }}</label>
              <select v-model.number="generationOptions.frames" class="setting-select">
                <option :value="49">~2 {{ $t('settings.seconds') }}</option>
                <option :value="120">~5 {{ $t('settings.seconds') }}</option>
                <option :value="241">~10 {{ $t('settings.seconds') }}</option>
              </select>
            </div>

            <div class="setting-group">
              <label>{{ $t('settings.fps') }}</label>
              <select v-model.number="generationOptions.fps" class="setting-select">
                <option :value="24">24 FPS</option>
              </select>
            </div>
          </template>
          
          <!-- Credit Estimate -->
          <div class="setting-divider"></div>
          <div class="credit-estimate">
            <div class="credit-row">
              <span class="credit-label">
                <svg class="credit-icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.31-8.86c-1.77-.45-2.34-.94-2.34-1.67 0-.84.79-1.43 2.1-1.43 1.38 0 1.9.66 1.94 1.64h1.71c-.05-1.34-.87-2.57-2.49-2.97V5H10.9v1.69c-1.51.32-2.72 1.3-2.72 2.81 0 1.79 1.49 2.69 3.66 3.21 1.95.46 2.34 1.15 2.34 1.87 0 .53-.39 1.39-2.1 1.39-1.6 0-2.23-.72-2.32-1.64H8.04c.1 1.7 1.36 2.66 2.86 2.97V19h2.34v-1.67c1.52-.29 2.72-1.16 2.73-2.77-.01-2.2-1.9-2.96-3.66-3.42z"/>
                </svg>
                {{ $t('credits.estimated') }}
              </span>
              <span class="credit-value">{{ estimatedCredits }} {{ $t('credits.credits') }}</span>
            </div>
            <p class="credit-hint" v-if="currentMode === 'txt2video' || currentMode === 'img2video'">
              {{ $t('credits.videoHint') }}
            </p>
          </div>
        </div>

        <!-- JSON Tab -->
        <div v-else class="settings-json">
          <pre>{{ JSON.stringify(generationOptions, null, 2) }}</pre>
        </div>
      </aside>
    </div>

    <!-- BYOK Settings Modal -->
    <Teleport to="body">
      <div v-if="showSettingsModal" class="modal-backdrop" @click.self="showSettingsModal = false">
        <div class="byok-modal">
          <button class="modal-close-btn" @click="showSettingsModal = false">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
          
          <h3>{{ $t('header.settings') }}</h3>
          
          <div class="byok-section">
            <div class="byok-header">
              <span class="byok-badge">BYOK</span>
              <span class="byok-label">{{ $t('settings.bringYourOwnKey') }}</span>
            </div>
            <p class="byok-desc">
              {{ $t('settings.byokDesc') }}
              <a href="https://deapi.ai" target="_blank" rel="noopener">deapi.ai</a>
            </p>
            
            <div class="api-key-input">
              <input 
                :type="showApiKey ? 'text' : 'password'"
                v-model="customApiKey"
                :placeholder="$t('settings.enterApiKey')"
              />
              <button class="toggle-visibility" @click="showApiKey = !showApiKey">
                <svg v-if="showApiKey" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </button>
            </div>
            
            <div v-if="hasCustomApiKey" class="key-status active">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              <span>{{ $t('settings.customKeyActive') }}</span>
            </div>
          </div>
          
          <div class="modal-actions">
            <button class="modal-btn secondary" @click="clearApiKey" :disabled="!hasCustomApiKey">
              {{ $t('settings.clearKey') }}
            </button>
            <button class="modal-btn primary" @click="saveApiKey" :disabled="!customApiKey.trim()">
              {{ $t('settings.saveKey') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script>
import { useI18n } from 'vue-i18n'
import api from './services/api.js'
import LanguageSwitcher from './components/LanguageSwitcher.vue'

export default {
  name: 'App',
  components: {
    LanguageSwitcher
  },
  setup() {
    const { t } = useI18n()
    return { t }
  },
  data() {
    return {
      settingsTab: 'form',
      balance: null,
      showSettingsModal: false,
      customApiKey: '',
      showApiKey: false,
      generationOptions: {
        model: 'Flux_2_Klein_4B_BF16',
        width: 1024,
        height: 576,
        steps: 4,
        guidance: 3.5,
        seed: -1,
        frames: 49,
        fps: 24
      }
    }
  },
  computed: {
    currentMode() {
      return this.$route.meta.mode || this.$route.name
    },
    currentRouteTitle() {
      const titleKey = this.$route.meta.title
      return titleKey ? this.t(titleKey) : this.t('nav.generate')
    },
    showSettingsPanel() {
      // Hide settings for ads (uses internal pipeline), gallery, prompts, workflow, img-gen, and ads-img-gen
      return !['ads', 'gallery', 'prompts', 'workflow', 'img-gen', 'ads-img-gen'].includes(this.$route.name)
    },
    hasCustomApiKey() {
      return !!localStorage.getItem('deapi_key')
    },
    aspectPresets() {
      return [
        { label: '1:1', width: 1024, height: 1024 },
        { label: '16:9', width: 1024, height: 576 },
        { label: '9:16', width: 576, height: 1024 },
        { label: '4:3', width: 1024, height: 768 }
      ]
    },
    activeAspectPreset() {
      const w = this.generationOptions.width
      const h = this.generationOptions.height
      const preset = this.aspectPresets.find(p => p.width === w && p.height === h)
      return preset?.label || null
    },
    estimatedCredits() {
      // Credit pricing tables
      const txt2imgCredits = {
        'Flux1schnell': { 512: 4, 768: 5, 1024: 8, 1536: 12, 2048: 18 },
        'Flux_2_Klein_4B_BF16': { 512: 5, 768: 8, 1024: 10, 1536: 15 },
        'ZImageTurbo_INT8': { 512: 8, 768: 12, 1024: 20, 1536: 30, 2048: 45 }
      }
      const videoCredits = {
        'Ltx2_3_22B_Dist_INT8': { '512x512x49': 8, '768x768x120': 20, '1024x1024x120': 30, '768x768x241': 35, '1024x1024x241': 50 },
        'Ltx2_19B_Dist_FP8': { '512x512x49': 12, '768x768x120': 80, '1024x1024x120': 120, '768x768x241': 140 },
        'Ltxv_13B_0_9_8_Distilled_FP8': { '512x512x30': 5, '512x512x60': 8, '512x512x120': 12, '768x768x120': 20 }
      }
      const img2imgCredits = {
        'QwenImageEdit_Plus_NF4': { 512: 40, 768: 70, 1024: 100 },
        'Flux_2_Klein_4B_BF16': { 768: 12, 1024: 16, 1536: 25 }
      }
      
      const model = this.generationOptions.model
      const width = this.generationOptions.width
      const height = this.generationOptions.height
      const maxDim = Math.max(width, height)
      
      if (this.currentMode === 'txt2video' || this.currentMode === 'img2video') {
        const frames = this.generationOptions.frames || 49
        const pricing = videoCredits[model] || videoCredits['Ltx2_3_22B_Dist_INT8']
        
        // Find best match
        let bestMatch = 20
        for (const [key, credits] of Object.entries(pricing)) {
          const [w, h, f] = key.split('x').map(Number)
          if (width <= w && height <= h && frames <= f) {
            if (credits < bestMatch) bestMatch = credits
          }
        }
        return bestMatch
      } else if (this.currentMode === 'imgedit') {
        const pricing = img2imgCredits[model] || img2imgCredits['QwenImageEdit_Plus_NF4']
        for (const [dim, credits] of Object.entries(pricing)) {
          if (maxDim <= parseInt(dim)) return credits
        }
        return 100
      } else {
        // text2img
        const pricing = txt2imgCredits[model] || txt2imgCredits['Flux_2_Klein_4B_BF16']
        for (const [dim, credits] of Object.entries(pricing)) {
          if (maxDim <= parseInt(dim)) return credits
        }
        return 15
      }
    }
  },
  watch: {
    currentMode(mode) {
      // Update model based on mode
      if (mode === 'text2img') {
        this.generationOptions.model = 'Flux_2_Klein_4B_BF16'
      } else if (mode === 'txt2video' || mode === 'img2video') {
        this.generationOptions.model = 'Ltx2_3_22B_Dist_INT8'
      } else if (mode === 'imgedit') {
        this.generationOptions.model = 'QwenImageEdit_Plus_NF4'
      }
    },
    'generationOptions.model'(model) {
      // Flux 2 requires exactly 4 steps
      if (model === 'Flux_2_Klein_4B_BF16') {
        this.generationOptions.steps = 4
      }
    }
  },
  mounted() {
    this.loadCachedBalance()
    this.loadSavedApiKey()
  },
  methods: {
    loadCachedBalance() {
      // Use cached balance if available and less than 5 minutes old
      const cached = localStorage.getItem('videlo_balance')
      if (cached) {
        try {
          const { balance, timestamp } = JSON.parse(cached)
          const age = Date.now() - timestamp
          if (age < 5 * 60 * 1000) { // 5 minutes
            this.balance = balance
            return
          }
        } catch (e) {}
      }
      this.fetchBalance()
    },
    async fetchBalance() {
      try {
        const response = await api.getBalance()
        this.balance = response.balance
        // Cache for 5 minutes
        localStorage.setItem('videlo_balance', JSON.stringify({
          balance: response.balance,
          timestamp: Date.now()
        }))
      } catch (error) {
        console.error('Failed to fetch balance:', error)
      }
    },
    setAspectPreset(preset) {
      this.generationOptions.width = preset.width
      this.generationOptions.height = preset.height
    },
    updateOptions(options) {
      this.generationOptions = { ...this.generationOptions, ...options }
    },
    loadSavedApiKey() {
      const savedKey = localStorage.getItem('deapi_key')
      if (savedKey) {
        this.customApiKey = savedKey
      }
    },
    saveApiKey() {
      if (this.customApiKey.trim()) {
        localStorage.setItem('deapi_key', this.customApiKey.trim())
        this.showSettingsModal = false
      }
    },
    clearApiKey() {
      localStorage.removeItem('deapi_key')
      this.customApiKey = ''
    }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --bg-base: #0F0F0F;
  --bg-panel: #1A1A1A;
  --bg-elevated: #242424;
  --bg-input: #1F1F1F;
  --accent-primary: #F59E0B;
  --accent-primary-hover: #FBBF24;
  --accent-secondary: #2DD4BF;
  --text-primary: #EDEDED;
  --text-secondary: #A3A3A3;
  --text-muted: #737373;
  --border-color: #262626;
  --border-hover: #404040;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg-base);
  min-height: 100vh;
  color: var(--text-primary);
  overflow-x: hidden;
}

#app {
  height: 100vh;
  overflow: hidden;
}

/* App Layout */
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* Left Sidebar */
.sidebar {
  width: 240px;
  background: var(--bg-panel);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid var(--border-color);
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  text-decoration: none;
}

.logo svg {
  width: 28px;
  height: 28px;
  color: var(--accent-primary);
}

.nav-menu {
  flex: 1;
  padding: 16px 8px;
  overflow-y: auto;
}

.nav-section {
  margin-bottom: 24px;
}

.nav-section-title {
  display: block;
  padding: 8px 12px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 10px 12px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
  text-decoration: none;
}

.nav-item svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.nav-item:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border-color);
}

.api-balance {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: var(--bg-elevated);
  border-radius: 8px;
}

.balance-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.balance-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--accent-primary);
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

/* Top Header */
.top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border-color);
}

.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
}

.breadcrumb-item {
  color: var(--text-muted);
}

.breadcrumb-item.active {
  color: var(--text-primary);
}

.breadcrumbs svg {
  width: 14px;
  height: 14px;
  color: var(--text-muted);
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.icon-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.icon-btn:hover {
  background: var(--bg-elevated);
  border-color: var(--border-hover);
  color: var(--text-primary);
}

.icon-btn svg {
  width: 18px;
  height: 18px;
}

/* Page Content */
.page-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  overflow-x: hidden;
  background: var(--bg-base);
  min-height: 0;
}

/* Workflow page gets zero padding so canvas fills full area */
.page-content.workflow-page {
  padding: 0;
  overflow: hidden;
}

/* Right Settings Panel */
.settings-panel {
  width: 280px;
  background: var(--bg-panel);
  border-left: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.settings-tabs {
  display: flex;
  padding: 4px;
  margin: 12px;
  background: var(--bg-elevated);
  border-radius: 8px;
}

.tab {
  flex: 1;
  padding: 8px 16px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tab:hover {
  color: var(--text-secondary);
}

.tab.active {
  background: var(--bg-panel);
  color: var(--text-primary);
}

.settings-form {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.setting-group {
  margin-bottom: 20px;
}

.setting-group label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.setting-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.setting-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--accent-primary);
}

.setting-select {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 0.875rem;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23A3A3A3' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  padding-right: 36px;
}

.setting-select:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.setting-input {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 0.875rem;
}

.setting-input:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.setting-input::placeholder {
  color: var(--text-muted);
}

/* Dimension Inputs */
.dimension-inputs {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}

.dim-input {
  flex: 1;
  position: relative;
}

.dim-input input {
  width: 100%;
  padding: 10px 12px;
  padding-right: 32px;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 0.875rem;
}

.dim-input input:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.dim-input span {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.7rem;
  color: var(--text-muted);
  font-weight: 600;
}

.aspect-presets {
  display: flex;
  gap: 6px;
}

.preset-btn {
  flex: 1;
  padding: 6px 8px;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-muted);
  font-size: 0.7rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.preset-btn:hover {
  border-color: var(--border-hover);
  color: var(--text-secondary);
}

.preset-btn.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #000;
}

/* Slider */
.setting-slider {
  width: 100%;
  height: 4px;
  background: var(--bg-elevated);
  border-radius: 2px;
  appearance: none;
  cursor: pointer;
}

.setting-slider::-webkit-slider-thumb {
  appearance: none;
  width: 16px;
  height: 16px;
  background: var(--accent-primary);
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 0 8px rgba(245, 158, 11, 0.4);
}

.setting-slider::-webkit-slider-thumb:hover {
  transform: scale(1.1);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 6px;
  font-size: 0.65rem;
  color: var(--text-muted);
}

.steps-fixed {
  padding: 8px 0;
}

.fixed-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-style: italic;
}

/* Seed Input */
.seed-input-wrapper {
  display: flex;
  gap: 8px;
}

.seed-input-wrapper input {
  flex: 1;
}

.seed-random-btn {
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--accent-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.seed-random-btn:hover {
  background: var(--bg-elevated);
  border-color: var(--accent-secondary);
}

.seed-random-btn svg {
  width: 16px;
  height: 16px;
}

.setting-divider {
  height: 1px;
  background: var(--border-color);
  margin: 20px 0;
}

/* Credit Estimate */
.credit-estimate {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(34, 197, 94, 0.05));
  border: 1px solid rgba(34, 197, 94, 0.2);
  border-radius: 10px;
  padding: 14px;
}

.credit-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.credit-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.credit-icon {
  width: 18px;
  height: 18px;
  color: #22C55E;
}

.credit-value {
  font-size: 1rem;
  font-weight: 700;
  color: #22C55E;
}

.credit-hint {
  margin: 10px 0 0;
  font-size: 0.7rem;
  color: var(--text-muted);
  line-height: 1.4;
}

/* JSON Tab */
.settings-json {
  flex: 1;
  padding: 16px;
  overflow: auto;
}

.settings-json pre {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.7rem;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-all;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--border-hover);
}

/* Responsive */
@media (max-width: 1200px) {
  .settings-panel {
    width: 260px;
  }
}

@media (max-width: 900px) {
  .sidebar {
    width: 60px;
  }
  
  .sidebar-header .logo span,
  .nav-section-title,
  .nav-item span,
  .sidebar-footer {
    display: none;
  }
  
  .nav-item {
    justify-content: center;
    padding: 12px;
  }
  
  .settings-panel {
    display: none;
  }
}

/* Settings Icon Button with Badge */
.settings-icon-btn {
  position: relative;
}

.settings-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 14px;
  height: 14px;
  background: #22C55E;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  color: white;
  font-weight: bold;
}

/* BYOK Modal Styles */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.byok-modal {
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  max-width: 420px;
  width: 90%;
  position: relative;
}

.modal-close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.modal-close-btn:hover {
  background: var(--bg-input);
  color: var(--text-primary);
}

.modal-close-btn svg {
  width: 16px;
  height: 16px;
}

.byok-modal h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.byok-section {
  margin-bottom: 20px;
}

.byok-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.byok-badge {
  background: linear-gradient(135deg, #F59E0B, #D97706);
  color: #000;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.byok-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

.byok-desc {
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 16px;
}

.byok-desc a {
  color: var(--accent-primary);
  text-decoration: none;
}

.byok-desc a:hover {
  text-decoration: underline;
}

.api-key-input {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.api-key-input input {
  flex: 1;
  padding: 12px 14px;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.875rem;
  font-family: monospace;
}

.api-key-input input:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.api-key-input input::placeholder {
  color: var(--text-muted);
  font-family: inherit;
}

.toggle-visibility {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.toggle-visibility:hover {
  background: var(--bg-input);
  color: var(--text-primary);
}

.toggle-visibility svg {
  width: 18px;
  height: 18px;
}

.key-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.2);
  border-radius: 8px;
  font-size: 0.8rem;
}

.key-status.active {
  color: #22C55E;
}

.key-status svg {
  width: 16px;
  height: 16px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.modal-btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.modal-btn.secondary {
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.modal-btn.secondary:hover:not(:disabled) {
  background: var(--bg-input);
  color: var(--text-primary);
}

.modal-btn.primary {
  background: var(--accent-primary);
  border: none;
  color: #000;
}

.modal-btn.primary:hover:not(:disabled) {
  background: var(--accent-primary-hover);
}

.modal-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>