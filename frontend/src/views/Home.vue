<template>
  <div class="home">
    <!-- Generation View -->
    <div v-if="currentView !== 'gallery'" class="generation-view">
      <!-- Results Grid (Midjourney Style) -->
      <div class="results-container">
        <!-- Generating Item -->
        <div v-if="generating" class="result-card generating">
          <div class="generating-overlay">
            <div class="generating-animation">
              <div class="pulse"></div>
              <div class="pulse delay-1"></div>
              <div class="pulse delay-2"></div>
            </div>
            <p>{{ $t('home.generating') }}</p>
          </div>
        </div>
        
        <!-- Results Grid -->
        <div v-if="displayGenerations.length > 0" class="results-grid">
          <div
            v-for="gen in displayGenerations"
            :key="gen.id"
            class="result-card"
            :class="{ processing: gen.status === 'processing' }"
            @click="openModal(gen)"
          >
            <!-- Image Result -->
            <img
              v-if="gen.thumbnail_url || gen.remote_url"
              :src="gen.thumbnail_url || gen.remote_url"
              :alt="gen.prompt"
              class="result-image"
              loading="lazy"
            />
            
            <!-- Video Result -->
            <video
              v-else-if="isVideo(gen)"
              :src="gen.remote_url"
              class="result-image"
              muted
              loop
              @mouseover="e => e.target.play()"
              @mouseleave="e => { e.target.pause(); e.target.currentTime = 0 }"
            />
            
            <!-- Processing Placeholder -->
            <div v-else-if="gen.status === 'processing'" class="result-placeholder processing">
              <div class="processing-animation">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="12" r="10" stroke-opacity="0.2"/>
                  <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round">
                    <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
                  </path>
                </svg>
              </div>
              <span>{{ gen.progress || 0 }}%</span>
            </div>
            
            <!-- Hover Overlay -->
            <div class="result-overlay">
              <div class="overlay-actions">
                <button class="action-btn" @click.stop="regenerateItem(gen)" :title="$t('home.regenerate')">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 4v6h6M23 20v-6h-6"/>
                    <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"/>
                  </svg>
                </button>
                <button v-if="!isVideo(gen)" class="action-btn" @click.stop="createVideoFromItem(gen)" :title="$t('home.createVideo')">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M8 5v14l11-7z"/>
                  </svg>
                </button>
                <a v-if="gen.remote_url" :href="gen.remote_url" target="_blank" class="action-btn" @click.stop :title="$t('common.download')">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                  </svg>
                </a>
              </div>
              <p class="overlay-prompt">{{ truncatePrompt(gen.prompt) }}</p>
            </div>
          </div>
        </div>
        
        <!-- Empty State -->
        <div v-else-if="!generating" class="empty-state">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
              <rect x="3" y="3" width="18" height="18" rx="2"/>
              <circle cx="8.5" cy="8.5" r="1.5"/>
              <path d="M21 15l-5-5L5 21"/>
            </svg>
          </div>
          <p class="empty-title">{{ $t('home.noCreationsYet') }}</p>
          <p class="empty-hint">{{ $t('home.startCreating') }}</p>
        </div>
        
        <!-- Upload for img2video -->
        <div v-if="currentView === 'img2video' && !uploadedImagePreview && displayGenerations.length === 0" class="upload-zone" @click="$refs.fileInput.click()">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          <p>{{ $t('home.dropImageHere') }}</p>
          <span>{{ $t('home.orClickToBrowse') }}</span>
          <input ref="fileInput" type="file" accept="image/*" style="display: none" @change="handleFileUpload" />
        </div>
        
        <!-- Uploaded Image Preview for img2video -->
        <div v-if="currentView === 'img2video' && uploadedImagePreview" class="uploaded-preview">
          <img :src="uploadedImagePreview" alt="Uploaded" />
          <button class="remove-upload" @click="clearUpload">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Bottom Input Bar (Midjourney Style) -->
      <div class="input-bar">
        <!-- Expandable Options -->
        <Transition name="slide">
          <div v-if="showOptions" class="options-panel">
            <div class="options-row">
              <div class="option-group">
                <label>Model</label>
                <select v-model="localModel">
                  <optgroup v-if="currentView === 'text2img'" label="Image Models">
                    <option value="Flux_2_Klein_4B_BF16">FLUX.2 Klein</option>
                    <option value="Flux1schnell">FLUX.1 Schnell</option>
                    <option value="ZImageTurbo_INT8">Z-Image Turbo</option>
                  </optgroup>
                  <optgroup v-else label="Video Models">
                    <option value="Ltx2_3_22B_Dist_INT8">LTX-2.3 22B</option>
                    <option value="Ltx2_19B_Dist_FP8">LTX-2 19B</option>
                    <option value="Ltxv_13B_0_9_8_Distilled_FP8">LTX-Video 13B</option>
                  </optgroup>
                </select>
              </div>
              
              <div v-if="currentView === 'text2img'" class="option-group">
                <label>Size</label>
                <select v-model="localDimensions">
                  <option value="1024x1024">1:1 Square</option>
                  <option value="768x768">1:1 Small</option>
                  <option value="1024x576">16:9 Landscape</option>
                  <option value="576x1024">9:16 Portrait</option>
                  <option value="1536x864">16:9 HD</option>
                  <option value="864x1536">9:16 HD</option>
                </select>
              </div>
              
              <div v-else class="option-group">
                <label>Aspect</label>
                <select v-model="localVideoDimensions">
                  <option value="768x432">16:9 Landscape</option>
                  <option value="432x768">9:16 Portrait</option>
                  <option value="768x768">1:1 Square</option>
                  <option value="1024x576">16:9 HD</option>
                  <option value="576x1024">9:16 HD</option>
                  <option value="1024x1024">1:1 HD</option>
                </select>
              </div>
              
              <div v-if="currentView !== 'text2img'" class="option-group">
                <label>Duration</label>
                <select v-model="localFrames">
                  <option value="49">~2 sec</option>
                  <option value="120">~5 sec</option>
                  <option value="241">~10 sec</option>
                </select>
              </div>
            </div>
          </div>
        </Transition>
        
        <!-- Main Input -->
        <div class="input-wrapper">
          <button class="options-toggle" :class="{ active: showOptions }" @click="showOptions = !showOptions">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"/>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
            </svg>
          </button>
          
          <button class="input-action" @click="enhancePrompt" :disabled="!prompt.trim() || enhancing" :title="$t('home.enhancePrompt')">
            <svg v-if="!enhancing" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/>
              <path d="M20 3v4M22 5h-4M4 17v2M5 18H3"/>
            </svg>
            <span v-else class="mini-spinner"></span>
          </button>
          
          <button class="input-action" @click="getRandomPrompt" :disabled="gettingRandom" :title="$t('home.getRandomPrompt')">
            <svg v-if="!gettingRandom" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect width="12" height="12" x="2" y="10" rx="2"/>
              <path d="m17.92 14 3.5-3.5a2.24 2.24 0 0 0 0-3l-5-4.92a2.24 2.24 0 0 0-3 0L10 6"/>
              <circle cx="6" cy="18" r="1"/>
              <circle cx="10" cy="14" r="1"/>
              <circle cx="15" cy="6" r="1"/>
              <circle cx="18" cy="9" r="1"/>
            </svg>
            <span v-else class="mini-spinner"></span>
          </button>
          
          <input
            v-model="prompt"
            type="text"
            :placeholder="placeholderText"
            class="prompt-input"
            @keydown.enter="handleGenerate"
          />
          
          <button
            class="generate-btn"
            :disabled="!canGenerate"
            @click="handleGenerate"
          >
            <span v-if="generating" class="btn-spinner"></span>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Gallery View -->
    <div v-else class="gallery-view">
      <Gallery ref="gallery" @select="openModal" @create-video="createVideoFromItem" />
    </div>

    <!-- Image Modal -->
    <ImageModal :visible="modalVisible" :generation="selectedGeneration" @close="closeModal" />
  </div>
