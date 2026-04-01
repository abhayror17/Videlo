<template>
  <div class="avatar-page">
    <!-- Header -->
    <header class="page-header">
      <div class="header-content">
        <h1>{{ $t('avatar.createTalkingAvatar') }}</h1>
        <p class="header-subtitle">{{ $t('avatar.subtitle') }}</p>
      </div>
      <button class="projects-toggle" @click="showProjects = !showProjects">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
        </svg>
        <span>{{ $t('avatar.myProjects') }}</span>
        <span class="project-count">{{ projects.length }}</span>
      </button>
    </header>

    <!-- Step Progress -->
    <div class="step-progress">
      <div class="progress-track">
        <div 
          class="progress-fill" 
          :style="{ width: progressWidth }"
        ></div>
      </div>
      <div class="step-indicators">
        <button 
          v-for="(step, index) in steps" 
          :key="step.id"
          class="step-indicator"
          :class="{ 
            active: currentStep === index,
            completed: isStepCompleted(index),
            clickable: canGoToStep(index)
          }"
          @click="goToStep(index)"
        >
          <span class="step-number">
            <svg v-if="isStepCompleted(index)" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <path d="M5 13l4 4L19 7"/>
            </svg>
            <span v-else>{{ index + 1 }}</span>
          </span>
          <span class="step-label">{{ step.label }}</span>
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Preview Area - Always Visible -->
      <div class="preview-area" :class="{ 'has-content': activeProject?.video_url || activeProject?.portrait_url }">
        <!-- Generating Overlay -->
        <div v-if="isGenerating" class="generating-overlay">
          <div class="generating-animation">
            <div class="pulse-ring"></div>
            <div class="pulse-ring delay-1"></div>
            <div class="pulse-ring delay-2"></div>
            <div class="generating-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z"/>
              </svg>
            </div>
          </div>
          <p class="generating-text">{{ statusMessage || $t('avatar.generating') }}</p>
          <p v-if="activeProject" class="generating-step">
            {{ currentGeneratingStep }}
          </p>
        </div>

        <!-- Video Result -->
        <video
          v-else-if="activeProject?.video_url"
          :src="activeProject.video_url"
          controls
          class="preview-media"
        ></video>

        <!-- Portrait Preview -->
        <img
          v-else-if="activeProject?.portrait_url"
          :src="activeProject.portrait_url"
          alt="Avatar portrait"
          class="preview-media"
        />

        <!-- Empty State -->
        <div v-else class="preview-empty">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
              <path d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"/>
            </svg>
          </div>
          <p class="empty-title">{{ $t('avatar.previewPlaceholder') }}</p>
          <p class="empty-hint">{{ $t('avatar.fillDetailsBelow') }}</p>
        </div>
      </div>

      <!-- Step Content -->
      <div class="step-content">
        <!-- Step 1: Portrait -->
        <div v-if="currentStep === 0" class="step-panel">
          <div class="step-header">
            <h2>{{ $t('avatar.stepPortrait') }}</h2>
            <StatusBadge v-if="activeProject" :status="activeProject.portrait_status" />
          </div>
          <div class="step-body">
            <div class="form-group">
              <label>{{ $t('avatar.portraitPrompt') }}</label>
              <textarea
                v-model="form.portraitPrompt"
                rows="4"
                :placeholder="$t('avatar.portraitPromptPlaceholder')"
              ></textarea>
            </div>
            <div class="form-tips">
              <p><strong>Tip:</strong> Describe facial features, hair style, clothing, and expression for best results.</p>
            </div>
          </div>
        </div>

        <!-- Step 2: Voice -->
        <div v-if="currentStep === 1" class="step-panel">
          <div class="step-header">
            <h2>{{ $t('avatar.stepVoice') }}</h2>
            <StatusBadge v-if="activeProject" :status="activeProject.audio_status" />
          </div>
          <div class="step-body">
            <div class="form-group">
              <label>{{ $t('avatar.speechText') }}</label>
              <textarea
                v-model="form.speechText"
                rows="4"
                :placeholder="$t('avatar.speechTextPlaceholder')"
              ></textarea>
            </div>
            
            <div class="form-group">
              <label>{{ $t('avatar.voice') }}</label>
              <div class="voice-grid">
                <button
                  v-for="voice in voiceOptions"
                  :key="voice.id"
                  class="voice-option"
                  :class="{ selected: form.voiceId === voice.id }"
                  @click="form.voiceId = voice.id"
                >
                  <span class="voice-avatar">{{ voice.avatar }}</span>
                  <span class="voice-name">{{ voice.name }}</span>
                  <span class="voice-accent">{{ voice.accent }}</span>
                </button>
              </div>
            </div>

            <div class="form-group">
              <label>{{ $t('avatar.speed') }}</label>
              <div class="speed-slider">
                <input
                  v-model.number="form.voiceSpeed"
                  type="range"
                  min="0.5"
                  max="2"
                  step="0.1"
                />
                <span class="speed-value">{{ form.voiceSpeed }}x</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 3: Animation -->
        <div v-if="currentStep === 2" class="step-panel">
          <div class="step-header">
            <h2>{{ $t('avatar.stepAnimation') }}</h2>
            <StatusBadge v-if="activeProject" :status="activeProject.video_status" />
          </div>
          <div class="step-body">
            <div class="form-group">
              <label>{{ $t('avatar.motionPrompt') }}</label>
              <div class="motion-presets">
                <button
                  v-for="preset in motionPresets"
                  :key="preset.id"
                  class="preset-chip"
                  :class="{ selected: form.motionPrompt === preset.prompt }"
                  @click="form.motionPrompt = preset.prompt"
                >
                  <span class="preset-emoji">{{ preset.emoji }}</span>
                  {{ preset.label }}
                </button>
              </div>
              <input
                v-model="form.motionPrompt"
                type="text"
                :placeholder="$t('avatar.motionPromptPlaceholder')"
              />
            </div>

            <!-- Duration & Quality Options -->
            <div class="options-row">
              <div class="form-group">
                <label>{{ $t('avatar.duration') }}</label>
                <div class="option-chips">
                  <button
                    v-for="dur in durationOptions"
                    :key="dur.value"
                    class="option-chip"
                    :class="{ selected: form.duration === dur.value }"
                    @click="form.duration = dur.value"
                  >
                    {{ dur.label }}
                  </button>
                </div>
              </div>

              <div class="form-group">
                <label>{{ $t('avatar.quality') }}</label>
                <div class="option-chips">
                  <button
                    v-for="q in qualityOptions"
                    :key="q.value"
                    class="option-chip"
                    :class="{ selected: form.quality === q.value }"
                    @click="form.quality = q.value"
                  >
                    {{ q.label }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="step-actions">
          <button
            v-if="currentStep > 0"
            class="btn-secondary"
            @click="prevStep"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M15 19l-7-7 7-7"/>
            </svg>
            {{ $t('common.back') }}
          </button>
          
          <button
            v-if="currentStep < 2"
            class="btn-primary"
            :disabled="!isCurrentStepValid"
            @click="nextStep"
          >
            {{ $t('common.next') }}
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 5l7 7-7 7"/>
            </svg>
          </button>

          <button
            v-if="currentStep === 2"
            class="btn-primary generate"
            :disabled="isGenerating || !isFormValid"
            @click="createAndGenerate"
          >
            <svg v-if="isGenerating" class="spinner" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-dasharray="31.4 31.4" transform="rotate(-90 12 12)"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z"/>
            </svg>
            {{ isGenerating ? $t('avatar.generating') : $t('avatar.generateAvatar') }}
          </button>
        </div>

        <!-- Download Section (when complete) -->
        <div v-if="activeProject?.video_status === 'completed' && activeProject?.video_url" class="download-section">
          <h3>{{ $t('avatar.readyToDownload') }}</h3>
          <div class="download-actions">
            <a :href="activeProject.video_url" target="_blank" rel="noopener" class="btn-download">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              {{ $t('avatar.downloadVideo') }}
            </a>
            <button class="btn-copy" @click="copyLink(activeProject.video_url)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
              </svg>
              {{ $t('avatar.copyLink') }}
            </button>
          </div>
        </div>
      </div>
    </main>

    <!-- Projects Drawer -->
    <Teleport to="body">
      <Transition name="drawer">
        <div v-if="showProjects" class="drawer-overlay" @click.self="showProjects = false">
          <div class="projects-drawer">
            <div class="drawer-header">
              <h2>{{ $t('avatar.myProjects') }}</h2>
              <button class="drawer-close" @click="showProjects = false">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
            <div class="drawer-body">
              <div v-if="loadingProjects" class="drawer-loading">
                <div class="spinner"></div>
              </div>
              <div v-else-if="!projects.length" class="drawer-empty">
                <p>{{ $t('avatar.noProjects') }}</p>
              </div>
              <div v-else class="projects-list">
                <div
                  v-for="project in projects"
                  :key="project.id"
                  class="project-card"
                  :class="{ active: project.id === activeProjectId }"
                  @click="selectProject(project.id)"
                >
                  <div class="project-preview">
                    <img v-if="project.video_url" :src="project.video_url" alt="" />
                    <img v-else-if="project.portrait_url" :src="project.portrait_url" alt="" />
                    <div v-else class="preview-placeholder">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"/>
                      </svg>
                    </div>
                    <StatusBadge :status="project.overall_status" class="project-status" />
                  </div>
                  <div class="project-info">
                    <span class="project-name">{{ project.name || $t('avatar.untitledProject') }}</span>
                    <span class="project-date">{{ formatDate(project.created_at) }}</span>
                  </div>
                  <div class="project-actions">
                    <button class="action-icon" @click.stop="startRename(project)" :title="$t('common.rename')">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                        <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                      </svg>
                    </button>
                    <button class="action-icon danger" @click.stop="confirmDelete(project)" :title="$t('common.delete')">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"/>
                        <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Rename Modal -->
    <Teleport to="body">
      <div v-if="showRenameModal" class="modal-overlay" @click.self="showRenameModal = false">
        <div class="modal-content">
          <h3>{{ $t('avatar.renameProject') }}</h3>
          <input
            v-model="renameValue"
            type="text"
            class="modal-input"
            :placeholder="$t('avatar.projectName')"
            @keyup.enter="saveRename"
            ref="renameInput"
          />
          <div class="modal-actions">
            <button class="btn-secondary" @click="showRenameModal = false">{{ $t('common.cancel') }}</button>
            <button class="btn-primary" @click="saveRename" :disabled="!renameValue.trim()">{{ $t('common.save') }}</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Delete Modal -->
    <Teleport to="body">
      <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
        <div class="modal-content delete">
          <div class="delete-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
          </div>
          <h3>{{ $t('avatar.deleteProject') }}</h3>
          <p>{{ $t('avatar.deleteConfirm', { name: projectToDelete?.name || $t('avatar.untitledProject') }) }}</p>
          <div class="modal-actions">
            <button class="btn-secondary" @click="showDeleteModal = false">{{ $t('common.cancel') }}</button>
            <button class="btn-danger" @click="deleteProject">{{ $t('common.delete') }}</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script>
import { useI18n } from 'vue-i18n'
import api from '../services/api.js'
import StatusBadge from '../components/StatusBadge.vue'

export default {
  name: 'AiAvatar',
  components: { StatusBadge },
  setup() {
    const { t } = useI18n()
    return { t }
  },
  data() {
    return {
      currentStep: 0,
      showProjects: false,
      form: {
        portraitPrompt: '',
        speechText: '',
        motionPrompt: '',
        voiceId: 'af_sky',
        voiceSpeed: 1.0,
        duration: '120',
        quality: '768'
      },
      steps: [
        { id: 'portrait', label: 'Portrait' },
        { id: 'voice', label: 'Voice' },
        { id: 'animate', label: 'Animate' }
      ],
      voiceOptions: [
        { id: 'af_sky', name: 'Sky', accent: 'Female, US', avatar: '👩' },
        { id: 'af_sarah', name: 'Sarah', accent: 'Female, US', avatar: '👩‍🦰' },
        { id: 'am_adam', name: 'Adam', accent: 'Male, US', avatar: '👨' },
        { id: 'am_michael', name: 'Michael', accent: 'Male, US', avatar: '👨‍🦱' },
        { id: 'bf_emma', name: 'Emma', accent: 'Female, UK', avatar: '👱‍♀️' },
        { id: 'bm_george', name: 'George', accent: 'Male, UK', avatar: '🧔' }
      ],
      motionPresets: [
        { id: 'natural', label: 'Natural', emoji: '😊', prompt: 'Natural head movement, occasional blinking, subtle expressions' },
        { id: 'talking', label: 'Talking', emoji: '🗣️', prompt: 'Active talking gestures, nodding, expressive mouth movements' },
        { id: 'professional', label: 'Professional', emoji: '💼', prompt: 'Steady gaze, minimal movement, confident posture' },
        { id: 'friendly', label: 'Friendly', emoji: '👋', prompt: 'Warm smile, welcoming gestures, approachable demeanor' },
        { id: 'energetic', label: 'Energetic', emoji: '⚡', prompt: 'Dynamic expressions, animated gestures, lively movement' },
        { id: 'calm', label: 'Calm', emoji: '🧘', prompt: 'Slow movements, peaceful expressions, relaxed posture' }
      ],
      durationOptions: [
        { value: '49', label: '~2 sec' },
        { value: '97', label: '~4 sec' },
        { value: '120', label: '~5 sec' },
        { value: '161', label: '~7 sec' },
        { value: '241', label: '~10 sec' }
      ],
      qualityOptions: [
        { value: '512', label: 'Standard' },
        { value: '768', label: 'HD' },
        { value: '1024', label: 'Full HD' }
      ],
      projects: [],
      activeProjectId: null,
      activeProject: null,
      loadingProjects: false,
      isGenerating: false,
      statusMessage: '',
      pollInterval: null,
      showRenameModal: false,
      renameValue: '',
      projectToRename: null,
      showDeleteModal: false,
      projectToDelete: null
    }
  },
  computed: {
    progressWidth() {
      // Progress advances as user moves through steps
      // On step 0: 0%, On step 1: 33%, On step 2: 66%, After generate: 100%
      if (this.activeProject?.video_status === 'completed') {
        return '100%'
      }
      return `${(this.currentStep / this.steps.length) * 100}%`
    },
    isCurrentStepValid() {
      if (this.currentStep === 0) return this.form.portraitPrompt.trim().length >= 5
      if (this.currentStep === 1) return this.form.speechText.trim().length >= 3
      return true
    },
    isFormValid() {
      return this.form.portraitPrompt.trim().length >= 5 &&
             this.form.speechText.trim().length >= 3
    },
    currentGeneratingStep() {
      if (!this.activeProject) return ''
      if (this.activeProject.portrait_status === 'processing') return this.t('avatar.generatingPortrait')
      if (this.activeProject.audio_status === 'processing') return this.t('avatar.generatingVoice')
      if (this.activeProject.video_status === 'processing') return this.t('avatar.generatingVideo')
      return ''
    }
  },
  mounted() {
    this.loadProjects()
  },
  beforeUnmount() {
    this.stopPolling()
  },
  methods: {
    isStepCompleted(index) {
      if (!this.activeProject) return false
      if (index === 0) return this.activeProject.portrait_status === 'completed'
      if (index === 1) return this.activeProject.audio_status === 'completed'
      if (index === 2) return this.activeProject.video_status === 'completed'
      return false
    },
    canGoToStep(index) {
      if (!this.activeProject) return index === 0
      return true
    },
    goToStep(index) {
      if (this.canGoToStep(index)) {
        this.currentStep = index
      }
    },
    nextStep() {
      if (this.currentStep < this.steps.length - 1) {
        this.currentStep++
      }
    },
    prevStep() {
      if (this.currentStep > 0) {
        this.currentStep--
      }
    },
    formatDate(date) {
      if (!date) return ''
      return new Date(date).toLocaleDateString()
    },
    
    async loadProjects() {
      this.loadingProjects = true
      try {
        const response = await api.getAiAvatars(1, 20)
        this.projects = response.items || []
      } catch (error) {
        console.error('Failed to load projects:', error)
      } finally {
        this.loadingProjects = false
      }
    },

    async selectProject(projectId) {
      this.activeProjectId = projectId
      await this.loadProjectDetail(projectId)
      this.showProjects = false
    },

    async loadProjectDetail(projectId = this.activeProjectId) {
      if (!projectId) return
      try {
        this.activeProject = await api.getAiAvatarStatus(projectId)
        this.form.portraitPrompt = this.activeProject.portrait_prompt || ''
        this.form.speechText = this.activeProject.speech_text || ''
        this.form.motionPrompt = this.activeProject.motion_prompt || ''
        this.form.voiceId = this.activeProject.voice_id || 'af_sky'
        this.form.voiceSpeed = this.activeProject.voice_speed || 1.0
        
        if (this.activeProject.overall_status === 'processing') {
          this.isGenerating = true
          this.startPolling()
        } else {
          this.isGenerating = false
          this.stopPolling()
        }
      } catch (error) {
        console.error('Failed to load project:', error)
      }
    },

    startPolling() {
      this.stopPolling()
      // Increased from 5s to 15s to reduce API requests
      this.pollInterval = setInterval(async () => {
        if (this.activeProjectId) {
          await this.loadProjectDetail()
        }
      }, 15000)
    },

    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
        this.pollInterval = null
      }
    },

    async createAndGenerate() {
      if (!this.isFormValid) return

      this.isGenerating = true
      this.statusMessage = this.t('avatar.creatingProject')
      this.stopPolling()

      try {
        const project = await api.createAiAvatar({
          name: this.form.portraitPrompt.slice(0, 30),
          portraitPrompt: this.form.portraitPrompt,
          speechText: this.form.speechText,
          motionPrompt: this.form.motionPrompt,
          voiceId: this.form.voiceId,
          voiceSpeed: this.form.voiceSpeed,
          animationFrames: parseInt(this.form.duration),
          portraitWidth: parseInt(this.form.quality),
          portraitHeight: parseInt(this.form.quality)
        })

        this.activeProjectId = project.id
        this.statusMessage = this.t('avatar.startingPipeline')

        await api.generateAiAvatar(project.id, 'all')
        
        await this.loadProjects()
        await this.loadProjectDetail(project.id)
        
        this.startPolling()
      } catch (error) {
        console.error('Failed to create avatar:', error)
        this.statusMessage = error?.response?.data?.detail || error?.message || this.t('avatar.failedToCreate')
        this.isGenerating = false
      }
    },

    async copyLink(url) {
      try {
        await navigator.clipboard.writeText(url)
        this.statusMessage = this.t('avatar.linkCopied')
        setTimeout(() => { this.statusMessage = '' }, 2000)
      } catch (error) {
        console.error('Failed to copy:', error)
      }
    },

    startRename(project) {
      this.projectToRename = project
      this.renameValue = project.name || ''
      this.showRenameModal = true
      this.$nextTick(() => this.$refs.renameInput?.focus())
    },

    async saveRename() {
      if (!this.renameValue.trim() || !this.projectToRename) return
      
      try {
        await api.updateAiAvatar(this.projectToRename.id, { name: this.renameValue.trim() })
        
        const idx = this.projects.findIndex(p => p.id === this.projectToRename.id)
        if (idx !== -1) {
          this.projects[idx].name = this.renameValue.trim()
        }
        if (this.activeProjectId === this.projectToRename.id && this.activeProject) {
          this.activeProject.name = this.renameValue.trim()
        }
        
        this.showRenameModal = false
      } catch (error) {
        console.error('Failed to rename:', error)
      }
    },

    confirmDelete(project) {
      this.projectToDelete = project
      this.showDeleteModal = true
    },

    async deleteProject() {
      if (!this.projectToDelete) return
      
      try {
        await api.deleteAiAvatar(this.projectToDelete.id)
        this.projects = this.projects.filter(p => p.id !== this.projectToDelete.id)
        
        if (this.activeProjectId === this.projectToDelete.id) {
          this.activeProjectId = null
          this.activeProject = null
          this.stopPolling()
        }
        
        this.showDeleteModal = false
        this.projectToDelete = null
      } catch (error) {
        console.error('Failed to delete:', error)
      }
    }
  }
}
</script>

