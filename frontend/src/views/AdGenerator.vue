<template>
  <div class="ad-generator">
    <div class="generation-view">
      <!-- Preview Area -->
      <div class="preview-area">
        <!-- No campaign: empty state -->
        <div v-if="!campaign" class="preview-placeholder">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="2" y="4" width="20" height="16" rx="2"/>
            <path d="M10 9l5 3-5 3V9z"/>
            <circle cx="17" cy="7" r="2"/>
            <path d="M17 7l2-2"/>
          </svg>
          <p>{{ $t('ads.yourAdCampaignWillAppear') }}</p>
        </div>

        <!-- Campaign in progress -->
        <div v-else class="pipeline-preview">
          <!-- Phase Progress -->
          <div class="phase-progress">
            <div 
              v-for="phase in phases" 
              :key="phase.id"
              class="phase-step"
              :class="getPhaseClass(phase.id)"
              @click="canNavigateToPhase(phase.id) && redoFromPhase(phase.id)"
            >
              <div class="phase-icon">
                <svg v-if="campaign.current_phase > phase.id || (campaign.current_phase === phase.id && campaign.phase_status === 'completed')" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <span v-else>{{ phase.id }}</span>
              </div>
              <span class="phase-label">{{ $t(phase.labelKey) }}</span>
              <button 
                v-if="canNavigateToPhase(phase.id) && campaign.current_phase !== phase.id" 
                class="phase-redo-btn"
                @click.stop="redoFromPhase(phase.id)"
                :title="'Redo from Phase ' + phase.id"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 4v6h6"/>
                  <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Phase Content -->
          <div class="phase-content-area">
            <!-- Phase 1: Clarification Questions -->
            <div v-if="campaign.current_phase === 1 && questions.length > 0" class="phase-content questions">
              <h3>{{ $t('ads.helpUsUnderstand') }}</h3>
              <div class="questions-list">
                <div v-for="(q, idx) in questions" :key="q.id" class="question-item">
                  <label>{{ q.question }}</label>
                  <input 
                    v-if="q.type === 'text'" 
                    v-model="answers[q.id]" 
                    type="text" 
                    class="answer-input"
                    :placeholder="$t('ads.typeAnswer')"
                  />
                  <select v-else-if="q.type === 'select'" v-model="answers[q.id]" class="answer-select">
                    <option value="">{{ $t('ads.selectOption') }}</option>
                    <option v-for="opt in q.options" :key="opt" :value="opt">{{ opt }}</option>
                  </select>
                </div>
              </div>
              <button @click="submitAnswers" class="submit-answers-btn" :disabled="!hasAllAnswers">
                {{ $t('ads.continue') }}
              </button>
            </div>

            <!-- Processing State -->
            <div v-else-if="campaign.phase_status === 'processing'" class="phase-content processing">
              <div class="spinner-large"></div>
              <p>{{ getProcessingMessage() }}</p>
            </div>

            <!-- Phase 3: Ad Strategy -->
            <div v-else-if="campaign.current_phase === 3 && campaign.ad_angles?.length" class="phase-content strategy">
              <h3>{{ $t('ads.adStrategy') }}</h3>
              <div class="angles-grid">
                <div v-for="angle in campaign.ad_angles" :key="angle.id" class="angle-card">
                  <div class="angle-header">
                    <span class="angle-id">#{{ angle.id }}</span>
                    <span class="angle-hook">{{ angle.hook_idea }}</span>
                  </div>
                  <p class="angle-emotion">{{ angle.emotional_trigger }}</p>
                  <p class="angle-why">{{ angle.why_convert }}</p>
                </div>
              </div>
              <button @click="generateScripts" class="action-btn">
                {{ $t('ads.generateScripts') }}
              </button>
            </div>

            <!-- Phase 4+: Generated Content -->
            <div v-else-if="campaign.current_phase >= 4 || (campaign.scripts_status === 'completed' && scripts.length > 0)" class="phase-content generated">
              <!-- Scripts -->
              <div v-if="scripts.length > 0" class="scripts-section">
                <h3>{{ $t('ads.generatedScripts') }}</h3>
                <div class="scripts-tabs">
                  <button 
                    v-for="script in scripts" 
                    :key="script.id"
                    :class="['script-tab', { active: selectedScriptId === script.id }]"
                    @click="selectedScriptId = script.id"
                  >
                    Script {{ script.id }}
                  </button>
                </div>
                <div v-if="selectedScript" class="script-content">
                  <div class="script-hook">
                    <label>{{ $t('ads.hook') }}</label>
                    <p>"{{ selectedScript.hook }}"</p>
                  </div>
                  <div class="script-scenes">
                    <div v-for="scene in selectedScript.scenes" :key="scene.scene" class="scene-item">
                      <span class="scene-num">{{ $t('ads.scene') }} {{ scene.scene }}</span>
                      <p class="scene-dialogue">{{ scene.dialogue }}</p>
                      <p class="scene-visual">{{ scene.visual }}</p>
                      <span class="scene-duration">{{ scene.duration }}</span>
                    </div>
                  </div>
                  <div class="script-cta">
                    <label>{{ $t('ads.cta') }}</label>
                    <p>"{{ selectedScript.cta }}"</p>
                  </div>
                </div>
              </div>

              <!-- Avatars -->
              <div v-if="avatars.length > 0" class="avatars-section">
                <h3>{{ $t('ads.generatedAvatars') }}</h3>
                <div class="avatars-grid">
                  <div v-for="avatar in avatars" :key="avatar.id" class="avatar-card">
                    <div class="avatar-name">{{ avatar.name }}</div>
                    <div class="avatar-details">
                      <span>{{ avatar.age }}y, {{ avatar.gender }}</span>
                      <span>{{ avatar.region }}</span>
                    </div>
                    <p class="avatar-appearance">{{ avatar.appearance }}</p>
                    <p class="avatar-vibe">{{ avatar.personality_vibe }}</p>
                  </div>
                </div>
              </div>

              <!-- Continue Button -->
              <button v-if="campaign.current_phase < 9" @click="continueGeneration" class="action-btn">
                {{ getNextPhaseButton() }}
              </button>

              <!-- Completed -->
              <div v-if="campaign.overall_status === 'completed'" class="completed-section">
                <div class="completed-header">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                    <polyline points="22 4 12 14.01 9 11.01"/>
                  </svg>
                  <h3>{{ $t('ads.campaignComplete') }}</h3>
                </div>
                <button @click="resetCampaign" class="new-campaign-btn">
                  {{ $t('ads.newCampaign') }}
                </button>
              </div>
            </div>

            <!-- Error State -->
            <div v-else-if="campaign.error_message" class="phase-content error">
              <div class="error-message">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <span>{{ campaign.error_message }}</span>
              </div>
              <button @click="resetCampaign" class="action-btn">{{ $t('ads.tryAgain') }}</button>
            </div>
          </div>

          <!-- Debug Logs Panel -->
          <div v-if="showDebugLogs && campaign" class="debug-panel">
            <div class="debug-header">
              <h4>Debug Logs</h4>
              <button @click="loadDebugLogs" class="debug-refresh-btn" title="Refresh logs">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 4v6h6"/>
                  <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
                </svg>
              </button>
            </div>
            <div class="debug-logs">
              <div v-if="debugLogs.length === 0" class="debug-empty">No logs yet</div>
              <div v-for="(log, idx) in debugLogs" :key="idx" class="debug-log-item" :class="log.status">
                <span class="log-time">{{ formatLogTime(log.timestamp) }}</span>
                <span class="log-phase">{{ log.phase }}</span>
                <span class="log-status">{{ log.status }}</span>
                <span class="log-data">{{ log.data?.error || log.data?.elapsed_ms + 'ms' || '' }}</span>
              </div>
            </div>
          </div>

          <!-- Debug Toggle Button -->
          <button v-if="campaign" @click="showDebugLogs = !showDebugLogs" class="debug-toggle-btn" :class="{ active: showDebugLogs }">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/>
              <path d="M12 18a6 6 0 1 0 0-12 6 6 0 0 0 0 12z"/>
              <circle cx="12" cy="12" r="2"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Prompt Area -->
      <div v-if="!campaign" class="prompt-area">
        <div class="prompt-wrapper">
          <textarea
            v-model="userPrompt"
            :placeholder="promptPlaceholder"
            rows="3"
            class="prompt-input"
            @keydown.ctrl.enter="startCampaign"
          ></textarea>
          <div class="prompt-footer">
            <div class="prompt-actions">
              <input
                v-model="brandName"
                type="text"
                :placeholder="$t('ads.brandName')"
                class="brand-input"
              />
            </div>
            <div class="generate-btn-wrapper">
              <button
                @click="campaign ? resetCampaign() : startCampaign()"
                :disabled="!userPrompt.trim() && !campaign"
                class="generate-btn"
              >
                <span v-if="creating" class="btn-content">
                  <span class="spinner"></span>
                  <span>{{ $t('ads.starting') }}</span>
                </span>
                <span v-else-if="campaign" class="btn-content">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="19" y1="12" x2="5" y2="12"/>
                    <polyline points="12 19 5 12 12 5"/>
                  </svg>
                  <span>{{ $t('ads.newCampaign') }}</span>
                </span>
                <span v-else class="btn-content">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                  </svg>
                  <span>{{ $t('ads.generateAd') }}</span>
                </span>
              </button>
              <div class="credit-badge" v-if="!campaign">
                <svg class="credit-icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.31-8.86c-1.77-.45-2.34-.94-2.34-1.67 0-.84.79-1.43 2.1-1.43 1.38 0 1.9.66 1.94 1.64h1.71c-.05-1.34-.87-2.57-2.49-2.97V5H10.9v1.69c-1.51.32-2.72 1.3-2.72 2.81 0 1.79 1.49 2.69 3.66 3.21 1.95.46 2.34 1.15 2.34 1.87 0 .53-.39 1.39-2.1 1.39-1.6 0-2.23-.72-2.32-1.64H8.04c.1 1.7 1.36 2.66 2.86 2.97V19h2.34v-1.67c1.52-.29 2.72-1.16 2.73-2.77-.01-2.2-1.9-2.96-3.66-3.42z"/>
                </svg>
                <span>{{ adCredits }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Campaigns -->
      <div v-if="previousCampaigns.length > 0 && !campaign" class="recent-section">
        <h3>{{ $t('ads.previousCampaigns') }}</h3>
        <div class="recent-grid">
          <div
            v-for="camp in previousCampaigns.slice(0, 4)"
            :key="camp.id"
            class="recent-card"
            @click="loadCampaign(camp.id)"
          >
            <div class="card-status" :class="camp.overall_status"></div>
            <div class="card-placeholder">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="2" y="4" width="20" height="16" rx="2"/>
                <path d="M10 9l5 3-5 3V9z"/>
              </svg>
            </div>
            <div class="card-info">
              <span class="card-brand">{{ camp.brand_name || $t('ads.noBrand') }}</span>
              <span class="card-prompt">{{ camp.user_prompt?.substring(0, 40) }}...</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useI18n } from 'vue-i18n'
