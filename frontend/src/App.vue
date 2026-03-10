<template>
  <div id="app">
    <div class="app-layout">
      <!-- Left Sidebar -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <div class="logo">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"/>
              <path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
            </svg>
            <span>Videlo</span>
          </div>
        </div>
        
        <nav class="nav-menu">
          <div class="nav-section">
            <span class="nav-section-title">Generate</span>
            <button 
              :class="['nav-item', { active: currentView === 'text2img' }]"
              @click="currentView = 'text2img'"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <path d="M21 15l-5-5L5 21"/>
              </svg>
              <span>Text to Image</span>
            </button>
            <button 
              :class="['nav-item', { active: currentView === 'txt2video' }]"
              @click="currentView = 'txt2video'"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="4" width="20" height="16" rx="2"/>
                <path d="M10 9l5 3-5 3V9z"/>
              </svg>
              <span>Text to Video</span>
            </button>
            <button 
              :class="['nav-item', { active: currentView === 'img2video' }]"
              @click="currentView = 'img2video'"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <path d="M21 15l-5-5L5 21"/>
                <path d="M17 11l4 4-4 4"/>
              </svg>
              <span>Image to Video</span>
            </button>
          </div>
          
          <div class="nav-section">
            <span class="nav-section-title">Library</span>
            <button 
              :class="['nav-item', { active: currentView === 'gallery' }]"
              @click="currentView = 'gallery'"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="7" height="7" rx="1"/>
                <rect x="14" y="3" width="7" height="7" rx="1"/>
                <rect x="3" y="14" width="7" height="7" rx="1"/>
                <rect x="14" y="14" width="7" height="7" rx="1"/>
              </svg>
              <span>Gallery</span>
            </button>
          </div>
        </nav>
        
        <div class="sidebar-footer">
          <div class="api-balance">
            <span class="balance-label">Credits</span>
            <span class="balance-value">{{ balance !== null ? '$' + balance.toFixed(2) : '--' }}</span>
          </div>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="main-content">
        <!-- Top Header -->
        <header class="top-header">
          <div class="breadcrumbs">
            <span class="breadcrumb-item">Home</span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
            <span class="breadcrumb-item active">{{ currentViewTitle }}</span>
          </div>
          <div class="header-actions">
            <button class="icon-btn" title="Settings">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/>
              </svg>
            </button>
          </div>
        </header>

        <!-- Page Content -->
        <div class="page-content">
          <Home 
            ref="home"
            :current-view="currentView"
            :generation-options="generationOptions"
            @update-options="updateOptions"
          />
        </div>
      </main>

      <!-- Right Settings Panel -->
      <aside class="settings-panel">
        <div class="settings-tabs">
          <button 
            :class="['tab', { active: settingsTab === 'form' }]"
            @click="settingsTab = 'form'"
          >Form</button>
          <button 
            :class="['tab', { active: settingsTab === 'json' }]"
            @click="settingsTab = 'json'"
          >JSON</button>
        </div>

        <div v-if="settingsTab === 'form'" class="settings-form">
          <!-- Model Selection -->
          <div class="setting-group">
            <label>Model</label>
            <select v-model="generationOptions.model" class="setting-select">
              <optgroup v-if="currentView === 'text2img'" label="Image Models">
                <option value="ZImageTurbo_INT8">ZImage Turbo</option>
                <option value="Flux1schnell">Flux 1 Schnell</option>
                <option value="Flux_2_Klein_4B_BF16">Flux 2 Klein</option>
              </optgroup>
              <optgroup v-else label="Video Models">
                <option value="Ltx2_19B_Dist_FP8">LTX-2 19B</option>
                <option value="Ltxv_13B_0_9_8_Distilled_FP8">LTX-Video 13B</option>
                <option value="Wan2_1_14B_T2V_BF16">Wan 2.1 T2V</option>
                <option value="HunyuanVideo_BF16">Hunyuan Video</option>
              </optgroup>
            </select>
          </div>

          <!-- Dimensions -->
          <div class="setting-group">
            <label>Dimensions</label>
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
              <label>Steps</label>
              <span class="setting-value">{{ generationOptions.steps }}</span>
            </div>
            <input 
              type="range" 
              v-model.number="generationOptions.steps"
              :min="currentView === 'text2img' ? 1 : 10"
              :max="currentView === 'text2img' ? 30 : 50"
              class="setting-slider"
            >
            <div class="slider-labels">
              <span>Fast</span>
              <span>Quality</span>
            </div>
          </div>

          <!-- Guidance -->
          <div class="setting-group">
            <div class="setting-header">
              <label>Guidance Scale</label>
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
            <label>Seed</label>
            <div class="seed-input-wrapper">
              <input 
                type="number" 
                v-model.number="generationOptions.seed"
                placeholder="Random"
                class="setting-input"
              >
              <button class="seed-random-btn" @click="generationOptions.seed = -1" title="Random seed">
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
          <template v-if="currentView !== 'text2img'">
            <div class="setting-divider"></div>
            
            <div class="setting-group">
              <label>Duration</label>
              <select v-model.number="generationOptions.frames" class="setting-select">
                <option :value="24">1 second</option>
                <option :value="48">2 seconds</option>
                <option :value="72">3 seconds</option>
                <option :value="96">4 seconds</option>
              </select>
            </div>

            <div class="setting-group">
              <label>FPS</label>
              <select v-model.number="generationOptions.fps" class="setting-select">
                <option :value="24">24 FPS</option>
                <option :value="30">30 FPS</option>
                <option :value="60">60 FPS</option>
              </select>
            </div>
          </template>
        </div>

        <!-- JSON Tab -->
        <div v-else class="settings-json">
          <pre>{{ JSON.stringify(generationOptions, null, 2) }}</pre>
        </div>
      </aside>
    </div>
  </div>
</template>

<script>
import Home from './views/Home.vue'
import api from './services/api.js'

export default {
  name: 'App',
  components: {
    Home
  },
  data() {
    return {
      currentView: 'text2img',
      settingsTab: 'form',
      balance: null,
      generationOptions: {
        model: 'ZImageTurbo_INT8',
        width: 1024,
        height: 768,
        steps: 8,
        guidance: 3.5,
        seed: -1,
        frames: 48,
        fps: 24
      }
    }
  },
  computed: {
    currentViewTitle() {
      const titles = {
        text2img: 'Text to Image',
        txt2video: 'Text to Video',
        img2video: 'Image to Video',
        gallery: 'Gallery'
      }
      return titles[this.currentView] || 'Generate'
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
    }
  },
  watch: {
    currentView(view) {
      // Update model based on view
      if (view === 'text2img') {
        this.generationOptions.model = 'ZImageTurbo_INT8'
      } else {
        this.generationOptions.model = 'Ltx2_19B_Dist_FP8'
      }
    }
  },
  mounted() {
    this.fetchBalance()
  },
  methods: {
    async fetchBalance() {
      try {
        const response = await api.getBalance()
        this.balance = response.balance
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
  min-height: 100vh;
}

/* App Layout */
.app-layout {
  display: flex;
  min-height: 100vh;
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
  background: var(--bg-base);
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
</style>