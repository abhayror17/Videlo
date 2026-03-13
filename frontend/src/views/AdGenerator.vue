<template>
  <div class="ad-generator">
    <!-- Generation View -->
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

        <!-- Campaign in progress: show pipeline -->
        <div v-else class="pipeline-preview">
          <!-- Pipeline Steps -->
          <div class="pipeline-steps">
            <!-- Step 1: Enhancement -->
            <div class="pipeline-step" :class="getStepClass('enhancing')">
              <div class="step-icon">
                <svg v-if="campaign.enhancement_status === 'completed'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <span v-else>1</span>
              </div>
              <span class="step-label">{{ $t('ads.enhance') }}</span>
            </div>

            <!-- Step 2: Script -->
            <div class="pipeline-step" :class="getStepClass('script')">
              <div class="step-icon">
                <svg v-if="campaign.script_status === 'completed'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <span v-else>2</span>
              </div>
              <span class="step-label">{{ $t('ads.script') }}</span>
            </div>

            <!-- Step 3: Image -->
            <div class="pipeline-step" :class="getStepClass('image')">
              <div class="step-icon">
                <svg v-if="campaign.image_status === 'completed'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <span v-else>3</span>
              </div>
              <span class="step-label">{{ $t('ads.image') }}</span>
            </div>

            <!-- Step 4: Video -->
            <div class="pipeline-step" :class="getStepClass('video')">
              <div class="step-icon">
                <svg v-if="campaign.video_status === 'completed'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <span v-else>4</span>
              </div>
              <span class="step-label">{{ $t('ads.video') }}</span>
            </div>

            <!-- Step 5: QA -->
            <div class="pipeline-step" :class="getStepClass('qa')">
              <div class="step-icon">
                <svg v-if="campaign.qa_status === 'approved'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <svg v-else-if="campaign.qa_status === 'rejected'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
                <span v-else>5</span>
              </div>
              <span class="step-label">{{ $t('ads.qa') }}</span>
            </div>
          </div>

          <!-- Current Step Content -->
          <div class="step-content-area">
            <!-- Enhancement -->
            <div v-if="campaign.current_step === 'enhancing'" class="step-content processing">
              <div class="spinner-large"></div>
              <p>{{ $t('ads.enhancingConcept') }}</p>
            </div>

            <!-- Script -->
            <div v-else-if="campaign.script && campaign.current_step === 'script'" class="step-content">
              <div class="script-preview">
                <label>{{ $t('ads.adScript') }}</label>
                <p>{{ parsedScript?.script || campaign.script }}</p>
              </div>
            </div>

            <!-- Image -->
            <div v-else-if="campaign.image_url && (campaign.current_step === 'image' || campaign.current_step === 'video' || campaign.current_step === 'qa')" class="step-content">
              <img :src="campaign.image_url" class="generated-image" />
            </div>
            <div v-else-if="campaign.image_status === 'processing'" class="step-content processing">
              <div class="spinner-large"></div>
              <p>{{ $t('ads.generatingBrandImage') }}</p>
            </div>

            <!-- Video -->
            <div v-else-if="campaign.video_url" class="step-content">
              <video :src="campaign.video_url" controls muted loop class="generated-video"></video>
            </div>
            <div v-else-if="campaign.video_status === 'processing'" class="step-content processing">
              <div class="spinner-large"></div>
              <p>{{ $t('ads.generatingVideoAd') }}</p>
              <span class="progress-note">{{ $t('ads.mayTakeFewMinutes') }}</span>
            </div>

            <!-- QA -->
            <div v-else-if="campaign.qa_status === 'processing'" class="step-content processing">
              <div class="spinner-large"></div>
              <p>{{ $t('ads.runningQA') }}</p>
            </div>

            <!-- Completed -->
            <div v-else-if="campaign.overall_status === 'completed'" class="step-content completed">
              <div class="completed-header">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                <h3>{{ $t('ads.campaignComplete') }}</h3>
              </div>
              <video v-if="campaign.video_url" :src="campaign.video_url" controls muted loop class="generated-video"></video>
              <div class="completed-actions">
                <button @click="downloadVideo" class="download-btn">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                  </svg>
                  {{ $t('ads.downloadVideo') }}
                </button>
              </div>
            </div>

            <!-- Error -->
            <div v-else-if="campaign.error_message" class="step-content error">
              <div class="error-message">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <span>{{ campaign.error_message }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Prompt Area -->
      <div class="prompt-area">
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
                <span v-if="creating || (campaign && campaign.overall_status === 'processing')" class="btn-content">
                  <span class="spinner"></span>
                  <span>{{ creating ? $t('ads.starting') : $t('ads.processing') }}</span>
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
            <img v-if="camp.image_url" :src="camp.image_url" class="card-image" />
            <div v-else class="card-placeholder">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="2" y="4" width="20" height="16" rx="2"/>
                <path d="M10 9l5 3-5 3V9z"/>
              </svg>
            </div>
            <div class="card-info">
              <span class="card-brand">{{ camp.brand_name || $t('ads.noBrand') }}</span>
              <span class="card-prompt">{{ camp.user_prompt.substring(0, 40) }}...</span>
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
      previousCampaigns: []
    }
  },
  computed: {
    promptPlaceholder() {
      if (this.campaign) {
        return this.t('ads.describeAdConcept')
      }
      return this.t('ads.describeAdConcept')
    },
    parsedScript() {
      if (!this.campaign?.script) return null
      try {
        return JSON.parse(this.campaign.script)
      } catch {
        return { script: this.campaign.script }
      }
    },
    adCredits() {
      // Ad campaign includes: image generation (~10) + video generation (~20)
      // Total estimated credits for a complete ad campaign
      return 30
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

      this.creating = true
      try {
        const result = await api.createAdCampaign({
          user_prompt: this.userPrompt,
          brand_name: this.brandName || null,
          brand_description: this.brandDescription || null
        })

        this.campaign = result
        this.startPolling()

      } catch (error) {
        console.error('Failed to start campaign:', error)
        alert(this.t('ads.failedToStartCampaign'))
      } finally {
        this.creating = false
      }
    },

    async loadCampaign(campaignId) {
      try {
        this.campaign = await api.getAdCampaign(campaignId)
        if (this.campaign.overall_status === 'processing') {
          this.startPolling()
        }
      } catch (error) {
        console.error('Failed to load campaign:', error)
      }
    },

    startPolling() {
      this.stopPolling()
      this.pollingInterval = setInterval(async () => {
        try {
          const updated = await api.getAdCampaignStatus(this.campaign.id)
          this.campaign = updated

          if (updated.overall_status !== 'processing') {
            this.stopPolling()
            this.loadPreviousCampaigns()
          }
        } catch (error) {
          console.error('Polling error:', error)
        }
      }, 5000)
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
      this.userPrompt = ''
      this.brandName = ''
      this.brandDescription = ''
      this.loadPreviousCampaigns()
    },

    getStepClass(step) {
      const stepOrder = ['init', 'enhancing', 'script', 'image', 'video', 'qa', 'completed']
      const currentIndex = stepOrder.indexOf(this.campaign?.current_step)
      const stepIndex = stepOrder.indexOf(step)

      if (this.campaign?.current_step === step) return 'active'
      if (currentIndex > stepIndex || this.campaign?.overall_status === 'completed') return 'completed'
      return 'pending'
    },

    downloadVideo() {
      if (this.campaign?.video_url) {
        window.open(this.campaign.video_url, '_blank')
      }
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
  padding: 24px;
}

/* Pipeline Steps */
.pipeline-steps {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 24px;
}

.pipeline-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  transition: all 0.2s ease;
}