</template>

<script>
import { useI18n } from 'vue-i18n'
import Gallery from '../components/Gallery.vue'
import ImageModal from '../components/ImageModal.vue'
import api from '../services/api.js'

export default {
  name: 'Home',
  components: { Gallery, ImageModal },
  props: {
    currentView: { type: String, default: 'text2img' },
    generationOptions: { type: Object, default: () => ({}) }
  },
  setup() {
    const { t } = useI18n()
    return { t }
  },
  data() {
    return {
      prompt: '',
      modalVisible: false,
      selectedGeneration: {},
      generating: false,
      enhancing: false,
      gettingRandom: false,
      showOptions: false,
      generations: [],
      pollingIds: {},
      recentPollingInterval: null,
      // Local options
      localModel: 'Flux_2_Klein_4B_BF16',
      localDimensions: '1024x1024',
      localVideoDimensions: '768x432',
      localFrames: '120',
      // Upload
      uploadedImageFile: null,
      uploadedImagePreview: null
    }
  },
  computed: {
    placeholderText() {
      if (this.currentView === 'text2img') return this.t('home.describeImage')
      if (this.currentView === 'txt2video') return this.t('home.describeVideo')
      return this.t('home.describeTransformation')
    },
    displayGenerations() {
      return this.generations.filter(g => g.status !== 'failed').slice(0, 12)
    },
    canGenerate() {
      if (!this.prompt.trim() || this.generating) return false
      if (this.currentView === 'img2video' && !this.uploadedImageFile) return false
      return true
    }
  },
  watch: {
    currentView() {
      this.loadGenerations()
      if (this.currentView === 'txt2video' || this.currentView === 'img2video') {
        this.localModel = 'Ltx2_3_22B_Dist_INT8'
      } else {
        this.localModel = 'Flux_2_Klein_4B_BF16'
      }
    },
    localModel() { this.emitOptions() },
    localDimensions() { this.emitOptions() },
    localVideoDimensions() { this.emitOptions() },
    localFrames() { this.emitOptions() }
  },
  mounted() {
    this.loadGenerations()
    this.startPolling()
  },
  beforeUnmount() {
    this.stopPolling()
  },
  methods: {
    isVideo(gen) {
      return gen.generation_type === 'img2video' ||
        gen.generation_type === 'txt2video' ||
        gen.generation_type === 'audio2video' ||
        (gen.remote_url && gen.remote_url.endsWith('.mp4'))
    },
    truncatePrompt(prompt) {
      if (!prompt) return ''
      return prompt.length > 100 ? prompt.slice(0, 100) + '...' : prompt
    },
    emitOptions() {
      const [width, height] = (this.localDimensions || '1024x1024').split('x').map(Number)
      const [vw, vh] = (this.localVideoDimensions || '768x432').split('x').map(Number)
      this.$emit('update-options', {
        model: this.localModel,
        width, height,
        videoWidth: vw,
        videoHeight: vh,
        steps: this.localModel === 'Flux_2_Klein_4B_BF16' ? 4 : 8,
        frames: parseInt(this.localFrames) || 120,
        fps: 24
      })
    },
    async loadGenerations() {
      try {
        const response = await api.getGenerations(1, 20)
        this.generations = response.items || []
      } catch (error) {
        // Silently handle errors
      }
    },
    startPolling() {
      // Increased from 5s to 15s to reduce API requests
      this.recentPollingInterval = setInterval(() => this.pollInProgress(), 15000)
    },
    stopPolling() {
      if (this.recentPollingInterval) {
        clearInterval(this.recentPollingInterval)
        this.recentPollingInterval = null
      }
    },
    async pollInProgress() {
      const inProgress = this.generations.filter(g => g.status === 'processing')
      // Don't poll if nothing is in progress - save API requests
      if (inProgress.length === 0) {
        this.stopPolling()
        return
      }
      
      for (const gen of inProgress) {
        try {
          const updated = await api.getStatus(gen.id)
          const index = this.generations.findIndex(g => g.id === gen.id)
          if (index !== -1) {
            // If generation failed, remove it from the list (don't show errors)
            if (updated.status === 'failed') {
              this.generations.splice(index, 1)
            } else {
              this.generations[index] = { ...this.generations[index], ...updated }
            }
          }
          // Stop polling early if this item completed or failed
          if (updated.status === 'completed' || updated.status === 'failed') {
            if (updated.status === 'completed') {
              await this.loadGenerations()
            }
            if (this.$refs.gallery) this.$refs.gallery.refresh()
            // Check if we should stop polling entirely
            const stillProcessing = this.generations.filter(g => g.status === 'processing')
            if (stillProcessing.length === 0) {
              this.stopPolling()
            }
          }
        } catch (error) {
          // Silently handle polling errors - they're expected for expired requests
          // The backend will mark them as failed, and we'll filter them out
        }
      }
    },
    async handleGenerate() {
      if (!this.canGenerate) return
      
      this.generating = true
      try {
        const [width, height] = (this.localDimensions || '1024x1024').split('x').map(Number)
        const [vw, vh] = (this.localVideoDimensions || '768x432').split('x').map(Number)
        
        const options = {
          model: this.localModel,
          width: this.currentView === 'text2img' ? width : vw,
          height: this.currentView === 'text2img' ? height : vh,
          steps: this.localModel === 'Flux_2_Klein_4B_BF16' ? 4 : 8,
          frames: parseInt(this.localFrames) || 120,
          fps: 24
        }
        
        let result
        if (this.currentView === 'text2img') {
          result = await api.generateText2Img(this.prompt, options)
        } else if (this.currentView === 'txt2video') {
          result = await api.generateTxt2Video(this.prompt, options)
        } else if (this.currentView === 'img2video' && this.uploadedImageFile) {
          result = await api.generateImg2VideoWithFile(this.uploadedImageFile, this.prompt, options)
          this.clearUpload()
        }
        
        if (result) {
          await this.loadGenerations()
          if (this.$refs.gallery) this.$refs.gallery.refresh()
        }
      } catch (error) {
        // Silently handle generation errors
      } finally {
        this.generating = false
      }
    },
    async enhancePrompt() {
      if (!this.prompt.trim() || this.enhancing) return
      this.enhancing = true
      try {
        const result = await api.enhancePrompt(this.prompt)
        if (result.enhanced_prompt) this.prompt = result.enhanced_prompt
      } catch (error) {
        // Silently handle enhancement errors
      } finally {
        this.enhancing = false
      }
    },
    async getRandomPrompt() {
      if (this.gettingRandom) return
      this.gettingRandom = true
      try {
        const result = await api.getRandomPrompt()
        if (result.prompt) this.prompt = result.prompt
      } catch (error) {
        // Silently handle random prompt errors
      } finally {
        this.gettingRandom = false
      }
    },
    async regenerateItem(gen) {
      try {
        const options = {
          model: gen.model,
          width: gen.width,
          height: gen.height,
          steps: gen.steps || 4,
          frames: gen.frames || 120,
          fps: 24
        }
        
        if (gen.generation_type === 'text2img') {
          await api.generateText2Img(gen.prompt, options)
        } else if (gen.generation_type === 'txt2video') {
          await api.generateTxt2Video(gen.prompt, options)
        } else if (gen.generation_type === 'img2video') {
          await api.generateImg2Video(gen.source_generation_id, gen.prompt, options)
        }
        
        await this.loadGenerations()
      } catch (error) {
        // Silently handle regenerate errors
      }
    },
    createVideoFromItem(gen) {
      if (this.isVideo(gen)) return
      // Emit event to parent to switch to img2video with this image
      this.$emit('create-video', gen)
    },
    handleFileUpload(event) {
      const file = event.target.files[0]
      if (!file || !file.type.startsWith('image/')) return
      this.uploadedImageFile = file
      this.uploadedImagePreview = URL.createObjectURL(file)
    },
    clearUpload() {
      this.uploadedImageFile = null
      this.uploadedImagePreview = null
    },
    openModal(generation) {
      this.selectedGeneration = generation
      this.modalVisible = true
    },
    closeModal() {
      this.modalVisible = false
      this.selectedGeneration = {}
    }
  }
}
</script>

