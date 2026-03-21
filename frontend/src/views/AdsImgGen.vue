<template>
  <div class="ads-img-gen">
    <!-- Step Indicator -->
    <div class="step-indicator">
      <div 
        v-for="step in 4" 
        :key="step" 
        :class="['step', { active: currentStep === step, completed: currentStep > step }]"
        @click="currentStep > step && goToStep(step)"
      >
        <div class="step-number">{{ step }}</div>
        <div class="step-label">{{ $t(`adsImgGen.steps[${step - 1}]`) }}</div>
      </div>
    </div>

    <div class="wizard-container">
      <!-- Step 1: Ad Type Selection -->
      <div v-if="currentStep === 1" class="step-content step-1">
        <h2>{{ $t('adsImgGen.selectAdType') }}</h2>
        <p class="step-desc">{{ $t('adsImgGen.selectAdTypeDesc') }}</p>
        
        <div class="ad-types-grid">
          <div 
            v-for="adType in adTypes" 
            :key="adType.id"
            :class="['ad-type-card', { selected: selectedAdType === adType.id }]"
            @click="selectAdType(adType.id)"
          >
            <div class="ad-type-icon">
              <component :is="getIcon(adType.icon)" />
            </div>
            <h3>{{ $t(`adsImgGen.adTypes.${adType.id}`) }}</h3>
            <p>{{ $t(`adsImgGen.adTypesDesc.${adType.id}`) }}</p>
          </div>
        </div>
      </div>

      <!-- Step 2: Product/Brand Info -->
      <div v-if="currentStep === 2" class="step-content step-2">
        <h2>{{ $t('adsImgGen.productInfo') }}</h2>
        <p class="step-desc">{{ $t('adsImgGen.productInfoDesc') }}</p>
        
        <div class="form-grid">
          <!-- Left: Form Fields -->
          <div class="form-fields">
            <!-- Product Name -->
            <div class="form-group">
              <label>{{ $t('adsImgGen.productName') }} *</label>
              <input 
                v-model="formData.productName" 
                type="text" 
                :placeholder="$t('adsImgGen.productNamePlaceholder')"
                class="form-input"
              />
            </div>
            
            <!-- Dynamic fields based on ad type -->
            <template v-if="selectedAdType === 'product'">
              <div class="form-group">
                <label>{{ $t('adsImgGen.description') }}</label>
                <textarea 
                  v-model="formData.description" 
                  :placeholder="$t('adsImgGen.descriptionPlaceholder')"
                  class="form-textarea"
                  rows="2"
                ></textarea>
              </div>
            </template>
            
            <template v-if="selectedAdType === 'social'">
              <div class="form-group">
                <label>{{ $t('adsImgGen.headline') }}</label>
                <input 
                  v-model="formData.headline" 
                  type="text" 
                  :placeholder="$t('adsImgGen.headlinePlaceholder')"
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label>{{ $t('adsImgGen.ctaText') }}</label>
                <input 
                  v-model="formData.ctaText" 
                  type="text" 
                  :placeholder="$t('adsImgGen.ctaPlaceholder')"
                  class="form-input"
                />
              </div>
            </template>
            
            <template v-if="selectedAdType === 'lifestyle'">
              <div class="form-group">
                <label>{{ $t('adsImgGen.subject') }}</label>
                <input 
                  v-model="formData.subject" 
                  type="text" 
                  :placeholder="$t('adsImgGen.subjectPlaceholder')"
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label>{{ $t('adsImgGen.action') }}</label>
                <input 
                  v-model="formData.action" 
                  type="text" 
                  :placeholder="$t('adsImgGen.actionPlaceholder')"
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label>{{ $t('adsImgGen.setting') }}</label>
                <input 
                  v-model="formData.setting" 
                  type="text" 
                  :placeholder="$t('adsImgGen.settingPlaceholder')"
                  class="form-input"
                />
              </div>
            </template>
            
            <template v-if="selectedAdType === 'food'">
              <div class="form-group">
                <label>{{ $t('adsImgGen.foodItem') }} *</label>
                <input 
                  v-model="formData.foodItem" 
                  type="text" 
                  :placeholder="$t('adsImgGen.foodItemPlaceholder')"
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label>{{ $t('adsImgGen.presentation') }}</label>
                <input 
                  v-model="formData.presentation" 
                  type="text" 
                  :placeholder="$t('adsImgGen.presentationPlaceholder')"
                  class="form-input"
                />
              </div>
            </template>
            
            <template v-if="selectedAdType === 'corporate'">
              <div class="form-group">
                <label>{{ $t('adsImgGen.subject') }}</label>
                <input 
                  v-model="formData.subject" 
                  type="text" 
                  :placeholder="$t('adsImgGen.corpSubjectPlaceholder')"
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label>{{ $t('adsImgGen.setting') }}</label>
                <input 
                  v-model="formData.setting" 
                  type="text" 
                  :placeholder="$t('adsImgGen.corpSettingPlaceholder')"
                  class="form-input"
                />
              </div>
            </template>
            
            <template v-if="selectedAdType === 'marketing'">
              <div class="form-group">
                <label>{{ $t('adsImgGen.contentType') }}</label>
                <select v-model="formData.contentType" class="form-select">
                  <option value="Promotional content">Promotional content</option>
                  <option value="Product showcase">Product showcase</option>
                  <option value="Flat-lay composition">Flat-lay composition</option>
                  <option value="Social media post">Social media post</option>
                </select>
              </div>
              <div class="form-group">
                <label>{{ $t('adsImgGen.headline') }}</label>
                <input 
                  v-model="formData.headline" 
                  type="text" 
                  :placeholder="$t('adsImgGen.headlinePlaceholder')"
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label>{{ $t('adsImgGen.ctaText') }}</label>
                <input 
                  v-model="formData.ctaText" 
                  type="text" 
                  :placeholder="$t('adsImgGen.ctaPlaceholder')"
                  class="form-input"
                />
              </div>
            </template>
          </div>
          
          <!-- Right: Image Upload -->
          <div class="image-upload-section">
            <label>{{ $t('adsImgGen.referenceImage') }}</label>
            <div 
              class="upload-area"
              :class="{ 'drag-over': isDragging, 'has-image': referenceImage }"
              @dragover.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
              @drop.prevent="handleImageDrop"
              @click="$refs.imageInput.click()"
            >
              <div v-if="referenceImage" class="preview-container">
                <img :src="referenceImage" alt="Reference" />
                <button class="remove-btn" @click.stop="referenceImage = null">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              </div>
              <div v-else class="upload-placeholder">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <rect x="3" y="3" width="18" height="18" rx="2"/>
                  <circle cx="8.5" cy="8.5" r="1.5"/>
                  <path d="M21 15l-5-5L5 21"/>
                </svg>
                <p>{{ $t('adsImgGen.dragDropImage') }}</p>
                <span>{{ $t('adsImgGen.orClickUpload') }}</span>
              </div>
            </div>
            <input 
              ref="imageInput"
              type="file" 
              accept="image/*"
              style="display: none"
              @change="handleImageUpload"
            />
            <p class="upload-hint">{{ $t('adsImgGen.uploadHint') }}</p>
          </div>
        </div>
      </div>

      <!-- Step 3: Style & Composition -->
      <div v-if="currentStep === 3" class="step-content step-3">
        <h2>{{ $t('adsImgGen.styleComposition') }}</h2>
        <p class="step-desc">{{ $t('adsImgGen.styleCompositionDesc') }}</p>
        
        <div class="style-section">
          <!-- Style Presets -->
          <div class="form-group">
            <label>{{ $t('adsImgGen.visualStyle') }}</label>
            <div class="style-presets-grid">
              <div 
                v-for="style in stylePresets" 
                :key="style.id"
                :class="['style-card', { selected: selectedStyle === style.id }]"
                @click="selectStyle(style.id)"
              >
                <div class="style-preview" :class="style.id"></div>
                <h4>{{ $t(`adsImgGen.styles.${style.id}`) }}</h4>
                <p>{{ $t(`adsImgGen.stylesDesc.${style.id}`) }}</p>
              </div>
            </div>
          </div>
          
          <!-- Composition -->
          <div class="form-group">
            <label>{{ $t('adsImgGen.composition') }}</label>
            <div class="options-grid">
              <button 
                v-for="comp in compositionOptions" 
                :key="comp.id"
                :class="['option-btn', { active: selectedComposition === comp.id }]"
                @click="selectedComposition = comp.id"
              >
                {{ $t(`adsImgGen.compositions.${comp.id}`) }}
              </button>
            </div>
          </div>
          
          <!-- Lighting -->
          <div class="form-group">
            <label>{{ $t('adsImgGen.lighting') }}</label>
            <div class="options-grid">
              <button 
                v-for="light in lightingOptions" 
                :key="light.id"
                :class="['option-btn', { active: selectedLighting === light.id }]"
                @click="selectedLighting = light.id"
              >
                {{ $t(`adsImgGen.lightingOptions.${light.id}`) }}
              </button>
            </div>
          </div>
          
          <!-- Aspect Ratio -->
          <div class="form-group">
            <label>{{ $t('adsImgGen.aspectRatio') }}</label>
            <div class="aspect-options">
              <button 
                v-for="ar in aspectRatios" 
                :key="ar.value"
                :class="['aspect-btn', { active: aspectRatio === ar.value }]"
                @click="aspectRatio = ar.value"
              >
                <div class="aspect-preview" :style="{ aspectRatio: ar.preview }"></div>
                <span>{{ ar.label }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 4: Generate -->
      <div v-if="currentStep === 4" class="step-content step-4">
        <h2>{{ $t('adsImgGen.generateAd') }}</h2>
        <p class="step-desc">{{ $t('adsImgGen.generateAdDesc') }}</p>
        
        <!-- Preview Prompt -->
        <div class="prompt-preview">
          <label>{{ $t('adsImgGen.generatedPrompt') }}</label>
          <div class="prompt-text">{{ generatedPrompt }}</div>
          <button class="edit-prompt-btn" @click="showPromptEditor = true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
            {{ $t('adsImgGen.editPrompt') }}
          </button>
        </div>
        
        <!-- Prompt Editor Modal -->
        <Teleport to="body">
          <div v-if="showPromptEditor" class="modal-backdrop" @click="showPromptEditor = false">
            <div class="prompt-editor-modal" @click.stop>
              <h3>{{ $t('adsImgGen.editPrompt') }}</h3>
              <textarea 
                v-model="editedPrompt" 
                class="prompt-editor-textarea"
                rows="8"
              ></textarea>
              <div class="modal-actions">
                <button class="btn-secondary" @click="showPromptEditor = false">
                  {{ $t('adsImgGen.cancel') }}
                </button>
                <button class="btn-primary" @click="applyEditedPrompt">
                  {{ $t('adsImgGen.apply') }}
                </button>
              </div>
            </div>
          </div>
        </Teleport>
        
        <!-- Generated Image -->
        <div class="generation-area">
          <!-- Loading State -->
          <div v-if="generating" class="loading-state">
            <div class="spinner-large"></div>
            <p>{{ $t('adsImgGen.generating') }}</p>
            <span>{{ $t('adsImgGen.generatingDesc') }}</span>
          </div>
          
          <!-- Generated Result -->
          <div v-else-if="generatedImage" class="generated-result">
            <img :src="generatedImage" alt="Generated Ad" referrerpolicy="no-referrer" />
            <div class="result-actions">
              <button class="action-btn primary" @click="downloadImage">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                  <polyline points="7 10 12 15 17 10"/>
                  <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                {{ $t('adsImgGen.download') }}
              </button>
              <button class="action-btn" @click="regenerate">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M23 4v6h-6"/>
                  <path d="M1 20v-6h6"/>
                  <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/>
                </svg>
                {{ $t('adsImgGen.regenerate') }}
              </button>
              <button class="action-btn" @click="useAsReference">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="3" width="18" height="18" rx="2"/>
                  <circle cx="8.5" cy="8.5" r="1.5"/>
                  <path d="M21 15l-5-5L5 21"/>
                </svg>
                {{ $t('adsImgGen.useAsRef') }}
              </button>
            </div>
          </div>
          
          <!-- Empty State -->
          <div v-else class="empty-generation">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
            <p>{{ $t('adsImgGen.clickGenerate') }}</p>
          </div>
        </div>
      </div>

      <!-- Navigation Buttons -->
      <div class="wizard-nav">
        <button 
          v-if="currentStep > 1" 
          class="btn-secondary"
          @click="prevStep"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
          {{ $t('adsImgGen.back') }}
        </button>
        
        <div class="nav-spacer"></div>
        
        <button 
          v-if="currentStep < 4" 
          class="btn-primary"
          :disabled="!canProceed"
          @click="nextStep"
        >
          {{ $t('adsImgGen.next') }}
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </button>
        
        <button 
          v-if="currentStep === 4" 
          class="btn-generate"
          :disabled="generating"
          @click="generateImage"
        >
          <span v-if="generating" class="btn-content">
            <span class="spinner"></span>
            {{ $t('adsImgGen.generating') }}
          </span>
          <span v-else class="btn-content">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
            {{ $t('adsImgGen.generate') }}
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { useI18n } from 'vue-i18n'
import api from '../services/api.js'
import { 
  adTypes, 
  stylePresets, 
  compositionOptions, 
  lightingOptions, 
  aspectRatios,
  fullPromptTemplates,
  defaultValues
} from '../data/adTemplates.js'

export default {
  name: 'AdsImgGen',
  setup() {
    const { t } = useI18n()
    return { t }
  },
  data() {
    return {
      currentStep: 1,
      selectedAdType: null,
      
      // Step 2 data
      formData: {
        productName: '',
        description: '',
        headline: '',
        ctaText: '',
        subject: '',
        action: '',
        setting: '',
        foodItem: '',
        presentation: '',
        contentType: 'Promotional content'
      },
      referenceImage: null,
      isDragging: false,
      
      // Step 3 data
      selectedStyle: 'minimal',
      selectedComposition: 'centered',
      selectedLighting: 'natural',
      aspectRatio: '1:1',
      
// Step 4 data
    generating: false,
    generatedImage: null,
    showPromptEditor: false,
    editedPrompt: '',
    useEditedPrompt: false,
      
      // Template data
      adTypes,
      stylePresets,
      compositionOptions,
      lightingOptions,
      aspectRatios
    }
  },
  computed: {
    canProceed() {
      if (this.currentStep === 1) {
        return this.selectedAdType !== null
      }
      if (this.currentStep === 2) {
        const nameField = this.selectedAdType === 'food' ? 'foodItem' : 'productName'
        return this.formData[nameField]?.trim()?.length > 0
      }
      return true
    },
    generatedPrompt() {
      return this.buildPrompt()
    }
  },
  methods: {
    // Icon components
    getIcon(iconName) {
      const icons = {
        package: {
          template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="16.5" y1="9.4" x2="7.5" y2="4.21"/>
            <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
            <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
            <line x1="12" y1="22.08" x2="12" y2="12"/>
          </svg>`
        },
        instagram: {
          template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
            <path d="M16 11.37A4 4 0 1112.63 8 4 4 0 0116 11.37z"/>
            <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/>
          </svg>`
        },
        camera: {
          template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/>
            <circle cx="12" cy="13" r="4"/>
          </svg>`
        },
        utensils: {
          template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 002-2V2"/>
            <path d="M7 2v20"/>
            <path d="M21 15V2v0a5 5 0 00-5 5v6c0 1.1.9 2 2 2h3zm0 0v7"/>
          </svg>`
        },
        briefcase: {
          template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
            <path d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16"/>
          </svg>`
        },
        megaphone: {
          template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 01-3.46 0"/>
          </svg>`
        }
      }
      return icons[iconName] || icons.package
    },
    
    selectAdType(typeId) {
      this.selectedAdType = typeId
      this.applyDefaults(typeId)
    },
    
    applyDefaults(typeId) {
      const defaults = defaultValues[typeId]
      if (defaults) {
        Object.keys(defaults).forEach(key => {
          if (this.formData.hasOwnProperty(key)) {
            this.formData[key] = defaults[key]
          }
        })
      }
    },
    
    selectStyle(styleId) {
      this.selectedStyle = styleId
    },
    
    // Image handling
    handleImageDrop(e) {
      this.isDragging = false
      const files = e.dataTransfer.files
      if (files.length > 0) {
        this.processImage(files[0])
      }
    },
    
    handleImageUpload(e) {
      const files = e.target.files
      if (files && files.length > 0) {
        this.processImage(files[0])
      }
      e.target.value = ''
    },
    
    processImage(file) {
      if (!file.type.startsWith('image/')) return
      
      if (file.size > 5 * 1024 * 1024) {
        alert('Image exceeds 5MB limit')
        return
      }
      
      const reader = new FileReader()
      reader.onload = (e) => {
        this.referenceImage = e.target.result
      }
      reader.readAsDataURL(file)
    },
    
    // Navigation
    nextStep() {
      if (this.canProceed && this.currentStep < 4) {
        this.currentStep++
      }
    },
    
    prevStep() {
      if (this.currentStep > 1) {
        this.currentStep--
      }
    },
    
    goToStep(step) {
      if (step < this.currentStep) {
        this.currentStep = step
      }
    },
    
    // Prompt building
    buildPrompt() {
      const style = stylePresets.find(s => s.id === this.selectedStyle)
      const composition = compositionOptions.find(c => c.id === this.selectedComposition)
      const lighting = lightingOptions.find(l => l.id === this.selectedLighting)
      
      const params = {
        ...this.formData,
        style: style?.style || 'minimalist',
        styleName: style?.name || 'Minimal',
        composition: composition?.value || 'centered hero shot composition',
        lighting: lighting?.value || 'soft natural window light',
        surface: style?.surface || 'clean surface'
      }
      
      const template = fullPromptTemplates[this.selectedAdType]
      if (template && template.buildPrompt) {
        return template.buildPrompt(params)
      }
      
      // Fallback prompt
      return `${params.productName || 'Product'} on ${params.surface}, ${params.composition}, ${params.lighting}, ${params.style} aesthetic, professional quality`
    },
    
applyEditedPrompt() {
      this.showPromptEditor = false
      this.useEditedPrompt = true
    },

    async generateImage() {
      const prompt = this.useEditedPrompt ? this.editedPrompt : this.generatedPrompt
      
      this.generating = true
      this.generatedImage = null
      
      try {
        const result = await api.generateNanoBanana({
          prompt: prompt,
          model: 'nano-banana-2',
          aspect_ratio: this.aspectRatio,
          reference_images: this.referenceImage ? [this.referenceImage] : null
        })
        
if (result.error) {
        alert(result.error)
      } else if (result.image_urls && result.image_urls.length > 0) {
        this.generatedImage = result.image_urls[0]
      } else {
        alert('No image generated')
      }
      } catch (error) {
        console.error('Generation failed:', error)
        alert('Failed to generate image: ' + (error.response?.data?.detail || error.message))
      } finally {
        this.generating = false
      }
    },
    
    async regenerate() {
      await this.generateImage()
    },
    
    async downloadImage() {
      if (!this.generatedImage) return
      
      try {
        const response = await fetch(this.generatedImage)
        const blob = await response.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `ad-${this.selectedAdType}-${Date.now()}.png`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      } catch (error) {
        window.open(this.generatedImage, '_blank')
      }
    },
    
    useAsReference() {
      if (this.generatedImage) {
        this.referenceImage = this.generatedImage
        this.currentStep = 2
      }
    }
  },
  watch: {
    generatedPrompt(newVal) {
      this.editedPrompt = newVal
      this.useEditedPrompt = false
    }
  }
}
</script>

<style scoped>
.ads-img-gen {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Step Indicator */
.step-indicator {
  display: flex;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  background: var(--bg-panel);
  border-radius: 16px;
}

.step {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border-radius: 12px;
  cursor: default;
  transition: all 0.2s;
}

.step.active {
  background: var(--accent-primary);
  color: #000;
}

.step.completed {
  cursor: pointer;
  opacity: 0.7;
}

.step.completed:hover {
  opacity: 1;
  background: rgba(255, 255, 255, 0.05);
}

.step-number {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  font-weight: 700;
  font-size: 0.875rem;
}

.step.active .step-number {
  background: rgba(0, 0, 0, 0.2);
}

.step-label {
  font-weight: 500;
  font-size: 0.875rem;
}

/* Wizard Container */
.wizard-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
  overflow-y: auto;
}

.step-content {
  flex: 1;
}

.step-content h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 8px;
}

