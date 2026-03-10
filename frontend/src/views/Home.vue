<template>
  <div class="home">
    <!-- Generation View -->
    <div v-if="currentView !== 'gallery'" class="generation-view">
      <!-- Image Preview Area -->
      <div class="preview-area">
        <!-- Upload area for img2video -->
        <div v-if="currentView === 'img2video' && !previewImage && !uploadedImagePreview" class="upload-area-main" @click="$refs.mainFileInput.click()">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          <p>Click to upload an image</p>
          <span>or select from Recent below</span>
          <input 
            ref="mainFileInput"
            type="file" 
            accept="image/*"
            style="display: none"
            @change="handleMainFileUpload"
          />
        </div>
        <!-- Preview image -->
        <div v-else-if="previewImage || uploadedImagePreview" class="preview-image-container">
          <img :src="previewImage || uploadedImagePreview" class="preview-image" />
          <div class="preview-overlay">
            <button class="overlay-btn" @click="clearUploadedImage">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>
        <!-- Default placeholder for other views -->
        <div v-else class="preview-placeholder">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <path d="M21 15l-5-5L5 21"/>
          </svg>
          <p>Your creation will appear here</p>
        </div>
      </div>

      <!-- Prompt Area -->
      <div class="prompt-area">
        <div class="prompt-wrapper">
          <textarea
            v-model="prompt"
            :placeholder="placeholderText"
            rows="3"
            class="prompt-input"
            @keydown.ctrl.enter="handleGenerate"
          ></textarea>
          <div class="prompt-footer">
            <div class="prompt-actions">
              <button 
                class="prompt-action-btn enhance"
                @click="enhancePrompt"
                :disabled="!prompt.trim() || enhancing"
                title="Enhance prompt with AI"
              >
                <svg v-if="!enhancing" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/>
                  <path d="M20 3v4"/>
                  <path d="M22 5h-4"/>
                  <path d="M4 17v2"/>
                  <path d="M5 18H3"/>
                </svg>
                <span v-else class="spinner-small"></span>
              </button>
              <button 
                class="prompt-action-btn random"
                @click="getRandomPrompt"
                :disabled="gettingRandom"
                title="Get random prompt"
              >
                <div v-if="gettingRandom" class="spinner-small"></div>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect width="12" height="12" x="2" y="10" rx="2" ry="2"/>
                  <path d="m17.92 14 3.5-3.5a2.24 2.24 0 0 0 0-3l-5-4.92a2.24 2.24 0 0 0-3 0L10 6"/>
                  <path d="M6 18h.01"/>
                  <path d="M10 14h.01"/>
                  <path d="M15 6h.01"/>
                  <path d="M18 9h.01"/>
                </svg>
              </button>
            </div>
            <button
              @click="handleGenerate"
              :disabled="!prompt.trim() || generating"
              class="generate-btn"
            >
              <span v-if="generating" class="btn-content">
                <span class="spinner"></span>
                <span>Generating...</span>
              </span>
              <span v-else class="btn-content">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                </svg>
                <span>Generate</span>
              </span>
            </button>
          </div>
        </div>
      </div>

      <!-- Recent Generations Mini Gallery -->
      <div v-if="recentGenerations.length > 0" class="recent-section">
        <h3>Recent</h3>
        <div class="recent-grid">
          <ImageCard
            v-for="gen in recentGenerations.slice(0, 4)"
            :key="gen.id"
            :generation="gen"
            @fullscreen="currentView === 'img2video' ? selectImageForVideo(gen) : openModal(gen)"
            @create-video="openVideoModal(gen)"
          />
        </div>
      </div>
    </div>

    <!-- Gallery View -->
    <div v-else class="gallery-view">
      <Gallery 
        ref="gallery"
        @select="openModal"
        @create-video="openVideoModal"
      />
    </div>

    <!-- Image Modal -->
    <ImageModal
      :visible="modalVisible"
      :generation="selectedGeneration"
      @close="closeModal"
    />

    <!-- Video Creation Modal -->
    <div v-if="videoModalVisible" class="modal-overlay" @click.self="closeVideoModal">
      <div class="video-modal">
        <button class="close-btn" @click="closeVideoModal">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
        <h3>Create Video from Image</h3>
        
        <div class="preview-section">
          <img 
            v-if="selectedImage?.remote_url || selectedImage?.thumbnail_url"
            :src="selectedImage.remote_url || selectedImage.thumbnail_url"
            class="preview-image"
          />
          <div v-else-if="uploadedImagePreview" class="upload-preview">
            <img :src="uploadedImagePreview" class="preview-image" />
          </div>
          <div v-else class="upload-area" @click="$refs.fileInput.click()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            <p>Click to upload an image</p>
            <span>or select one from the gallery</span>
          </div>
          <input 
            ref="fileInput"
            type="file" 
            accept="image/*"
            style="display: none"
            @change="handleFileUpload"
          />
        </div>
        
        <textarea
          v-model="videoPrompt"
          placeholder="Describe the video animation..."
          rows="3"
          class="modal-textarea"
        ></textarea>
        
        <div class="modal-options">
          <div class="modal-option">
            <label>Model</label>
            <select v-model="videoModel">
              <option value="Ltx2_19B_Dist_FP8">LTX-2 19B</option>
              <option value="Ltxv_13B_0_9_8_Distilled_FP8">LTX-Video 13B</option>
            </select>
          </div>
          <div class="modal-option">
            <label>Duration</label>
            <select v-model.number="videoFrames">
              <option :value="24">1 second</option>
              <option :value="48">2 seconds</option>
              <option :value="72">3 seconds</option>
              <option :value="96">4 seconds</option>
            </select>
          </div>
        </div>
        
        <button
          @click="createVideo"
          :disabled="!videoPrompt.trim() || creatingVideo"
          class="modal-generate-btn"
        >
          <span v-if="creatingVideo" class="btn-content">
            <span class="spinner"></span>
            <span>Creating...</span>
          </span>
          <span v-else>Generate Video</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import Gallery from '../components/Gallery.vue'