<style scoped>
.home {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.generation-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* Results Container */
.results-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  min-height: 0;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

/* Result Card */
.result-card {
  position: relative;
  aspect-ratio: 1;
  border-radius: 12px;
  overflow: hidden;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s ease;
}

.result-card:hover {
  border-color: var(--accent-primary);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.result-card:hover .result-overlay {
  opacity: 1;
}

.result-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.result-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--text-muted);
}

.result-placeholder.processing svg {
  width: 32px;
  height: 32px;
  color: var(--accent-primary);
}

.result-placeholder.failed svg {
  width: 32px;
  height: 32px;
  color: #ef4444;
}

/* Hover Overlay */
.result-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, transparent 60%);
  opacity: 0;
  transition: opacity 0.2s ease;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 12px;
}

.overlay-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 6px;
}

.action-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.6);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.15s ease;
  text-decoration: none;
}

.action-btn:hover {
  background: var(--accent-primary);
  color: #000;
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.overlay-prompt {
  margin: 0;
  font-size: 0.75rem;
  color: rgba(255,255,255,0.8);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Generating State */
.result-card.generating {
  background: var(--bg-elevated);
  border: 2px dashed var(--accent-primary);
}

.generating-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 16px;
}

.generating-animation {
  position: relative;
  width: 60px;
  height: 60px;
}

.pulse {
  position: absolute;
  inset: 0;
  border: 2px solid var(--accent-primary);
  border-radius: 50%;
  animation: pulse 1.5s ease-out infinite;
}

.pulse.delay-1 { animation-delay: 0.3s; }
.pulse.delay-2 { animation-delay: 0.6s; }

@keyframes pulse {
  0% { transform: scale(0.5); opacity: 1; }
  100% { transform: scale(1.5); opacity: 0; }
}

.generating-overlay p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
  text-align: center;
  color: var(--text-muted);
}