import api from '../services/api.js'

export default {
  name: 'AdGenerator',
  props: {
    generationOptions: {
      type: Object,
      default: () => ({})
    }
  },
  setup() {
    const { t } = useI18n()
    return { t }
  },
  data() {
    return {
      userPrompt: '',
      brandName: '',
      brandDescription: '',
      creating: false,
      campaign: null,
      pollingInterval: null,
      previousCampaigns: [],
      questions: [],
      answers: {},
      scripts: [],
      avatars: [],
      selectedScriptId: 1,
      showDebugLogs: false,
      debugLogs: [],
      redoingPhase: null,
      phases: [
        { id: 1, labelKey: 'ads.phaseAsk' },
        { id: 2, labelKey: 'ads.phaseContext' },
        { id: 3, labelKey: 'ads.phaseStrategy' },
        { id: 4, labelKey: 'ads.phaseScripts' },
        { id: 5, labelKey: 'ads.phaseAvatars' },
        { id: 6, labelKey: 'ads.phaseStoryboard' },
        { id: 7, labelKey: 'ads.phaseImages' },
        { id: 8, labelKey: 'ads.phaseVideos' },
        { id: 9, labelKey: 'ads.phaseComplete' }
      ]
    }
  },
  computed: {
    promptPlaceholder() {
      return this.t('ads.describeAdConcept')
    },
    adCredits() {
      return 30
    },
    hasAllAnswers() {
      if (this.questions.length === 0) return false
      return this.questions.every(q => this.answers[q.id]?.trim())
    },
    selectedScript() {
      return this.scripts.find(s => s.id === this.selectedScriptId) || this.scripts[0]
    }
  },
  mounted() {
    this.loadPreviousCampaigns()
  },
  beforeUnmount() {
    this.stopPolling()
  },
  methods: {
    async loadPreviousCampaigns() {
      try {
        const response = await api.getAdCampaigns(1, 6)
        this.previousCampaigns = response.items || []
      } catch (error) {
        console.error('Failed to load campaigns:', error)
      }
    },

    async startCampaign() {
      if (!this.userPrompt.trim() || this.creating) return
      
      // Validate minimum length
      if (this.userPrompt.trim().length < 5) {
        alert(this.t('ads.promptTooShort') || 'Please enter at least 5 characters for your ad concept')
        return
      }

      this.creating = true
      try {
        const result = await api.createAdCampaign({
          user_prompt: this.userPrompt,
          brand_name: this.brandName || null,
          brand_description: this.brandDescription || null
        })
        
        console.log('Create campaign result:', result)
        
        // Check if campaign creation failed (LLM error)
        if (result.phase_status === 'failed' || result.error_message) {
          alert(result.error_message || this.t('ads.failedToStartCampaign'))
          this.campaign = result // Still show the campaign with error state
          this.creating = false
          return
        }
        
        this.campaign = result
        
        // Phase 1: Show clarification questions
        if (result.clarification_questions?.length > 0) {
          this.questions = result.clarification_questions
          this.answers = {}
        } else if (result.phase_status === 'processing') {
          this.startPolling()
        }
        
        // Load debug logs (non-blocking)
        this.loadDebugLogs().catch(e => console.error('Failed to load debug logs:', e))

      } catch (error) {
        console.error('Failed to start campaign:', error)
        // Extract error message from response
        let errorMsg = this.t('ads.failedToStartCampaign')
        if (error.response?.data?.detail) {
          const detail = error.response.data.detail
          if (Array.isArray(detail)) {
            // Validation errors
            errorMsg = detail.map(e => e.msg).join(', ')
          } else if (typeof detail === 'string') {
            errorMsg = detail
          }
        } else if (error.message) {
          errorMsg = error.message
        }
        alert(errorMsg)
      } finally {
        this.creating = false
      }
    },

    async loadCampaign(campaignId) {
      try {
        this.campaign = await api.getAdCampaign(campaignId)
        if (this.campaign.clarification_questions?.length > 0 && !this.campaign.user_answers) {
          this.questions = this.campaign.clarification_questions
        }
        if (this.campaign.phase_status === 'processing') {
          this.startPolling()
        }
        await this.loadCampaignDetails(campaignId)
        await this.loadDebugLogs()
      } catch (error) {
        console.error('Failed to load campaign:', error)
      }
    },

    async loadCampaignDetails(campaignId) {
      try {
        const detail = await api.getAdCampaignDetail(campaignId)
        this.scripts = detail.scripts || []
        this.avatars = detail.avatars || []
      } catch (error) {
        console.error('Failed to load campaign details:', error)
      }
    },

    async submitAnswers() {
      if (!this.hasAllAnswers) return

      this.campaign.phase_status = 'processing'
      try {
        const answersList = Object.entries(this.answers).map(([id, answer]) => ({
          question_id: id,
          answer
        }))
        
        const result = await api.submitAdCampaignAnswers(this.campaign.id, answersList)
        console.log('Submit answers result:', result)
        
        // Refresh campaign from server to get full state
        this.campaign = await api.getAdCampaign(this.campaign.id)
        await this.loadDebugLogs()
      } catch (error) {
        console.error('Failed to submit answers:', error)
        this.campaign.error_message = 'Failed to process answers'
        this.campaign.phase_status = 'failed'
      }
    },

    async generateScripts() {
      if (!this.campaign || this.campaign.phase_status === 'processing') return
      
      this.campaign.phase_status = 'processing'
      try {
        const result = await api.generateAdScripts(this.campaign.id, { num_scripts: 5 })
        console.log('Generate scripts result:', result)
        this.scripts = result.scripts || []
        // Refresh campaign state from server
        this.campaign = await api.getAdCampaign(this.campaign.id)
        await this.loadDebugLogs()
      } catch (error) {
        console.error('Failed to generate scripts:', error)
        this.campaign.error_message = error.response?.data?.detail || 'Failed to generate scripts'
        this.campaign.phase_status = 'failed'
        // Refresh to get the actual error state from server
        try {
          this.campaign = await api.getAdCampaign(this.campaign.id)
        } catch (e) {
          console.error('Failed to refresh campaign:', e)
        }
      }
    },

    async continueGeneration() {
      if (!this.campaign || this.campaign.phase_status === 'processing') return
      
      this.campaign.phase_status = 'processing'
      try {
        // Auto-generate remaining phases
        const result = await api.generateAllAdCampaign(this.campaign.id)
        console.log('Generate all result:', result)
        // Refresh campaign state from server
        this.campaign = await api.getAdCampaign(this.campaign.id)
        await this.loadCampaignDetails(this.campaign.id)
        await this.loadDebugLogs()
      } catch (error) {
        console.error('Failed to continue:', error)
        this.campaign.error_message = error.response?.data?.detail || 'Generation failed'
        this.campaign.phase_status = 'failed'
        // Refresh to get the actual error state from server
        try {
          this.campaign = await api.getAdCampaign(this.campaign.id)
        } catch (e) {
          console.error('Failed to refresh campaign:', e)
        }
      }
    },

    startPolling() {
      this.stopPolling()
      this.pollingInterval = setInterval(async () => {
        try {
          const updated = await api.getAdCampaign(this.campaign.id)
          this.campaign = updated
          
          if (updated.clarification_questions?.length > 0 && !updated.user_answers) {
            this.questions = updated.clarification_questions
          }
          
          if (updated.phase_status !== 'processing') {
            this.stopPolling()
            await this.loadCampaignDetails(updated.id)
            await this.loadDebugLogs()
            this.loadPreviousCampaigns()
          }
        } catch (error) {
          console.error('Polling error:', error)
        }
      }, 3000)
    },

    stopPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval)
        this.pollingInterval = null
      }
    },

    resetCampaign() {
      this.stopPolling()
      this.campaign = null
      this.questions = []
      this.answers = {}
      this.scripts = []
      this.avatars = []
      this.selectedScriptId = 1
      this.userPrompt = ''
      this.brandName = ''
      this.brandDescription = ''
      this.loadPreviousCampaigns()
    },

    getPhaseClass(phaseId) {
      if (!this.campaign) return 'pending'
      if (this.campaign.current_phase > phaseId) return 'completed'
      if (this.campaign.current_phase === phaseId) {
        return this.campaign.phase_status === 'completed' ? 'completed' : 'active'
      }
      return 'pending'
    },

    getProcessingMessage() {
      const messages = {
        1: this.t('ads.processingQuestions'),
        2: this.t('ads.processingContext'),
        3: this.t('ads.processingStrategy'),
        4: this.t('ads.processingScripts'),
        5: this.t('ads.processingAvatars'),
        6: this.t('ads.processingStoryboard'),
        7: this.t('ads.processingImages'),
        8: this.t('ads.processingVideos'),
        9: this.t('ads.processingComplete')
      }
      return messages[this.campaign?.current_phase] || this.t('ads.processing')
    },

    getNextPhaseButton() {
      if (this.campaign.current_phase === 3) return this.t('ads.generateScripts')
      if (this.campaign.current_phase === 4 && this.scripts.length === 0) return this.t('ads.generateScripts')
      if (this.campaign.current_phase < 9) return this.t('ads.continueGeneration')
      return this.t('ads.viewResults')
    },

    // Check if user can navigate to a specific phase
    canNavigateToPhase(phaseId) {
      if (!this.campaign) return false
      // Can only navigate to completed phases or the current phase
      return this.campaign.current_phase >= phaseId
    },

    // Redo from a specific phase
    async redoFromPhase(phaseId) {
      if (!this.canNavigateToPhase(phaseId)) return
      if (this.redoingPhase) return // Prevent double-click
      
      const confirmMsg = this.t('ads.confirmRedoPhase') || `Redo from Phase ${phaseId}? This will clear all data from this phase onwards.`
      if (!confirm(confirmMsg)) return

      this.redoingPhase = phaseId
      this.campaign.phase_status = 'processing'
      
      try {
        const result = await api.redoCampaignPhase(this.campaign.id, phaseId)
        
        // If phase 1 needs answers
        if (result.status === 'needs_answers') {
          this.questions = result.questions || []
          this.answers = {}
          this.campaign = await api.getAdCampaign(this.campaign.id)
        } else {
          this.campaign = await api.getAdCampaign(this.campaign.id)
          await this.loadCampaignDetails(this.campaign.id)
        }
        
        // Reload debug logs
        await this.loadDebugLogs()
      } catch (error) {
        console.error('Failed to redo phase:', error)
        this.campaign.error_message = 'Failed to redo phase'
        this.campaign.phase_status = 'failed'
      } finally {
        this.redoingPhase = null
      }
    },

    // Load debug logs
    async loadDebugLogs() {
      if (!this.campaign) return
      try {
        const result = await api.getAdCampaignDebugLogs(this.campaign.id)
        this.debugLogs = result.logs || []
      } catch (error) {
        console.error('Failed to load debug logs:', error)
      }
    },

    // Format log timestamp
    formatLogTime(timestamp) {
      const date = new Date(timestamp * 1000)
      return date.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })
    }
  }
}
</script>

