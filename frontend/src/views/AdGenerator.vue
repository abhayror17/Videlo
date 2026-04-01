<template>
  <div class="ads-page">
    <!-- Header -->
    <header class="page-header">
      <div class="header-content">
        <h1>{{ $t('ads.generateAd') }}</h1>
        <p class="header-subtitle">{{ $t('ads.subtitle') }}</p>
      </div>
      <button class="campaigns-toggle" @click="showCampaigns = !showCampaigns">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
        </svg>
        <span>{{ $t('ads.myCampaigns') }}</span>
        <span class="campaign-count">{{ campaigns.length }}</span>
      </button>
    </header>

    <!-- Step Progress -->
    <div class="step-progress">
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: progressWidth }"></div>
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
      <!-- Step 1: Brief -->
      <div v-if="currentStep === 0" class="step-panel">
        <div class="step-header">
          <h2>{{ $t('ads.campaignBrief') }}</h2>
        </div>
        <div class="step-body">
          <div class="form-group">
            <label>{{ $t('ads.brandName') }}</label>
            <input v-model="form.brandName" type="text" :placeholder="$t('ads.brandNamePlaceholder')" />
          </div>
          <div class="form-group">
            <label>{{ $t('ads.brandDescription') }}</label>
            <textarea v-model="form.brandDescription" rows="2" :placeholder="$t('ads.brandDescriptionPlaceholder')"></textarea>
          </div>
          <div class="form-group">
            <label>{{ $t('ads.campaignBrief') }}</label>
            <textarea
              v-model="form.prompt"
              rows="5"
              :placeholder="$t('ads.describeAdConcept')"
            ></textarea>
          </div>
          <div class="form-tips">
            <p><strong>Tip:</strong> Describe your product, target audience, key message, and desired tone for best results.</p>
          </div>
        </div>
        <div class="step-actions">
          <button
            class="btn-primary generate"
            :disabled="isGenerating || !form.prompt.trim()"
            @click="createAndGenerateCampaign"
          >
            <svg v-if="isGenerating" class="spinner" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-dasharray="31.4 31.4" transform="rotate(-90 12 12)"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
            {{ isGenerating ? $t('ads.generating') : $t('ads.generateEverything') }}
          </button>
        </div>
      </div>

      <!-- Step 2: Scripts -->
      <div v-if="currentStep === 1" class="step-panel">
        <div class="step-header">
          <h2>{{ $t('ads.generatedScripts') }}</h2>
          <span class="badge">{{ campaignDetail?.scripts?.length || 0 }}</span>
        </div>
        <div class="step-body">
          <div v-if="!campaignDetail?.scripts?.length" class="empty-state">
            <p>{{ $t('ads.noScriptsYet') }}</p>
            <p class="empty-hint">{{ $t('ads.completeBriefFirst') }}</p>
          </div>
          <div v-else class="scripts-list">
            <div
              v-for="(script, index) in campaignDetail.scripts"
              :key="script.id"
              class="script-card"
              :class="{ expanded: expandedScript === script.id }"
            >
              <div class="script-header" @click="toggleScript(script.id)">
                <div class="script-meta">
                  <span class="script-number">#{{ index + 1 }}</span>
                  <span class="script-hook">{{ truncateText(script.hook, 60) }}</span>
                </div>
                <svg class="expand-icon" :class="{ rotated: expandedScript === script.id }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 5l7 7-7 7"/>
                </svg>
              </div>
              <div v-if="expandedScript === script.id" class="script-body">
                <div class="script-section">
                  <span class="script-label">{{ $t('ads.hook') }}</span>
                  <p>{{ script.hook }}</p>
                </div>
                <div class="script-section">
                  <span class="script-label">{{ $t('ads.cta') }}</span>
                  <p>{{ script.cta }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="step-actions">
          <button class="btn-secondary" @click="goToStep(0)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M15 19l-7-7 7-7"/>
            </svg>
            {{ $t('common.back') }}
          </button>
          <button
            class="btn-primary"
            :disabled="!campaignDetail?.scripts?.length"
            @click="goToStep(2)"
          >
            {{ $t('common.next') }}
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 5l7 7-7 7"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Step 3: Scenes & Assets -->
      <div v-if="currentStep === 2" class="step-panel">
        <div class="step-header">
          <h2>{{ $t('ads.sceneAssets') }}</h2>
          <div class="header-actions">
            <button
              class="btn-small"
              :disabled="busyImages"
              @click="generateSceneImages"
            >
              {{ busyImages ? $t('ads.generating') : $t('ads.generateImages') }}
            </button>
            <button
              class="btn-small"
              :disabled="busyVideos"
              @click="generateSceneVideos"
            >
              {{ busyVideos ? $t('ads.generating') : $t('ads.generateVideos') }}
            </button>
          </div>
        </div>
        
        <div class="step-body">
          <div v-if="!allScenes.length" class="empty-state">
            <p>{{ $t('ads.noScenesYet') }}</p>
          </div>
          <div v-else class="scenes-grid">
            <div
              v-for="scene in allScenes"
              :key="scene.id"
              class="scene-card"
            >
              <div class="scene-preview">
                <img v-if="scene.image_url" :src="scene.image_url" alt="" @click="openPreview(scene)" />
                <div v-else class="preview-placeholder">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <rect x="3" y="3" width="18" height="18" rx="2"/>
                    <circle cx="8.5" cy="8.5" r="1.5"/>
                    <path d="M21 15l-5-5L5 21"/>
                  </svg>
                </div>
                <div class="scene-badges">
                  <StatusBadge :status="scene.image_status || 'pending'" class="compact" />
                  <StatusBadge :status="scene.video_status || 'pending'" class="compact" />
                </div>
              </div>
              <div class="scene-info">
                <span class="scene-number">{{ $t('ads.scene') }} {{ scene.scene_num }}</span>
                <p class="scene-prompt">{{ truncateText(scene.image_prompt, 80) }}</p>
              </div>
              <div class="scene-actions">
                <button
                  class="btn-icon"
                  :disabled="busySceneId === `image-${scene.id}`"
                  @click="regenerateSceneImage(scene)"
                  :title="$t('ads.regenerateImage')"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                  </svg>
                </button>
                <button
                  class="btn-icon"
                  :disabled="busySceneId === `video-${scene.id}` || !scene.image_url"
                  @click="regenerateSceneVideo(scene)"
                  :title="$t('ads.regenerateVideo')"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                  </svg>
                </button>
                <a
                  v-if="scene.video_url"
                  :href="scene.video_url"
                  target="_blank"
                  rel="noopener"
                  class="btn-icon"
                  :title="$t('ads.downloadVideo')"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                  </svg>
                </a>
              </div>
            </div>
          </div>
        </div>
        
        <div class="step-actions">
          <button class="btn-secondary" @click="goToStep(1)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M15 19l-7-7 7-7"/>
            </svg>
            {{ $t('common.back') }}
          </button>
        </div>
      </div>

      <!-- Status Message -->
      <div v-if="statusMessage" class="status-toast" :class="{ error: statusError, success: statusTone === 'success' }">
        <p>{{ statusMessage }}</p>
        <button class="toast-close" @click="clearStatus">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
    </main>

    <!-- Campaigns Drawer -->
    <Teleport to="body">
      <Transition name="drawer">
        <div v-if="showCampaigns" class="drawer-overlay" @click.self="showCampaigns = false">
          <div class="campaigns-drawer">
            <div class="drawer-header">
              <h2>{{ $t('ads.myCampaigns') }}</h2>
              <button class="drawer-close" @click="showCampaigns = false">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
            <div class="drawer-body">
              <div v-if="loadingCampaigns" class="drawer-loading">
                <div class="spinner"></div>
              </div>
              <div v-else-if="!campaigns.length" class="drawer-empty">
                <p>{{ $t('ads.noCampaigns') }}</p>
              </div>
              <div v-else class="campaigns-list">
                <div
                  v-for="campaign in campaigns"
                  :key="campaign.id"
                  class="campaign-card"
                  :class="{ active: campaign.id === activeCampaignId }"
                  @click="selectCampaign(campaign.id)"
                >
                  <div class="campaign-preview">
                    <img v-if="getFirstSceneImage(campaign)" :src="getFirstSceneImage(campaign)" alt="" />
                    <div v-else class="preview-placeholder">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <rect x="3" y="3" width="18" height="18" rx="2"/>
                        <circle cx="8.5" cy="8.5" r="1.5"/>
                        <path d="M21 15l-5-5L5 21"/>
                      </svg>
                    </div>
                    <StatusBadge :status="campaign.overall_status || 'pending'" class="campaign-status" />
                  </div>
                  <div class="campaign-info">
                    <span class="campaign-name">{{ getCampaignTitle(campaign) }}</span>
                    <span class="campaign-date">{{ formatDate(campaign.created_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Preview Modal -->
    <Teleport to="body">
      <div v-if="previewScene" class="modal-overlay" @click.self="previewScene = null">
        <div class="preview-modal">
          <button class="modal-close" @click="previewScene = null">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
          <div class="preview-content">
            <video v-if="previewScene.video_url" :src="previewScene.video_url" controls autoplay></video>
            <img v-else-if="previewScene.image_url" :src="previewScene.image_url" alt="" />
          </div>
          <div class="preview-actions">
            <a v-if="previewScene.video_url" :href="previewScene.video_url" target="_blank" class="btn-primary">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              {{ $t('ads.downloadVideo') }}
            </a>
            <a v-else-if="previewScene.image_url" :href="previewScene.image_url" target="_blank" class="btn-primary">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              {{ $t('ads.downloadImage') }}
            </a>
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
  name: 'AdGenerator',
  components: { StatusBadge },
  setup() {
    const { t } = useI18n()
    return { t }
  },
  data() {
    return {
      currentStep: 0,
      showCampaigns: false,
      expandedScript: null,
      previewScene: null,
      pollInterval: null,
      form: {
        prompt: '',
        brandName: '',
        brandDescription: ''
      },
      steps: [
        { id: 'brief', label: 'Brief' },
        { id: 'scripts', label: 'Scripts' },
        { id: 'scenes', label: 'Scenes' }
      ],
      campaigns: [],
      activeCampaignId: null,
      campaignDetail: null,
      loadingCampaigns: false,
      isGenerating: false,
      busyImages: false,
      busyVideos: false,
      busySceneId: null,
      statusMessage: '',
      statusError: '',
      statusTone: 'neutral'
    }
  },
  computed: {
    progressWidth() {
      // Progress advances as user moves through steps
      // On step 0: 0%, On step 1: 33%, On step 2: 66%, After generate: 100%
      const hasResults = this.allScenes.some(s => s.image_url || s.video_url)
      if (hasResults) {
        return '100%'
      }
      return `${(this.currentStep / this.steps.length) * 100}%`
    },
    allScenes() {
      if (!this.campaignDetail?.storyboards) return []
      return this.campaignDetail.storyboards.flatMap(storyboard => storyboard.scene_prompts || [])
    },
    hasProcessingScenes() {
      return this.allScenes.some(s => s.image_status === 'processing' || s.video_status === 'processing')
    }
  },
  mounted() {
    this.loadCampaigns()
  },
  beforeUnmount() {
    this.stopPolling()
  },
  methods: {
    isStepCompleted(index) {
      if (!this.campaignDetail) return false
      if (index === 0) return !!this.campaignDetail.user_prompt
      if (index === 1) return this.campaignDetail.scripts?.length > 0
      if (index === 2) return this.allScenes.some(s => s.image_url || s.video_url)
      return false
    },
    canGoToStep(index) {
      return true
    },
    goToStep(index) {
      this.currentStep = index
    },
    toggleScript(scriptId) {
      this.expandedScript = this.expandedScript === scriptId ? null : scriptId
    },
    truncateText(text, maxLength) {
      if (!text) return ''
      return text.length > maxLength ? text.slice(0, maxLength) + '...' : text
    },
    formatDate(date) {
      if (!date) return ''
      return new Date(date).toLocaleDateString()
    },
    openPreview(scene) {
      this.previewScene = scene
    },
    clearStatus() {
      this.statusMessage = ''
      this.statusError = ''
    },
    getFirstSceneImage(campaign) {
      // Campaigns in list don't have storyboards loaded, return null
      // The detail view will have the actual scene images
      return null
    },

    async loadCampaigns() {
      this.loadingCampaigns = true
      try {
        const response = await api.getAdCampaigns(1, 20)
        this.campaigns = response.items || []
      } catch (error) {
        console.error('Failed to load campaigns:', error)
      } finally {
        this.loadingCampaigns = false
      }
    },

    async selectCampaign(campaignId) {
      this.activeCampaignId = campaignId
      this.showCampaigns = false
      this.statusMessage = ''
      this.statusError = ''
      
      try {
        await this.loadCampaignDetail(campaignId)
        
        // Go to appropriate step based on campaign progress
        if (!this.campaignDetail) {
          this.currentStep = 0
          return
        }
        
        // If campaign has storyboards with scene prompts, go to step 2 (scenes)
        if (this.campaignDetail.storyboards?.length > 0) {
          this.currentStep = 2
        }
        // If campaign has scripts, go to step 1 (scripts)
        else if (this.campaignDetail.scripts?.length > 0) {
          this.currentStep = 1
        }
        // Otherwise stay at step 0 (brief)
        else {
          this.currentStep = 0
          // Pre-fill form if campaign has user_prompt
          if (this.campaignDetail.user_prompt) {
            this.form.prompt = this.campaignDetail.user_prompt
          }
          if (this.campaignDetail.context?.brand) {
            this.form.brandName = this.campaignDetail.context.brand
          }
        }
      } catch (error) {
        console.error('Failed to select campaign:', error)
        this.statusMessage = this.t('ads.failedToLoadCampaign')
        this.statusError = true
      }
    },

    async loadCampaignDetail(campaignId = this.activeCampaignId) {
      if (!campaignId) return
      try {
        // First fetch the campaign details
        this.campaignDetail = await api.getAdCampaignDetail(campaignId)
        
        // Only check status if campaign has scene prompts that are processing
        if (this.hasProcessingScenes) {
          try {
            await api.checkAdCampaignStatus(campaignId)
            // Refresh after status check
            this.campaignDetail = await api.getAdCampaignDetail(campaignId)
          } catch (statusError) {
            console.warn('Status check failed, using cached data:', statusError)
          }
        }
        
        // Start polling if still processing
        if (this.campaignDetail?.overall_status === 'processing') {
          this.startPolling()
        } else {
          this.stopPolling()
        }
      } catch (error) {
        console.error('Failed to load campaign:', error)
        this.statusMessage = this.t('ads.failedToLoadCampaign')
        this.statusError = true
      }
    },

    startPolling() {
      this.stopPolling()
      // Increased from 5s to 15s to reduce API requests
      this.pollInterval = setInterval(async () => {
        if (!this.activeCampaignId) return
        try {
          // Check status only if there are processing scenes
          if (this.hasProcessingScenes) {
            try {
              await api.checkAdCampaignStatus(this.activeCampaignId)
            } catch (e) {
              console.warn('Status check failed:', e)
            }
          }
          // Always refresh details
          this.campaignDetail = await api.getAdCampaignDetail(this.activeCampaignId)
          
          if (this.campaignDetail?.overall_status !== 'processing') {
            this.stopPolling()
          }
        } catch (error) {
          console.error('Polling error:', error)
        }
      }, 15000)
    },

    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
        this.pollInterval = null
      }
    },

    async createAndGenerateCampaign() {
      if (!this.form.prompt.trim()) return

      this.isGenerating = true
      this.statusMessage = this.t('ads.creatingCampaign')

      try {
        const campaign = await api.createAdCampaign({
          user_prompt: this.form.prompt.trim(),
          brand_name: this.form.brandName.trim() || null,
          brand_description: this.form.brandDescription.trim() || null
        })

        this.activeCampaignId = campaign.id
        this.statusMessage = this.t('ads.generatingPipeline')

        await api.generateAllAdCampaign(campaign.id, {
          numScripts: 5,
          numAvatars: 3
        })

        await this.loadCampaigns()
        await this.loadCampaignDetail(campaign.id)
        
        this.currentStep = 1
        this.statusMessage = this.t('ads.campaignReady')
        this.statusTone = 'success'
        
        setTimeout(() => this.clearStatus(), 3000)
      } catch (error) {
        console.error('Failed:', error)
        this.statusMessage = error?.response?.data?.detail || this.t('ads.failedToGenerateCampaign')
        this.statusError = true
      } finally {
        this.isGenerating = false
      }
    },

    async generateSceneImages() {
      if (!this.activeCampaignId) return
      this.busyImages = true
      this.statusMessage = this.t('ads.generatingImages')
      try {
        await api.generateAdCampaignImages(this.activeCampaignId)
        await this.loadCampaignDetail()
        this.statusMessage = this.t('ads.imagesReady')
        this.statusTone = 'success'
        setTimeout(() => this.clearStatus(), 2000)
      } catch (error) {
        console.error('Failed:', error)
        this.statusMessage = this.t('ads.failedToGenerateImages')
        this.statusError = true
      } finally {
        this.busyImages = false
      }
    },

    async generateSceneVideos() {
      if (!this.activeCampaignId) return
      this.busyVideos = true
      this.statusMessage = this.t('ads.generatingVideos')
      try {
        await api.generateAdCampaignVideos(this.activeCampaignId)
        await this.loadCampaignDetail()
        this.statusMessage = this.t('ads.videosReady')
        this.statusTone = 'success'
        setTimeout(() => this.clearStatus(), 2000)
      } catch (error) {
        console.error('Failed:', error)
        this.statusMessage = this.t('ads.failedToGenerateVideos')
        this.statusError = true
      } finally {
        this.busyVideos = false
      }
    },

    async regenerateSceneImage(scene) {
      if (!this.activeCampaignId || !scene?.id) return
      this.busySceneId = `image-${scene.id}`
      try {
        await api.regenerateAdSceneImage(this.activeCampaignId, scene.id, scene.image_prompt)
        await this.loadCampaignDetail()
      } catch (error) {
        console.error('Failed:', error)
      } finally {
        this.busySceneId = null
      }
    },

    async regenerateSceneVideo(scene) {
      if (!this.activeCampaignId || !scene?.id) return
      this.busySceneId = `video-${scene.id}`
      try {
        await api.regenerateAdSceneVideo(this.activeCampaignId, scene.id, scene.video_prompt)
        await this.loadCampaignDetail()
      } catch (error) {
        console.error('Failed:', error)
      } finally {
        this.busySceneId = null
      }
    },

    getCampaignTitle(campaign) {
      if (!campaign) return this.t('ads.noBrand')
      if (campaign.brand_name) return campaign.brand_name
      if (campaign.user_prompt) return campaign.user_prompt.slice(0, 50)
      return this.t('ads.noBrand')
    }
  }
}
</script>

<style scoped>
.ads-page {
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

.campaigns-toggle {
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

.campaigns-toggle:hover {
  background: var(--bg-elevated);
  border-color: var(--accent-primary);
}

.campaigns-toggle svg {
  width: 18px;
  height: 18px;
}

.campaign-count {
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
  cursor: pointer;
  padding: 0;
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
  position: relative;
}

.step-panel {
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 32px;
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

.badge {
  background: var(--accent-primary);
  color: #000;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.step-body {
  margin-bottom: 24px;
}

/* Form Elements */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.form-group input,
.form-group textarea {
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

.form-group input:focus,
.form-group textarea:focus {
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

/* Buttons */
.step-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary {
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

.btn-primary {
  background: var(--accent-primary);
  border: none;
  color: #000;
}

.btn-primary:hover {
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

.btn-small {
  padding: 8px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-small:hover {
  background: var(--bg-elevated);
  border-color: var(--accent-primary);
}

.btn-small:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.15s;
  text-decoration: none;
}

.btn-icon:hover {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #000;
}

.btn-icon:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon svg {
  width: 18px;
  height: 18px;
}

.spinner {
  width: 18px;
  height: 18px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Scripts */
.scripts-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.script-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.script-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  cursor: pointer;
  transition: background 0.15s;
}

.script-header:hover {
  background: rgba(255, 255, 255, 0.02);
}

.script-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.script-number {
  background: var(--accent-primary);
  color: #000;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 700;
}

.script-hook {
  color: var(--text-primary);
  font-size: 0.875rem;
}

.expand-icon {
  width: 18px;
  height: 18px;
  color: var(--text-muted);
  transition: transform 0.2s;
}

.expand-icon.rotated {
  transform: rotate(90deg);
}

.script-body {
  padding: 0 16px 16px;
  border-top: 1px solid var(--border-color);
}

.script-section {
  margin-top: 12px;
}

.script-label {
  display: inline-block;
  padding: 4px 8px;
  background: rgba(245, 158, 11, 0.12);
  color: var(--accent-primary);
  font-size: 0.72rem;
  font-weight: 700;
  border-radius: 6px;
  margin-bottom: 6px;
}

.script-section p {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.9375rem;
  line-height: 1.5;
}

/* Scenes Grid */
.scenes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.scene-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  transition: border-color 0.2s;
}

.scene-card:hover {
  border-color: var(--accent-primary);
}

.scene-preview {
  position: relative;
  aspect-ratio: 16/9;
  background: var(--bg-elevated);
  cursor: pointer;
}

.scene-preview img {
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
  width: 32px;
  height: 32px;
}

.scene-badges {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 4px;
}

.scene-badges .compact {
  transform: scale(0.8);
}

.scene-info {
  padding: 12px;
}

.scene-number {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 600;
}

.scene-prompt {
  margin: 6px 0 0;
  font-size: 0.8125rem;
  color: var(--text-primary);
  line-height: 1.4;
}

.scene-actions {
  display: flex;
  gap: 6px;
  padding: 0 12px 12px;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 48px 24px;
  color: var(--text-muted);
}

.empty-state p {
  margin: 0 0 8px;
}

.empty-hint {
  font-size: 0.875rem;
}

/* Status Toast */
.status-toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  z-index: 1000;
}

.status-toast.error {
  border-color: #ef4444;
  background: rgba(127, 29, 29, 0.9);
}

.status-toast.success {
  border-color: #22c55e;
  background: rgba(20, 83, 45, 0.9);
}

.status-toast p {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.9375rem;
}

.toast-close {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 6px;
}

.toast-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.toast-close svg {
  width: 16px;
  height: 16px;
}

/* Campaigns Drawer */
.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
}

.campaigns-drawer {
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

.campaigns-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.campaign-card {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.campaign-card:hover {
  border-color: var(--accent-primary);
}

.campaign-card.active {
  border-color: var(--accent-primary);
  background: rgba(245, 158, 11, 0.05);
}

.campaign-preview {
  position: relative;
  width: 80px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background: var(--bg-elevated);
}

.campaign-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.campaign-preview .preview-placeholder {
  width: 100%;
  height: 100%;
}

.campaign-preview .preview-placeholder svg {
  width: 24px;
  height: 24px;
}

.campaign-status {
  position: absolute;
  bottom: 4px;
  right: 4px;
  transform: scale(0.8);
}

.campaign-info {
  flex: 1;
  min-width: 0;
}

.campaign-name {
  display: block;
  font-weight: 600;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.campaign-date {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Preview Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.preview-modal {
  max-width: 90vw;
  max-height: 90vh;
  position: relative;
}

.modal-close {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  cursor: pointer;
}

.modal-close svg {
  width: 20px;
  height: 20px;
}

.preview-content {
  max-width: 100%;
  max-height: 70vh;
}

.preview-content video,
.preview-content img {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
  border-radius: 8px;
}

.preview-actions {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

/* Drawer Transition */
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.3s ease;
}

.drawer-enter-active .campaigns-drawer,
.drawer-leave-active .campaigns-drawer {
  transition: transform 0.3s ease;
}

.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}

.drawer-enter-from .campaigns-drawer,
.drawer-leave-to .campaigns-drawer {
  transform: translateX(100%);
}

/* Responsive */
@media (max-width: 768px) {
  .ads-page {
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

  .campaigns-toggle {
    padding: 8px 12px;
    font-size: 0.8125rem;
  }

  .campaigns-toggle span:not(.campaign-count) {
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

  .step-panel {
    padding: 20px 16px;
    border-radius: 16px;
  }

  .step-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 20px;
  }

  .step-header h2 {
    font-size: 1.25rem;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .header-actions .btn-small {
    flex: 1;
    justify-content: center;
  }

  .form-group input,
  .form-group textarea {
    padding: 12px;
    font-size: 0.9375rem;
  }

  .form-tips {
    display: none;
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

  .scenes-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .scene-info {
    padding: 10px;
  }

  .scene-prompt {
    font-size: 0.75rem;
  }

  .scene-actions {
    padding: 0 10px 10px;
  }

  .btn-icon {
    width: 32px;
    height: 32px;
  }

  .btn-icon svg {
    width: 16px;
    height: 16px;
  }

  .status-toast {
    left: 12px;
    right: 12px;
    transform: none;
    bottom: 12px;
  }

  .campaigns-drawer {
    width: 100%;
  }

  .campaign-card {
    padding: 10px;
  }

  .campaign-preview {
    width: 60px;
    height: 45px;
  }
}

@media (max-width: 480px) {
  .ads-page {
    padding: 8px;
  }

  .header-content h1 {
    font-size: 1.125rem;
  }

  .campaigns-toggle {
    padding: 8px;
  }

  .step-panel {
    padding: 16px 12px;
    border-radius: 12px;
  }

  .scenes-grid {
    grid-template-columns: 1fr;
  }
}
</style>