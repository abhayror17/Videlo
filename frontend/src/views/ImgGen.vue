<template>
  <div class="img-gen">
    <div class="gen-container">
      <!-- Preview Area with Drag & Drop -->
      <div 
        class="preview-area"
        :class="{ 'drag-over': isDragging }"
        @dragover.prevent="handleDragOver"
        @dragleave.prevent="handleDragLeave"
        @drop.prevent="handleDrop"
      >
        <!-- Generated Images -->
        <div v-if="generatedImages.length > 0" class="generated-results">
          <div class="results-grid">
            <div 
              v-for="(img, idx) in generatedImages" 
              :key="idx" 
              class="result-item"
              @click="openImageModal(img)"
            >
              <img 
                :src="img" 
                alt="Generated image" 
                referrerpolicy="no-referrer"
                @error="handleImageError($event, img)"
                loading="lazy"
              />
              <div class="result-overlay">
                <button class="overlay-btn" @click.stop="downloadImage(img)" title="Download">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
          <div v-if="generating" class="generating-overlay">
            <div class="spinner-large"></div>
            <p>Generating...</p>
          </div>
        </div>
        
        <!-- Loading State -->
        <div v-else-if="generating" class="loading-state">
          <div class="spinner-large"></div>
          <p>Creating your image...</p>
          <span>This may take up to 2 minutes</span>
        </div>
        
        <!-- Reference Images Preview (multiple) -->
        <div v-else-if="referenceImages.length > 0" class="reference-preview-multiple">
          <div class="ref-images-grid">
            <div 
              v-for="(img, idx) in referenceImages" 
              :key="idx" 
              class="ref-image-item"
            >
              <img :src="img" alt="Reference" referrerpolicy="no-referrer" />
              <button class="remove-ref-btn" @click="removeReferenceImage(idx)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
            <!-- Add more button -->
            <div 
              v-if="referenceImages.length < 9" 
              class="add-ref-btn"
              @click="$refs.refInput.click()"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              <span>Add</span>
            </div>
          </div>
          <span class="reference-label">{{ referenceImages.length }} reference image(s) - Image-to-Image mode</span>
        </div>
        
        <!-- Drop Zone / Empty State -->
        <div v-else class="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <path d="M21 15l-5-5L5 21"/>
          </svg>
          <p>Your creation will appear here</p>
          <span>Drag & drop up to 9 reference images or enter a prompt</span>
        </div>
        
        <!-- Drag Overlay -->
        <div v-if="isDragging && referenceImages.length < 9 && !generatedImages.length" class="drag-overlay">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          <p>Drop image{{ referenceImages.length > 0 ? 's' : '' }} to use as reference</p>
        </div>
      </div>

      <!-- Prompt Area -->
      <div class="prompt-area">
        <div class="prompt-wrapper">
          <textarea
            v-model="prompt"
            :placeholder="$t('imgGen.describeImage') || 'Describe the image you want to create...'"
            rows="3"
            class="prompt-input"
            @keydown.ctrl.enter="handleGenerate"
          ></textarea>
          
          <div class="prompt-footer">
            <div class="prompt-actions">
              <!-- Reference Image Upload -->
              <button 
                class="prompt-action-btn"
                :class="{ active: referenceImages.length > 0 }"
                @click="$refs.refInput.click()"
                :title="$t('imgGen.addReference') || 'Add reference image'"
                :disabled="referenceImages.length >= maxImages"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="3" width="18" height="18" rx="2"/>
                  <circle cx="8.5" cy="8.5" r="1.5"/>
                  <path d="M21 15l-5-5L5 21"/>
                </svg>
                <span v-if="referenceImages.length > 0" class="ref-count">{{ referenceImages.length }}</span>
              </button>
              <input 
                ref="refInput"
                type="file" 
                accept="image/*"
                multiple
                style="display: none"
                @change="handleRefUpload"
              />
              
              <!-- Clear -->
              <button 
                v-if="prompt || referenceImages.length > 0"
                class="prompt-action-btn"
                @click="clearAll"
                title="Clear"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
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
                <span>{{ referenceImages.length > 0 ? `Generate (Img2Img)` : 'Generate' }}</span>
              </span>
            </button>
          </div>
        </div>
      </div>

      <!-- Options Bar -->
      <div class="options-bar">
        <!-- Model Selection -->
        <div class="option-group">
          <label>{{ $t('imgGen.model') || 'Model' }}</label>
          <div class="model-options">
            <button 
              :class="['model-btn', { active: model === 'nano-banana-2' }]"
              @click="model = 'nano-banana-2'"
            >
              <span class="model-name">Nano Banana 2</span>
              <span class="model-desc">Fast</span>
            </button>
            <button 
              :class="['model-btn', { active: model === 'nano-banana-pro' }]"
              @click="model = 'nano-banana-pro'"
            >
              <span class="model-name">Nano Banana Pro</span>
              <span class="model-desc">Quality</span>
            </button>
          </div>
        </div>
        
        <!-- Aspect Ratio -->
        <div class="option-group">
          <label>{{ $t('imgGen.aspectRatio') || 'Aspect Ratio' }}</label>
          <div class="aspect-options">
            <button 
              v-for="ar in aspectRatios" 
              :key="ar.value"
              :class="['aspect-btn', { active: aspectRatio === ar.value }]"
              @click="aspectRatio = ar.value"
              :title="ar.label"
            >
              <div class="aspect-preview" :style="{ aspectRatio: ar.preview }"></div>
              <span>{{ ar.label }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Image Modal -->
    <Teleport to="body">
      <div v-if="modalImage" class="modal-backdrop" @click="modalImage = null">
        <div class="image-modal" @click.stop>
          <button class="modal-close" @click="modalImage = null">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
          <img :src="modalImage" alt="Generated image" referrerpolicy="no-referrer" />
          <div class="modal-actions">
            <button class="action-btn" @click="downloadImage(modalImage)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              Download
            </button>
            <button class="action-btn" @click="useAsReference(modalImage)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <path d="M21 15l-5-5L5 21"/>
              </svg>
              Use as Reference
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import api from '../services/api.js'

export default {
  name: 'ImgGen',
  setup() {
    const { t } = useI18n()
    const route = useRoute()
    
    return { t, route }
  },
  data() {
    return {
      prompt: '',
      model: 'nano-banana-2',
      aspectRatio: '1:1',
      referenceImages: [],  // Changed to array for multiple images
      generating: false,
      generatedImages: [],
      modalImage: null,
      isDragging: false,
      maxImages: 9,
      maxSizeMB: 5,
      aspectRatios: [
        { value: '1:1', label: '1:1', preview: '1/1' },
        { value: '16:9', label: '16:9', preview: '16/9' },
        { value: '9:16', label: '9:16', preview: '9/16' },
        { value: '4:3', label: '4:3', preview: '4/3' },
        { value: '3:4', label: '3:4', preview: '3/4' }
      ]
    }
  },
  mounted() {
    // Set prompt from query params
    if (this.$route.query.prompt) {
      this.prompt = this.$route.query.prompt
    }
    // Set reference image from query params
    if (this.$route.query.ref) {
      this.referenceImages.push(this.$route.query.ref)
    }
  },
  methods: {
    // Drag and drop handlers
    handleDragOver(e) {
      this.isDragging = true
    },
    
    handleDragLeave(e) {
      this.isDragging = false
    },
    
    handleDrop(e) {
      this.isDragging = false
      const files = e.dataTransfer.files
      if (files.length > 0) {
        this.processFiles(files)
      }
    },
    
    // Process multiple files (from upload or drag/drop)
    processFiles(files) {
      const remainingSlots = this.maxImages - this.referenceImages.length
      if (remainingSlots <= 0) {
        alert(`Maximum ${this.maxImages} reference images allowed`)
        return
      }
      
      const filesToProcess = Array.from(files).slice(0, remainingSlots)
      
      filesToProcess.forEach(file => {
        if (!file.type.startsWith('image/')) return
        
        // Check file size
        if (file.size > this.maxSizeMB * 1024 * 1024) {
          alert(`Image "${file.name}" exceeds ${this.maxSizeMB}MB limit`)
          return
        }
        
        const reader = new FileReader()
        reader.onload = (e) => {
          this.referenceImages.push(e.target.result)
        }
        reader.readAsDataURL(file)
      })
    },
    
    handleRefUpload(event) {
      const files = event.target.files
      if (!files || files.length === 0) return
      this.processFiles(files)
      // Reset input
      event.target.value = ''
    },
    
    removeReferenceImage(index) {
      this.referenceImages.splice(index, 1)
    },
    
    clearAllReferenceImages() {
      this.referenceImages = []
    },
    
    clearAll() {
      this.prompt = ''
      this.referenceImages = []
      this.generatedImages = []
    },
    
    async handleGenerate() {
      if (!this.prompt.trim() || this.generating) return
      
      this.generating = true
      this.generatedImages = []
      
      try {
        const result = await api.generateNanoBanana({
          prompt: this.prompt,
          model: this.model,
          aspect_ratio: this.aspectRatio,
          reference_images: this.referenceImages.length > 0 ? this.referenceImages : null
        })
        
        console.log('NanoBanana result:', result)
        
        if (result.image_urls && result.image_urls.length > 0) {
          this.generatedImages = result.image_urls
        } else if (result.error) {
          alert(result.error)
        } else {
          alert('Generation completed but no images were returned. Please try again.')
        }
      } catch (error) {
        console.error('Generation failed:', error)
        alert('Failed to generate image: ' + (error.response?.data?.detail || error.message))
      } finally {
        this.generating = false
      }
    },
    
    openImageModal(img) {
      this.modalImage = img
    },
    
    handleImageError(event, img) {
      console.error('Image failed to load:', img)
      // Try reloading with a small delay (sometimes URLs need time to be accessible)
      const imgEl = event.target
      setTimeout(() => {
        imgEl.src = img + '?t=' + Date.now()
      }, 1000)
    },
    
    async downloadImage(url) {
      try {
        const response = await fetch(url)
        const blob = await response.blob()
        const downloadUrl = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = downloadUrl
        a.download = `nanobanana-${Date.now()}.png`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(downloadUrl)
      } catch (error) {
        console.error('Download failed:', error)
        window.open(url, '_blank')
      }
    },
    
    useAsReference(url) {
      if (this.referenceImages.length < this.maxImages) {
        this.referenceImages.push(url)
      } else {
        alert(`Maximum ${this.maxImages} reference images allowed`)
      }
      this.modalImage = null
    }
  }
}
</script>

<style scoped>
.img-gen {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.gen-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
}

/* Preview Area */
.preview-area {
  flex: 1;
  min-height: 300px;
  background: var(--bg-panel);
  border: 2px dashed var(--border-color);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
  transition: all 0.3s ease;
}

.preview-area.drag-over {
  border-color: var(--accent-primary);
  background: rgba(245, 158, 11, 0.05);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--text-muted);
  text-align: center;
  padding: 40px;
}