import ImageCard from '../components/ImageCard.vue'
import ImageModal from '../components/ImageModal.vue'
import api from '../services/api.js'

export default {
  name: 'Home',
  components: {
    Gallery,
    ImageCard,
    ImageModal
  },
  props: {
    currentView: {
      type: String,
      default: 'text2img'
    },
    generationOptions: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      prompt: '',
      modalVisible: false,
      selectedGeneration: {},
      previewImage: null,
      generating: false,
      enhancing: false,
      gettingRandom: false,
      pollingIds: {},
      recentGenerations: [],
      recentPollingInterval: null,
      // Video modal state
      videoModalVisible: false,
      selectedImage: null,
      uploadedImageFile: null,
      uploadedImagePreview: null,
      videoPrompt: '',
      videoModel: 'Ltx2_19B_Dist_FP8',
      videoFrames: 96,
      videoFps: 24,
      creatingVideo: false
    }
  },
  computed: {
    placeholderText() {
      if (this.currentView === 'text2img') {
        return 'Describe the image you want to create...'
      } else if (this.currentView === 'txt2video') {
        return 'Describe the video you want to generate...'
      }
      return 'Describe the transformation...'
    }
  },
  watch: {
    currentView() {
      this.loadRecentGenerations()
    }
  },
  mounted() {
    this.loadRecentGenerations()
    this.startRecentPolling()
  },
  beforeUnmount() {
    this.stopRecentPolling()
  },
  methods: {
    async loadRecentGenerations() {
      try {
        const response = await api.getGenerations(1, 8)
        this.recentGenerations = response.items || []
      } catch (error) {
        console.error('Failed to load recent generations:', error)
      }
    },
    
    async refreshAll() {
      // Single method to refresh both recent and gallery
      await this.loadRecentGenerations()
      if (this.$refs.gallery) {
        this.$refs.gallery.refresh()
      }
    },
    
    startRecentPolling() {
      this.recentPollingInterval = setInterval(() => {
        this.pollRecentInProgress()
      }, 5000) // Poll every 5 seconds instead of 2
    },
    
    stopRecentPolling() {
      if (this.recentPollingInterval) {
        clearInterval(this.recentPollingInterval)
        this.recentPollingInterval = null
      }
    },
    
    async pollRecentInProgress() {
      const inProgress = this.recentGenerations.filter(g => g.status === 'processing')
      
      if (inProgress.length === 0) return
      
      for (const gen of inProgress) {
        try {
          const updated = await api.getStatus(gen.id)
          
          const index = this.recentGenerations.findIndex(g => g.id === gen.id)
          if (index !== -1) {
            this.recentGenerations[index] = { ...this.recentGenerations[index], ...updated }
          }
          
          if (updated.status === 'completed' || updated.status === 'failed') {
            this.refreshAll()
          }
        } catch (error) {
          console.error('Polling error:', error)
        }
      }
    },
    
    async handleGenerate() {
      if (!this.prompt.trim() || this.generating) return
      
      // For img2video, require an image
      if (this.currentView === 'img2video' && !this.uploadedImageFile && !this.selectedImage) {
        alert('Please upload an image or select one from Recent')
        return
      }
      
      this.generating = true
      try {
        let result
        
        const options = {
          ...this.generationOptions
        }
        
        if (this.currentView === 'text2img') {
          result = await api.generateText2Img(this.prompt, options)
        } else if (this.currentView === 'txt2video') {
          options.frames = this.generationOptions.frames || 48
          options.fps = this.generationOptions.fps || 24
          result = await api.generateTxt2Video(this.prompt, options)
        } else if (this.currentView === 'img2video') {
          options.frames = this.generationOptions.frames || 48
          options.fps = this.generationOptions.fps || 24
          options.width = this.generationOptions.width || 512
          options.height = this.generationOptions.height || 512
          
          if (this.uploadedImageFile) {
            result = await api.generateImg2VideoWithFile(this.uploadedImageFile, this.prompt, options)
          } else if (this.selectedImage) {
            result = await api.generateImg2Video(this.selectedImage.id, this.prompt, options)
          }
        }
        
        if (result) {
          // Clear uploaded image after successful generation
          if (this.currentView === 'img2video') {
            this.clearUploadedImage()
          }
          this.startPolling(result.id)
          this.refreshAll()
        }
      } catch (error) {
        console.error('Generation failed:', error)
        alert('Failed to generate. Please try again.')
      } finally {
        this.generating = false
      }
    },

    async enhancePrompt() {
      if (!this.prompt.trim() || this.enhancing) return
      
      this.enhancing = true
      try {
        const result = await api.enhancePrompt(this.prompt)
        if (result.enhanced_prompt) {
          this.prompt = result.enhanced_prompt
        }
      } catch (error) {
        console.error('Prompt enhancement failed:', error)
      } finally {
        this.enhancing = false
      }
    },

    async getRandomPrompt() {
      if (this.gettingRandom) return
      
      this.gettingRandom = true
      try {
        const result = await api.getRandomPrompt()
        if (result.prompt) {
          this.prompt = result.prompt
        }
      } catch (error) {
        console.error('Random prompt failed:', error)
      } finally {
        this.gettingRandom = false
      }
    },
    
    startPolling(generationId) {
      const pollId = setInterval(async () => {
        try {
          const updated = await api.getStatus(generationId)
          
          if (updated.status === 'completed') {
            this.stopPolling(generationId)
            this.refreshAll()
            if (updated.remote_url) {
              this.previewImage = updated.remote_url
            }
          } else if (updated.status === 'failed') {
            this.stopPolling(generationId)
          }
        } catch (error) {
          console.error('Polling error:', error)
          this.stopPolling(generationId)
        }
      }, 5000) // Poll every 5 seconds instead of 3
      
      this.pollingIds[generationId] = pollId
      setTimeout(() => this.stopPolling(generationId), 10 * 60 * 1000)
    },
    
    stopPolling(generationId) {
      if (this.pollingIds[generationId]) {
        clearInterval(this.pollingIds[generationId])
        delete this.pollingIds[generationId]
      }
    },
    
    openModal(generation) {
      this.selectedGeneration = generation
      this.modalVisible = true
    },
    
    closeModal() {
      this.modalVisible = false
      this.selectedGeneration = {}
    },
    
    // Video creation methods
    openVideoModal(imageGeneration) {
      this.selectedImage = imageGeneration
      this.uploadedImageFile = null
      this.uploadedImagePreview = null
      this.videoPrompt = ''
      this.videoModalVisible = true
    },

    handleFileUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      if (!file.type.startsWith('image/')) {
        alert('Please select an image file')
        return
      }
      this.uploadedImageFile = file
      this.uploadedImagePreview = URL.createObjectURL(file)
    },

    handleMainFileUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      if (!file.type.startsWith('image/')) {
        alert('Please select an image file')
        return
      }
      this.uploadedImageFile = file
      this.uploadedImagePreview = URL.createObjectURL(file)
    },

    clearUploadedImage() {
      this.uploadedImageFile = null
      this.uploadedImagePreview = null
      this.selectedImage = null
    },

    selectImageForVideo(gen) {
      this.selectedImage = gen
      this.uploadedImageFile = null
      this.uploadedImagePreview = gen.remote_url || gen.thumbnail_url
    },

    closeVideoModal() {
      this.videoModalVisible = false
      this.selectedImage = null
      this.uploadedImageFile = null
      this.uploadedImagePreview = null
      this.videoPrompt = ''
      this.creatingVideo = false
    },
    
    async createVideo() {
      if (!this.videoPrompt.trim() || this.creatingVideo) return
      if (!this.selectedImage && !this.uploadedImageFile) {
        alert('Please select an image')
        return
      }

      this.creatingVideo = true
      try {
        let result

        if (this.uploadedImageFile) {
          result = await api.generateImg2VideoWithFile(
            this.uploadedImageFile,
            this.videoPrompt,
            {
              model: this.videoModel,
              frames: this.videoFrames,
              fps: this.videoFps,
              width: 512,
              height: 512
            }
          )
        } else {
          result = await api.generateImg2Video(
            this.selectedImage.id,
            this.videoPrompt,
            {
              model: this.videoModel,
              frames: this.videoFrames,
              fps: this.videoFps,
              width: 512,
              height: 512
            }
          )
        }

        this.closeVideoModal()
        this.startPolling(result.id)
        this.refreshAll()
      } catch (error) {
        console.error('Video generation failed:', error)
        alert('Failed to generate video.')
      } finally {
        this.creatingVideo = false
      }
    }
  }
}
</script>