.step-desc {
  color: var(--text-secondary);
  margin-bottom: 24px;
}

/* Step 1: Ad Types Grid */
.ad-types-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.ad-type-card {
  padding: 24px;
  background: var(--bg-panel);
  border: 2px solid var(--border-color);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.ad-type-card:hover {
  border-color: var(--border-hover);
  transform: translateY(-2px);
}

.ad-type-card.selected {
  border-color: var(--accent-primary);
  background: rgba(245, 158, 11, 0.1);
}

.ad-type-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  margin-bottom: 16px;
}

.ad-type-icon svg {
  width: 24px;
  height: 24px;
  color: var(--accent-primary);
}

.ad-type-card h3 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 8px;
}

.ad-type-card p {
  font-size: 0.875rem;
  color: var(--text-muted);
  line-height: 1.4;
}

/* Step 2: Form Grid */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}

.form-fields {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.form-input,
.form-textarea,
.form-select {
  padding: 12px 16px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 0.9375rem;
  font-family: inherit;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: var(--text-muted);
}

/* Image Upload */
.image-upload-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.upload-area {
  flex: 1;
  min-height: 250px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed var(--border-color);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
  overflow: hidden;
}

.upload-area:hover,
.upload-area.drag-over {
  border-color: var(--accent-primary);
  background: rgba(245, 158, 11, 0.05);
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--text-muted);
  text-align: center;
  padding: 40px;
}