.empty-state svg {
  width: 64px;
  height: 64px;
  opacity: 0.4;
}

.empty-state p {
  font-size: 1rem;
  color: var(--text-secondary);
}

.empty-state span {
  font-size: 0.875rem;
}

/* Drag Overlay */
.drag-overlay {
  position: absolute;
  inset: 0;
  background: rgba(245, 158, 11, 0.1);
  border: 2px solid var(--accent-primary);
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: var(--accent-primary);
  z-index: 10;
}

.drag-overlay svg {
  width: 48px;
  height: 48px;
}

.drag-overlay p {
  font-size: 1rem;
  font-weight: 600;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--text-muted);
}

.loading-state p {
  font-size: 1rem;
  color: var(--text-primary);
}

.loading-state span {
  font-size: 0.875rem;
}

.spinner-large {
  width: 48px;
  height: 48px;
  border: 4px solid var(--border-color);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Generated Results */
.generated-results {
  width: 100%;
  height: 100%;
  position: relative;
}

.results-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 16px;
  padding: 20px;
  width: 100%;
  height: 100%;
  align-content: center;
}

.result-item {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  background: var(--bg-elevated);
  max-width: 100%;
  max-height: 100%;
}

.result-item img {
  max-width: 100%;
  max-height: 60vh;
  object-fit: contain;
  display: block;
}