<style scoped>
.home {
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

.preview-image-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.preview-overlay {
  position: absolute;
  top: 12px;
  right: 12px;
}

.overlay-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.6);
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
}

.overlay-btn svg {
  width: 16px;
  height: 16px;
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
  gap: 8px;
}

.prompt-action-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.prompt-action-btn svg {
  width: 20px;
  height: 20px;
}

.prompt-action-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.prompt-action-btn.enhance {
  background: linear-gradient(135deg, #273634, #1c413b);
  border: 1px solid #3b5d56;
  color: #9ca3af;
}

.prompt-action-btn.enhance:hover:not(:disabled) {
  color: white;
  filter: brightness(1.1);
}

.prompt-action-btn.random {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
}

.prompt-action-btn.random:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
}

.prompt-action-btn.random:disabled {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.3);
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

.spinner-small {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
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

/* Gallery View */
.gallery-view {
  height: 100%;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 24px;
}

.video-modal {
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  max-width: 480px;
  width: 100%;
  padding: 32px;
  position: relative;
}

.close-btn {
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
}

.close-btn svg {
  width: 16px;
  height: 16px;
}

.video-modal h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 20px;
}

.preview-section {
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 16px;
  min-height: 200px;
}

.preview-section img {
  width: 100%;
  height: auto;
  max-height: 240px;
  object-fit: contain;
}