.upload-placeholder svg {
  width: 48px;
  height: 48px;
  opacity: 0.4;
}

.upload-placeholder p {
  font-size: 1rem;
  color: var(--text-secondary);
}

.preview-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.preview-container img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.remove-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.7);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  transition: background 0.2s;
}

.remove-btn:hover {
  background: #ef4444;
}

.remove-btn svg {
  width: 18px;
  height: 18px;
}

.upload-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Step 3: Style Section */
.style-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.style-presets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.style-card {
  padding: 16px;
  background: var(--bg-panel);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.style-card:hover {
  border-color: var(--border-hover);
}

.style-card.selected {
  border-color: var(--accent-primary);
  background: rgba(245, 158, 11, 0.1);
}

.style-preview {
  width: 100%;
  height: 60px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.style-preview.minimal { background: linear-gradient(135deg, #f5f5f5, #fff); }
.style-preview.luxury { background: linear-gradient(135deg, #1a1a2e, #16213e); }
.style-preview.lifestyle { background: linear-gradient(135deg, #ffecd2, #fcb69f); }
.style-preview.dramatic { background: linear-gradient(135deg, #232526, #414345); }
.style-preview.fresh { background: linear-gradient(135deg, #e0f7fa, #80deea); }
.style-preview.editorial { background: linear-gradient(135deg, #f8f9fa, #e9ecef); }

.style-card h4 {
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 4px;
}

.style-card p {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.options-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.option-btn {
  padding: 10px 16px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.option-btn:hover {
  border-color: var(--border-hover);
  color: var(--text-primary);
}

.option-btn.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #000;
}

.aspect-options {
  display: flex;
  gap: 8px;
}

.aspect-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--bg-panel);
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

/* Step 4: Generation */
.prompt-preview {
  padding: 20px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  margin-bottom: 24px;
}

.prompt-preview label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  margin-bottom: 12px;
}

.prompt-text {
  font-size: 0.9375rem;
  line-height: 1.6;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.edit-prompt-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.edit-prompt-btn:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.edit-prompt-btn svg {
  width: 16px;
  height: 16px;
}

.generation-area {
  flex: 1;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-panel);
  border: 2px dashed var(--border-color);
  border-radius: 16px;
  overflow: hidden;
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

.generated-result {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.generated-result img {
  max-width: 100%;
  max-height: 50vh;
  object-fit: contain;
  border-radius: 12px;
}

.result-actions {
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
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.action-btn.primary {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #000;
}

.action-btn.primary:hover {
  background: var(--accent-primary-hover);
}

.action-btn svg {
  width: 18px;
  height: 18px;
}

.empty-generation {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--text-muted);
  text-align: center;
}

.empty-generation svg {
  width: 64px;
  height: 64px;
  opacity: 0.3;
}

.empty-generation p {
  font-size: 1rem;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 40px;
}

.prompt-editor-modal {
  background: var(--bg-elevated);
  border-radius: 16px;
  padding: 24px;
  max-width: 600px;
  width: 100%;
}

.prompt-editor-modal h3 {
  font-size: 1.125rem;
  margin-bottom: 16px;
}

.prompt-editor-textarea {
  width: 100%;
  padding: 16px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 0.9375rem;
  font-family: inherit;
  line-height: 1.6;
  resize: vertical;
}

.prompt-editor-textarea:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

/* Navigation */
.wizard-nav {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-spacer {
  flex: 1;
}

.btn-secondary,
.btn-primary,
.btn-generate {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

.btn-primary {
  background: var(--accent-primary);
  border: none;
  color: #000;
}

.btn-primary:hover:not(:disabled) {
  background: var(--accent-primary-hover);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-generate {
  background: linear-gradient(135deg, var(--accent-primary), #f59e0b);
  border: none;
  color: #000;
}

.btn-generate:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.3);
}

.btn-generate:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-secondary svg,
.btn-primary svg,
.btn-generate svg {
  width: 18px;
  height: 18px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0, 0, 0, 0.2);
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* Responsive */
@media (max-width: 768px) {
  .step-indicator {
    flex-wrap: wrap;
    gap: 4px;
    padding: 12px;
  }
  
  .step {
    padding: 8px 12px;
    flex: 1;
    min-width: 0;
  }
  
  .step-label {
    display: none;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .ad-types-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .style-presets-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .aspect-options {
    flex-wrap: wrap;
  }
  
  .result-actions {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>