.result-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.result-item:hover .result-overlay {
  opacity: 1;
}

.overlay-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.overlay-btn:hover {
  background: var(--accent-primary);
  color: #000;
}

.overlay-btn svg {
  width: 18px;
  height: 18px;
}

.generating-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: white;
}

/* Reference Preview Multiple */
.reference-preview-multiple {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.ref-images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 12px;
  max-width: 600px;
  width: 100%;
}

.ref-image-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-elevated);
}

.ref-image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-ref-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.7);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
}

.ref-image-item:hover .remove-ref-btn {
  opacity: 1;
}

.remove-ref-btn svg {
  width: 14px;
  height: 14px;
}

.add-ref-btn {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px dashed var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-muted);
}

.add-ref-btn:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.add-ref-btn svg {
  width: 24px;
  height: 24px;
}

.add-ref-btn span {
  font-size: 0.7rem;
}

.reference-label {
  margin-top: 16px;
  padding: 6px 16px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 20px;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

/* Prompt Area */
.prompt-area {
  display: flex;
  gap: 16px;
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
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.prompt-action-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.prompt-action-btn.active {
  background: rgba(245, 158, 11, 0.2);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.prompt-action-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.ref-count {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-primary);
  border-radius: 9px;
  font-size: 0.65rem;
  font-weight: 700;
  color: #000;
  padding: 0 5px;
}

.prompt-action-btn svg {
  width: 18px;
  height: 18px;
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
  gap: 8px;
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

/* Options Bar */
.options-bar {
  display: flex;
  gap: 24px;
  padding: 20px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 16px;
}

.option-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-group label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.model-options {
  display: flex;
  gap: 8px;
}

.model-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 20px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 130px;
}

.model-btn:hover {
  border-color: var(--border-hover);
}

.model-btn.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #000;
}

.model-name {
  font-size: 0.875rem;
  font-weight: 600;
}

.model-desc {
  font-size: 0.7rem;
  opacity: 0.7;
}

.model-btn.active .model-desc {
  opacity: 0.8;
}

.aspect-options {
  display: flex;
  gap: 8px;
}

.aspect-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.aspect-btn:hover {
  border-color: var(--border-hover);
}

.aspect-btn.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #000;
}

.aspect-preview {
  width: 24px;
  height: 24px;
  background: currentColor;
  opacity: 0.5;
  border-radius: 2px;
}

.aspect-btn.active .aspect-preview {
  opacity: 0.3;
  background: #000;
}

.aspect-btn span {
  font-size: 0.7rem;
  font-weight: 600;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 40px;
}

.image-modal {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.modal-close {
  position: absolute;
  top: -40px;
  right: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
}

.modal-close svg {
  width: 18px;
  height: 18px;
}

.image-modal img {
  max-width: 100%;
  max-height: calc(90vh - 80px);
  border-radius: 12px;
  object-fit: contain;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #000;
}

.action-btn svg {
  width: 18px;
  height: 18px;
}

/* Responsive */
@media (max-width: 768px) {
  .options-bar {
    flex-direction: column;
    gap: 16px;
  }
  
  .model-options, .aspect-options {
    flex-wrap: wrap;
  }
  
  .model-btn {
    min-width: 100px;
  }
}
</style>