.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  cursor: pointer;
  color: var(--text-muted);
}

.upload-area-main {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  min-height: 300px;
  cursor: pointer;
  color: var(--text-muted);
  border: 2px dashed var(--border-color);
  border-radius: 12px;
  transition: all 0.2s ease;
}

.upload-area-main:hover {
  border-color: var(--accent-primary);
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.02);
}

.upload-area-main svg {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.upload-area-main p {
  font-size: 1rem;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.upload-area-main span {
  font-size: 0.8125rem;
}

.upload-area svg {
  width: 40px;
  height: 40px;
  margin-bottom: 12px;
}

.upload-area p {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.upload-area span {
  font-size: 0.75rem;
  margin-top: 4px;
}

.modal-textarea {
  width: 100%;
  padding: 14px 16px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 0.875rem;
  resize: none;
  margin-bottom: 16px;
  font-family: inherit;
}

.modal-textarea:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.modal-options {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.modal-option {
  flex: 1;
}

.modal-option label {
  display: block;
  font-size: 0.7rem;
  color: var(--text-muted);
  margin-bottom: 6px;
  text-transform: uppercase;
}

.modal-option select {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.8125rem;
}

.modal-generate-btn {
  width: 100%;
  padding: 14px;
  background: var(--accent-primary);
  border: none;
  border-radius: 10px;
  color: #000;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
}

.modal-generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>