.pipeline-step.active {
  border-color: var(--accent-primary);
  background: rgba(245, 158, 11, 0.1);
}

.pipeline-step.completed {
  border-color: rgba(34, 197, 94, 0.3);
  background: rgba(34, 197, 94, 0.05);
}

.pipeline-step.completed .step-icon {
  background: rgba(34, 197, 94, 0.2);
  color: #22C55E;
}

.step-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-panel);
  border-radius: 50%;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-muted);
}

.pipeline-step.active .step-icon {
  background: var(--accent-primary);
  color: #000;
}

.step-icon svg {
  width: 14px;
  height: 14px;
}

.step-label {
  font-size: 0.6875rem;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.pipeline-step.active .step-label {
  color: var(--accent-primary);
}

.pipeline-step.completed .step-label {
  color: #22C55E;
}

/* Step Content Area */
.step-content-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.step-content {
  width: 100%;
  max-width: 480px;
  text-align: center;
}

.step-content.processing {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.step-content.processing p {
  font-size: 0.9375rem;
  color: var(--text-secondary);
}

.progress-note {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.script-preview {
  text-align: left;
  padding: 20px;
  background: var(--bg-elevated);
  border-radius: 12px;
}

.script-preview label {
  display: block;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.script-preview p {
  color: var(--text-primary);
  line-height: 1.6;
}

.generated-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 12px;
  object-fit: contain;
}

.generated-video {
  max-width: 100%;
  max-height: 300px;
  border-radius: 12px;
}

/* Completed State */
.step-content.completed {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.completed-header {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #22C55E;
}

.completed-header svg {
  width: 28px;
  height: 28px;
}

.completed-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
}

.completed-actions {
  margin-top: 8px;
}

.download-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--accent-primary);
  border: none;
  border-radius: 10px;
  color: #000;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.download-btn:hover {
  background: var(--accent-primary-hover);
}

.download-btn svg {
  width: 16px;
  height: 16px;
}

/* Error State */
.step-content.error {
  padding: 20px;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 10px;
  color: #EF4444;
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

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
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
  .pipeline-steps {
    flex-wrap: wrap;
  }

  .brand-input {
    width: 150px;
  }

  .recent-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