<style scoped>
.avatar-page {
  min-height: 100%;
  padding: 24px;
  padding-top: max(24px, env(safe-area-inset-top));
  padding-bottom: max(24px, env(safe-area-inset-bottom));
  padding-left: max(24px, env(safe-area-inset-left));
  padding-right: max(24px, env(safe-area-inset-right));
  max-width: 900px;
  margin: 0 auto;
}

/* Header */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 32px;
}

.header-content h1 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 8px;
}

.header-subtitle {
  color: var(--text-secondary);
  margin: 0;
}

.projects-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.15s;
}

.projects-toggle:hover {
  background: var(--bg-elevated);
  border-color: var(--accent-primary);
}

.projects-toggle svg {
  width: 18px;
  height: 18px;
}

.project-count {
  background: var(--accent-primary);
  color: #000;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
}

/* Step Progress */
.step-progress {
  margin-bottom: 40px;
}

.progress-track {
  height: 4px;
  background: var(--bg-elevated);
  border-radius: 2px;
  margin-bottom: 16px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
  transition: width 0.3s ease;
}

.step-indicators {
  display: flex;
  justify-content: space-between;
}

.step-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  cursor: default;
  padding: 0;
}

.step-indicator.clickable {
  cursor: pointer;
}

.step-number {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--bg-elevated);
  color: var(--text-muted);
  font-weight: 600;
  transition: all 0.2s;
}