<style scoped>
.ad-generator {
  height: 100%;
}

.generation-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: 100%;
}

/* Preview Area */
.preview-area {
  flex: 1;
  min-height: 300px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}

.preview-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--text-muted);
}

.preview-placeholder svg {
  width: 64px;
  height: 64px;
  opacity: 0.5;
}

.preview-placeholder p {
  font-size: 0.875rem;
}

/* Pipeline Preview */
.pipeline-preview {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow-y: auto;
}

/* Phase Progress */
.phase-progress {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.phase-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.phase-step.active {
  border-color: var(--accent-primary);
  background: rgba(245, 158, 11, 0.1);
}

.phase-step.completed {
  border-color: rgba(34, 197, 94, 0.3);
  background: rgba(34, 197, 94, 0.05);
}

.phase-step.completed .phase-icon {
  background: rgba(34, 197, 94, 0.2);
  color: #22C55E;
}

.phase-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-panel);
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
}

.phase-step.active .phase-icon {
  background: var(--accent-primary);
  color: #000;
}

.phase-icon svg {
  width: 12px;
  height: 12px;
}

.phase-label {
  font-size: 0.625rem;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.phase-step.active .phase-label {
  color: var(--accent-primary);
}

.phase-step.completed .phase-label {
  color: #22C55E;
}

/* Phase Content Area */
.phase-content-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.phase-content {
  width: 100%;
  max-width: 600px;
  text-align: center;
}

.phase-content.processing {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.phase-content.processing p {
  font-size: 0.9375rem;
  color: var(--text-secondary);
}

/* Questions Phase */
.phase-content.questions {
  text-align: left;
}

.phase-content.questions h3 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 20px;
  text-align: center;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.question-item label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.answer-input,
.answer-select {
  width: 100%;
  padding: 12px 14px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.875rem;
}

.answer-input:focus,
.answer-select:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.submit-answers-btn {
  width: 100%;
  margin-top: 20px;
  padding: 14px;
  background: var(--accent-primary);
  border: none;
  border-radius: 10px;
  color: #000;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.submit-answers-btn:hover:not(:disabled) {
  background: var(--accent-primary-hover);
}

.submit-answers-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Strategy Phase */
.phase-content.strategy {
  text-align: left;
}

.phase-content.strategy h3 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 16px;
  text-align: center;
}

.angles-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.angle-card {
  padding: 14px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 10px;
}

.angle-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.angle-id {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--accent-primary);
}