.empty-icon svg {
  width: 80px;
  height: 80px;
  opacity: 0.3;
  margin-bottom: 16px;
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

/* Upload Zone */
.upload-zone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  border: 2px dashed var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-muted);
}

.upload-zone:hover {
  border-color: var(--accent-primary);
  background: rgba(245, 158, 11, 0.05);
}

.upload-zone svg {
  width: 48px;
  height: 48px;
  margin-bottom: 12px;
}

.upload-zone p {
  margin: 0 0 4px;
  font-size: 1rem;
  color: var(--text-primary);
}

.upload-zone span {
  font-size: 0.875rem;
}

.uploaded-preview {
  position: relative;
  max-width: 400px;
  margin: 0 auto;
}

.uploaded-preview img {
  width: 100%;
  border-radius: 12px;
}

.remove-upload {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.7);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
}

.remove-upload svg {
  width: 16px;
  height: 16px;
}

/* Bottom Input Bar */
.input-bar {
  background: var(--bg-panel);
  border-top: 1px solid var(--border-color);
  padding: 12px 16px;
  padding-bottom: max(12px, env(safe-area-inset-bottom));
}

.options-panel {
  margin-bottom: 12px;
}

.options-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.option-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.option-group label {
  font-size: 0.6875rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.option-group select {
  padding: 8px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.8125rem;
  cursor: pointer;
  min-width: 120px;
}

.option-group select:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.options-toggle {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.options-toggle:hover,
.options-toggle.active {
  background: var(--bg-elevated);
  color: var(--accent-primary);
  border-color: var(--accent-primary);
}

.options-toggle svg {
  width: 20px;
  height: 20px;
}

.input-action {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.input-action:hover:not(:disabled) {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.input-action:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.input-action svg {
  width: 20px;
  height: 20px;
}

.mini-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.2);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.prompt-input {
  flex: 1;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 0.9375rem;
  transition: border-color 0.2s ease;
}

.prompt-input:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.prompt-input::placeholder {
  color: var(--text-muted);
}

.generate-btn {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-primary);
  border: none;
  border-radius: 12px;
  color: #000;
  cursor: pointer;
  transition: all 0.15s ease;
}

.generate-btn:hover:not(:disabled) {
  background: #fbbf24;
  transform: scale(1.05);
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.generate-btn svg {
  width: 20px;
  height: 20px;
}

.btn-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(0,0,0,0.2);
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Slide transition */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  max-height: 0;
  margin-bottom: 0;
}

.slide-enter-to,
.slide-leave-from {
  max-height: 100px;
}

/* Gallery View */
.gallery-view {
  flex: 1;
  min-height: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .results-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  
  .options-row {
    gap: 8px;
  }
  
  .option-group select {
    min-width: 100px;
    padding: 6px 10px;
    font-size: 0.75rem;
  }
  
  .input-wrapper {
    gap: 6px;
  }
  
  .options-toggle,
  .input-action {
    width: 36px;
    height: 36px;
  }
  
  .generate-btn {
    width: 44px;
    height: 44px;
  }
}

@media (max-width: 480px) {
  .results-container {
    padding: 8px;
  }
  
  .results-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 6px;
  }
  
  .result-card {
    border-radius: 8px;
  }
  
  .overlay-prompt {
    display: none;
  }
}
</style>