.step-indicator.active .step-number {
  background: var(--accent-primary);
  color: #000;
  box-shadow: 0 0 20px rgba(245, 158, 11, 0.4);
}

.step-indicator.completed .step-number {
  background: var(--accent-secondary);
  color: #000;
}

.step-number svg {
  width: 18px;
  height: 18px;
}

.step-label {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.step-indicator.active .step-label,
.step-indicator.completed .step-label {
  color: var(--text-primary);
}

/* Main Content */
.main-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* Preview Area */
.preview-area {
  position: relative;
  aspect-ratio: 16/9;
  border-radius: 20px;
  background: var(--bg-panel);
  border: 2px dashed var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.preview-area.has-content {
  border: none;
  background: #000;
}

.preview-media {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.preview-empty {
  text-align: center;
  color: var(--text-muted);
  padding: 40px 20px;
}

.empty-icon {
  margin-bottom: 16px;
}

.empty-icon svg {
  width: 64px;
  height: 64px;
  opacity: 0.5;
}

.empty-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px;
}

.empty-hint {
  margin: 0;
  font-size: 0.875rem;
}

/* Generating Overlay */
.generating-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(8px);
  padding: 20px;
}

.generating-animation {
  position: relative;
  width: 100px;
  height: 100px;
  margin-bottom: 24px;
}

.pulse-ring {
  position: absolute;
  inset: 0;
  border: 2px solid var(--accent-primary);
  border-radius: 50%;
  animation: pulse 2s ease-out infinite;
}

.pulse-ring.delay-1 { animation-delay: 0.5s; }
.pulse-ring.delay-2 { animation-delay: 1s; }

@keyframes pulse {
  0% { transform: scale(0.5); opacity: 1; }
  100% { transform: scale(1.5); opacity: 0; }
}

.generating-icon {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.generating-icon svg {
  width: 40px;
  height: 40px;
  color: var(--accent-primary);
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.generating-text {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 8px;
  text-align: center;
}

.generating-step {
  color: var(--text-secondary);
  margin: 0;
  text-align: center;
  font-size: 0.875rem;
}

/* Step Content */
.step-content {
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 32px;
}

.step-panel {
  margin-bottom: 32px;
}

.step-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.step-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.step-body {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Form Elements */
.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.form-group textarea,
.form-group input[type="text"] {
  width: 100%;
  padding: 14px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  color: var(--text-primary);
  font: inherit;
  font-size: 1rem;
  resize: vertical;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-group textarea:focus,
.form-group input[type="text"]:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.15);
}

.form-tips {
  padding: 12px 16px;
  background: rgba(245, 158, 11, 0.1);
  border-radius: 10px;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.form-tips p {
  margin: 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* Voice Grid */
.voice-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.voice-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 12px;
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.voice-option:hover {
  border-color: var(--accent-primary);
  background: rgba(245, 158, 11, 0.05);
}

.voice-option.selected {
  border-color: var(--accent-primary);
  background: rgba(245, 158, 11, 0.1);
}

.voice-avatar {
  font-size: 2rem;
  margin-bottom: 8px;
}

.voice-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.875rem;
}

.voice-accent {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Speed Slider */
.speed-slider {
  display: flex;
  align-items: center;
  gap: 16px;
}

.speed-slider input[type="range"] {
  flex: 1;
  height: 6px;
  background: var(--bg-elevated);
  border-radius: 3px;
  appearance: none;
}

.speed-slider input[type="range"]::-webkit-slider-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
  background: var(--accent-primary);
  border-radius: 50%;
  cursor: pointer;
}

.speed-value {
  min-width: 50px;
  text-align: center;
  font-weight: 600;
  color: var(--text-primary);
}

/* Motion Presets */
.motion-presets {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 12px;
}

.preset-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  color: var(--text-primary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-chip:hover {
  border-color: var(--accent-primary);
}

.preset-chip.selected {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #000;
}

.preset-emoji {
  font-size: 1rem;
}

/* Options Row */
.options-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 20px;
}

.option-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.option-chip {
  padding: 8px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.option-chip:hover {
  border-color: var(--accent-primary);
}

.option-chip.selected {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #000;
}

/* Action Buttons */
.step-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary,
.btn-download,
.btn-copy,
.btn-danger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-primary,
.btn-download {
  background: var(--accent-primary);
  border: none;
  color: #000;
}

.btn-primary:hover,
.btn-download:hover {
  background: #fbbf24;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.btn-secondary:hover {
  background: var(--bg-elevated);
  border-color: var(--accent-primary);
}

.btn-danger {
  background: #ef4444;
  border: none;
  color: #fff;
}

.btn-danger:hover {
  background: #dc2626;
}

.btn-copy {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  text-decoration: none;
}

.btn-copy:hover {
  background: var(--bg-elevated);
}

.btn-primary svg,
.btn-secondary svg,
.btn-download svg,
.btn-copy svg,
.btn-danger svg {
  width: 18px;
  height: 18px;
}

.spinner {
  width: 18px;
  height: 18px;
  animation: spin 1s linear infinite;
}

/* Download Section */
.download-section {
  margin-top: 32px;
  padding-top: 32px;
  border-top: 1px solid var(--border-color);
  text-align: center;
}

.download-section h3 {
  margin: 0 0 20px;
  font-size: 1.25rem;
}

.download-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

/* Projects Drawer */
.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
}

.projects-drawer {
  width: 400px;
  max-width: 100%;
  background: var(--bg-secondary);
  border-left: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  animation: slide-in 0.3s ease;
  padding-bottom: env(safe-area-inset-bottom);
}

@keyframes slide-in {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.drawer-header h2 {
  margin: 0;
  font-size: 1.25rem;
}

.drawer-close {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
}

.drawer-close svg {
  width: 18px;
  height: 18px;
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.drawer-loading,
.drawer-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: var(--text-muted);
}

.projects-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.project-card {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.project-card:hover {
  border-color: var(--accent-primary);
}

.project-card.active {
  border-color: var(--accent-primary);
  background: rgba(245, 158, 11, 0.05);
}

.project-preview {
  position: relative;
  width: 80px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background: var(--bg-elevated);
}

.project-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.preview-placeholder svg {
  width: 24px;
  height: 24px;
}

.project-status {
  position: absolute;
  bottom: 4px;
  right: 4px;
  transform: scale(0.8);
}

.project-info {
  flex: 1;
  min-width: 0;
}

.project-name {
  display: block;
  font-weight: 600;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.project-date {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.project-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.action-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.15s;
}

.action-icon:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.action-icon.danger:hover {
  color: #ef4444;
}

.action-icon svg {
  width: 16px;
  height: 16px;
}

/* Modals */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  width: 400px;
  max-width: 90vw;
}

.modal-content.delete {
  text-align: center;
}

.delete-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  color: #f59e0b;
}

.delete-icon svg {
  width: 100%;
  height: 100%;
}

.modal-content h3 {
  margin: 0 0 16px;
  font-size: 1.25rem;
}

.modal-content p {
  margin: 0 0 24px;
  color: var(--text-secondary);
}

.modal-input {
  width: 100%;
  padding: 12px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font: inherit;
  margin-bottom: 20px;
}

.modal-input:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* Drawer Transition */
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.3s ease;
}

.drawer-enter-active .projects-drawer,
.drawer-leave-active .projects-drawer {
  transition: transform 0.3s ease;
}

.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}

.drawer-enter-from .projects-drawer,
.drawer-leave-to .projects-drawer {
  transform: translateX(100%);
}

/* Responsive */
@media (max-width: 768px) {
  .avatar-page {
    padding: 12px;
  }

  .page-header {
    flex-direction: row;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
  }

  .header-content h1 {
    font-size: 1.25rem;
    margin-bottom: 4px;
  }

  .header-subtitle {
    display: none;
  }

  .projects-toggle {
    padding: 8px 12px;
    font-size: 0.8125rem;
  }

  .projects-toggle span:not(.project-count) {
    display: none;
  }

  .step-progress {
    margin-bottom: 20px;
  }

  .step-indicators {
    gap: 0;
  }

  .step-indicator {
    flex: 1;
  }

  .step-number {
    width: 32px;
    height: 32px;
    font-size: 0.875rem;
  }

  .step-number svg {
    width: 16px;
    height: 16px;
  }

  .step-label {
    display: none;
  }

  .main-content {
    gap: 16px;
  }

  .preview-area {
    aspect-ratio: 1;
    border-radius: 16px;
  }

  .generating-icon svg {
    width: 32px;
    height: 32px;
  }

  .generating-text {
    font-size: 1rem;
  }

  .generating-animation {
    width: 80px;
    height: 80px;
    margin-bottom: 16px;
  }

  .step-content {
    padding: 20px 16px;
    border-radius: 16px;
  }

  .step-header {
    margin-bottom: 16px;
  }

  .step-header h2 {
    font-size: 1.125rem;
  }

  .step-body {
    gap: 16px;
  }

  .form-group textarea,
  .form-group input[type="text"] {
    padding: 12px;
    font-size: 0.9375rem;
  }

  .form-tips {
    display: none;
  }

  .voice-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }

  .voice-option {
    padding: 12px 8px;
  }

  .voice-avatar {
    font-size: 1.5rem;
  }

  .voice-name {
    font-size: 0.8125rem;
  }

  .voice-accent {
    font-size: 0.6875rem;
  }

  .motion-presets {
    gap: 6px;
  }

  .preset-chip {
    padding: 6px 10px;
    font-size: 0.75rem;
  }

  .preset-emoji {
    font-size: 0.875rem;
  }

  .step-actions {
    flex-direction: column;
    gap: 10px;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
    justify-content: center;
    padding: 14px 20px;
  }

  .btn-primary.generate {
    order: -1;
  }

  .download-section {
    margin-top: 20px;
    padding-top: 20px;
  }

  .download-section h3 {
    font-size: 1rem;
    margin-bottom: 16px;
  }

  .download-actions {
    flex-direction: column;
    gap: 10px;
  }

  .btn-download,
  .btn-copy {
    width: 100%;
    justify-content: center;
  }

  .projects-drawer {
    width: 100%;
    max-width: 100%;
  }

  .project-card {
    padding: 10px;
  }

  .project-preview {
    width: 60px;
    height: 45px;
  }

  .project-name {
    font-size: 0.875rem;
  }

  .modal-content {
    width: 95vw;
    padding: 20px 16px;
    margin: 16px;
  }

  .modal-actions {
    flex-direction: column;
    gap: 10px;
  }

  .modal-actions .btn-primary,
  .modal-actions .btn-secondary,
  .modal-actions .btn-danger {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .avatar-page {
    padding: 8px;
  }

  .header-content h1 {
    font-size: 1.125rem;
  }

  .projects-toggle {
    padding: 8px;
  }

  .project-count {
    padding: 2px 6px;
    font-size: 0.6875rem;
  }

  .preview-area {
    aspect-ratio: 1;
    border-radius: 12px;
  }

  .preview-empty {
    padding: 20px;
  }

  .empty-icon svg {
    width: 48px;
    height: 48px;
  }

  .empty-title {
    font-size: 0.9375rem;
  }

  .empty-hint {
    font-size: 0.8125rem;
  }

  .step-content {
    padding: 16px 12px;
    border-radius: 12px;
  }

  .step-panel {
    margin-bottom: 20px;
  }

  .voice-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 6px;
  }

  .voice-option {
    padding: 10px 6px;
  }

  .voice-avatar {
    font-size: 1.25rem;
    margin-bottom: 4px;
  }

  .voice-name {
    font-size: 0.75rem;
  }

  .voice-accent {
    display: none;
  }

  .options-row {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .option-chips {
    gap: 6px;
  }

  .option-chip {
    padding: 6px 12px;
    font-size: 0.75rem;
  }

  .speed-slider {
    gap: 12px;
  }

  .speed-value {
    font-size: 0.875rem;
  }

  .drawer-header {
    padding: 16px;
  }

  .drawer-body {
    padding: 12px;
  }

  .project-card {
    padding: 8px;
    gap: 8px;
  }

  .project-preview {
    width: 50px;
    height: 38px;
  }

  .project-actions {
    flex-direction: row;
    gap: 4px;
  }

  .action-icon {
    width: 28px;
    height: 28px;
  }

  .action-icon svg {
    width: 14px;
    height: 14px;
  }
}
</style>