.angle-hook {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

.angle-emotion {
  font-size: 0.8125rem;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.angle-why {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Generated Content Phase */
.phase-content.generated {
  text-align: left;
}

.scripts-section h3,
.avatars-section h3 {
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.scripts-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.script-tab {
  padding: 8px 16px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.8125rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.script-tab.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #000;
}

.script-content {
  padding: 16px;
  background: var(--bg-elevated);
  border-radius: 10px;
  margin-bottom: 24px;
}

.script-hook,
.script-cta {
  margin-bottom: 16px;
}

.script-hook label,
.script-cta label {
  display: block;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--accent-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}

.script-hook p,
.script-cta p {
  font-size: 0.9375rem;
  color: var(--text-primary);
  font-style: italic;
}

.script-scenes {
  margin-bottom: 16px;
}

.scene-item {
  padding: 12px;
  background: var(--bg-panel);
  border-radius: 8px;
  margin-bottom: 8px;
}

.scene-num {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-muted);
}

.scene-dialogue {
  font-size: 0.875rem;
  color: var(--text-primary);
  margin: 6px 0;
}

.scene-visual {
  font-size: 0.8125rem;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.scene-duration {
  font-size: 0.6875rem;
  color: var(--text-muted);
}

/* Avatars */
.avatars-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

.avatar-card {
  padding: 14px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 10px;
}

.avatar-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.avatar-details {
  display: flex;
  gap: 8px;
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.avatar-appearance {
  font-size: 0.8125rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 6px;
}

.avatar-vibe {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-style: italic;
}

/* Action Button */
.action-btn {
  display: block;
  width: 100%;
  padding: 14px;
  background: var(--accent-primary);
  border: none;
  border-radius: 10px;
  color: #000;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  margin-top: 20px;
}

.action-btn:hover {
  background: var(--accent-primary-hover);
}

/* Completed Section */
.completed-section {
  text-align: center;
  padding: 20px;
}

.completed-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #22C55E;
  margin-bottom: 20px;
}

.completed-header svg {
  width: 32px;
  height: 32px;
}

.completed-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
}

.new-campaign-btn {
  padding: 12px 28px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.new-campaign-btn:hover {
  border-color: var(--accent-primary);
}

/* Error State */
.phase-content.error {
  text-align: center;
}

.error-message {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 10px;
  color: #EF4444;
  margin-bottom: 16px;
}

.error-message svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

/* Spinner */
.spinner-large {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Prompt Area */
.prompt-area {
  display: flex;
  gap: 16px;
  align-items: flex-end;
}

.prompt-wrapper {
  flex: 1;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.prompt-input {
  width: 100%;
  padding: 16px 20px;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 0.9375rem;
  line-height: 1.6;
  resize: none;
  font-family: inherit;
}

.prompt-input:focus {
  outline: none;
}

.prompt-input::placeholder {
  color: var(--text-muted);
}

.prompt-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid var(--border-color);
}

.prompt-actions {
  display: flex;
  gap: 12px;
}

.brand-input {
  padding: 10px 14px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.875rem;
  width: 200px;
}

.brand-input:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.brand-input::placeholder {
  color: var(--text-muted);
}

.generate-btn-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.credit-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(34, 197, 94, 0.08));
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #22C55E;
  white-space: nowrap;
}

.credit-badge .credit-icon {
  width: 16px;
  height: 16px;
}

.generate-btn {
  padding: 10px 24px;
  background: var(--accent-primary);
  border: none;
  border-radius: 8px;
  color: #000;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.generate-btn:hover:not(:disabled) {
  background: var(--accent-primary-hover);
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn-content svg {
  width: 16px;
  height: 16px;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(0, 0, 0, 0.2);
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* Recent Section */
.recent-section {
  margin-top: auto;
}

.recent-section h3 {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

.recent-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.recent-card {
  position: relative;
  aspect-ratio: 1;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  transition: all 0.2s ease;
}

.recent-card:hover {
  border-color: var(--border-hover);
  transform: translateY(-2px);
}

.card-status {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  z-index: 1;
}

.card-status.completed {
  background: #22C55E;
}

.card-status.processing {
  background: #F59E0B;
}

.card-status.failed,
.card-status.needs_revision {
  background: #EF4444;
}

.card-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-elevated);
}

.card-placeholder svg {
  width: 32px;
  height: 32px;
  color: var(--text-muted);
  opacity: 0.5;
}

.card-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.85));
}

.card-brand {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
  margin-bottom: 2px;
}

.card-prompt {
  font-size: 0.6875rem;
  color: rgba(255, 255, 255, 0.7);
}

@media (max-width: 900px) {
  .phase-progress {
    flex-wrap: wrap;
  }

  .brand-input {
    width: 150px;
  }

  .recent-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Phase Redo Button */
.phase-redo-btn {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 18px;
  height: 18px;
  padding: 2px;
  background: var(--accent-primary);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.phase-step:hover .phase-redo-btn {
  opacity: 1;
}

.phase-redo-btn svg {
  width: 10px;
  height: 10px;
  color: #000;
}

.phase-redo-btn:hover {
  background: var(--accent-primary-hover);
}

.phase-step {
  position: relative;
  cursor: pointer;
}

/* Debug Panel */
.debug-panel {
  position: absolute;
  bottom: 10px;
  left: 10px;
  right: 10px;
  max-height: 200px;
  background: rgba(0, 0, 0, 0.9);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  font-size: 0.75rem;
}

.debug-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid var(--border-color);
}

.debug-header h4 {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  margin: 0;
}

.debug-refresh-btn {
  padding: 4px;
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  transition: color 0.15s ease;
}

.debug-refresh-btn:hover {
  color: var(--text-primary);
}

.debug-refresh-btn svg {
  width: 14px;
  height: 14px;
}

.debug-logs {
  padding: 8px;
  max-height: 150px;
  overflow-y: auto;
}

.debug-empty {
  color: var(--text-muted);
  text-align: center;
  padding: 12px;
}

.debug-log-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  margin-bottom: 2px;
  background: rgba(255, 255, 255, 0.03);
}

.debug-log-item.start {
  border-left: 2px solid #F59E0B;
}

.debug-log-item.complete {
  border-left: 2px solid #22C55E;
}

.debug-log-item.error,
.debug-log-item.exception {
  border-left: 2px solid #EF4444;
}

.log-time {
  color: var(--text-muted);
  font-family: monospace;
}

.log-phase {
  color: var(--text-secondary);
  flex: 1;
}

.log-status {
  text-transform: uppercase;
  font-size: 0.625rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 3px;
}

.debug-log-item.start .log-status {
  background: rgba(245, 158, 11, 0.2);
  color: #F59E0B;
}

.debug-log-item.complete .log-status {
  background: rgba(34, 197, 94, 0.2);
  color: #22C55E;
}

.debug-log-item.error .log-status,
.debug-log-item.exception .log-status {
  background: rgba(239, 68, 68, 0.2);
  color: #EF4444;
}

.log-data {
  color: var(--text-muted);
  font-family: monospace;
  font-size: 0.6875rem;
}

/* Debug Toggle Button */
.debug-toggle-btn {
  position: absolute;
  bottom: 10px;
  right: 10px;
  width: 32px;
  height: 32px;
  padding: 6px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-muted);
  transition: all 0.15s ease;
}

.debug-toggle-btn:hover,
.debug-toggle-btn.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #000;
}

.debug-toggle-btn svg {
  width: 18px;
  height: 18px;
}
</style>