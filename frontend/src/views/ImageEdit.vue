<template>
  <div class="image-edit">
    <!-- Image Preview Area -->
    <div class="preview-area">
      <!-- Upload area -->
      <div v-if="!previewImage" class="upload-area-main" @click="$refs.fileInput.click()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
          <polyline points="17 8 12 3 7 8"/>
          <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        <p>{{ $t('imageEdit.clickToUpload') }}</p>
        <span>{{ $t('imageEdit.orSelectFromRecent') }}</span>
        <input 
          ref="fileInput"
          type="file" 
          accept="image/*"
          style="display: none"
          @change="handleFileSelect"
        />
      </div>
      <!-- Preview image -->
      <div v-else class="preview-image-container">
        <img :src="previewImage" class="preview-image" />
        <div class="preview-overlay">
          <button class="overlay-btn" @click="clearImage">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Prompt Area -->
    <div class="prompt-area">
      <div class="prompt-wrapper">
        <textarea
          v-model="prompt"
          :placeholder="$t('imageEdit.describeTransformation')"
          rows="3"
          class="prompt-input"
          @keydown.ctrl.enter="handleEdit"
        ></textarea>
        <div class="prompt-footer">
          <div class="prompt-actions">
            <div v-if="sourceImage" class="uploaded-info">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <path d="M21 15l-5-5L5 21"/>
              </svg>
              <span>{{ $t('imageEdit.imageLoaded') }}</span>
            </div>
          </div>
          <div class="generate-btn-wrapper">
            <button
              @click="handleEdit"
              :disabled="!sourceImage || !prompt.trim() || generating"
              class="generate-btn"
            >
              <span v-if="generating" class="btn-content">
                <span class="spinner"></span>
                <span>{{ $t('imageEdit.editing') }}</span>
              </span>
              <span v-else class="btn-content">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
                <span>{{ $t('imageEdit.editImage') }}</span>
              </span>
            </button>
            <div class="credit-badge">
              <svg class="credit-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.31-8.86c-1.77-.45-2.34-.94-2.34-1.67 0-.84.79-1.43 2.1-1.43 1.38 0 1.9.66 1.94 1.64h1.71c-.05-1.34-.87-2.57-2.49-2.97V5H10.9v1.69c-1.51.32-2.72 1.3-2.72 2.81 0 1.79 1.49 2.69 3.66 3.21 1.95.46 2.34 1.15 2.34 1.87 0 .53-.39 1.39-2.1 1.39-1.6 0-2.23-.72-2.32-1.64H8.04c.1 1.7 1.36 2.66 2.86 2.97V19h2.34v-1.67c1.52-.29 2.72-1.16 2.73-2.77-.01-2.2-1.9-2.96-3.66-3.42z"/>
              </svg>
              <span>{{ editCredits }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Edits -->
    <div v-if="recentEdits.length > 0" class="recent-section">
      <h3>{{ $t('imageEdit.recentEdits') }}</h3>
      <div class="recent-grid">
        <ImageCard
          v-for="edit in recentEdits"
          :key="edit.id"
          :generation="edit"
          :show-use-button="true"
          @fullscreen="openModal(edit)"
          @use-image="loadEdit(edit)"
        />
      </div>
    </div>

    <!-- Image Modal -->
    <ImageModal
      :visible="modalVisible"
      :generation="selectedEdit"
      @close="closeModal"
    />
  </div>
</template>

<script>
import { useI18n } from 'vue-i18n'
import ImageCard from '../components/ImageCard.vue'
import ImageModal from '../components/ImageModal.vue'
import api from '../services/api.js'

export default {
  name: 'ImageEdit',
  components: {
    ImageCard,
    ImageModal
  },
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
      sourceImage: null,
      previewImage: null,
      prompt: '',
      generating: false,
      pollingId: null,
      recentEdits: [],
      modalVisible: false,
      selectedEdit: {}
    }
  },
  computed: {
    editCredits() {
      const img2imgCredits = {
        'QwenImageEdit_Plus_NF4': { 512: 40, 768: 70, 1024: 100 },
        'Flux_2_Klein_4B_BF16': { 768: 12, 1024: 16, 1536: 25 }
      }
      
      const model = this.generationOptions?.model || 'QwenImageEdit_Plus_NF4'
      const pricing = img2imgCredits[model] || img2imgCredits['QwenImageEdit_Plus_NF4']
      
      // Default to medium size
      return pricing[768] || 40
    }
  },
  mounted() {
    this.loadRecentEdits()
  },
  beforeUnmount() {
    this.stopPolling()
  },
  methods: {
    handleFileSelect(event) {
      const file = event.target.files[0]
      if (!file) return
      if (!file.type.startsWith('image/')) {
        alert(this.t('imageEdit.pleaseSelectImage'))
        return
      }
      this.sourceImage = file
      this.previewImage = URL.createObjectURL(file)
    },
    
    clearImage() {
      this.sourceImage = null
      this.previewImage = null
    },
    
    async handleEdit() {
      if (!this.sourceImage || !this.prompt.trim() || this.generating) return
      
      this.generating = true
      try {
        const result = await api.generateImg2Img(this.sourceImage, this.prompt, {
          model: this.generationOptions.model || 'QwenImageEdit_Plus_NF4',
          steps: this.generationOptions.steps || 20,
          guidance: this.generationOptions.guidance || 3.5,
          seed: this.generationOptions.seed ?? -1
        })
        
        this.startPolling(result.id)
        
      } catch (error) {
        console.error('Edit failed:', error)
        alert(this.t('imageEdit.failedToEdit'))
        this.generating = false
      }
    },
    
    startPolling(generationId) {
      this.stopPolling()
      this.pollingId = setInterval(async () => {
        try {
          const updated = await api.getStatus(generationId)
          
          if (updated.status === 'completed') {
            this.stopPolling()
            this.generating = false
            this.previewImage = updated.remote_url
            this.sourceImage = null // Clear source so user can save result
            this.loadRecentEdits()
          } else if (updated.status === 'failed') {
            this.stopPolling()
            this.generating = false
            alert(this.t('imageEdit.failedToEdit') + ': ' + (updated.error_message || 'Unknown error'))
          }
        } catch (error) {
          console.error('Polling error:', error)
        }
      }, 5000)
      
      // Timeout after 10 minutes
      setTimeout(() => {
        if (this.pollingId) {
          this.stopPolling()
          this.generating = false
        }
      }, 10 * 60 * 1000)
    },
    
    stopPolling() {
      if (this.pollingId) {
        clearInterval(this.pollingId)
        this.pollingId = null
      }
    },
    
    async loadRecentEdits() {
      try {
        const response = await api.getGenerations(1, 8, 'img2img')
        this.recentEdits = response.items || []
      } catch (error) {
        console.error('Failed to load recent edits:', error)
      }
    },
    
    loadEdit(edit) {
      // Fetch the image and set it as source
      this.loadImageFromUrl(edit.remote_url)
      this.prompt = edit.prompt
    },
    
    async loadImageFromUrl(url) {
      try {
        const response = await fetch(url)
        const blob = await response.blob()
        const file = new File([blob], 'image.png', { type: blob.type })
        this.sourceImage = file
        this.previewImage = url
      } catch (error) {
        console.error('Failed to load image:', error)
      }
    },
    
    openModal(edit) {
      this.selectedEdit = edit
      this.modalVisible = true
    },
    
    closeModal() {
      this.modalVisible = false
      this.selectedEdit = {}
    }
  }
}
</script>

<style scoped>
.image-edit {
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
  align-items: center;
}

.uploaded-info {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--accent-secondary);
  font-size: 0.8125rem;
}

.uploaded-info svg {
  width: 16px;
  height: 16px;
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

@media (max-width: 900px) {
  .recent-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
