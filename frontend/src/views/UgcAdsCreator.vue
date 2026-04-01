<template>
  <div class="ugc-ads-page">
    <!-- Header -->
    <header class="page-header">
      <div class="header-content">
        <h1>UGC AI Ads Creator</h1>
        <p class="header-subtitle">Create realistic influencer-style video ads with AI</p>
      </div>
      <button class="stories-toggle" @click="showStoriesList = !showStoriesList">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
        </svg>
        <span>My Stories</span>
        <span class="count-badge">{{ stories.length }}</span>
      </button>
    </header>

    <!-- Stories List Sidebar -->
    <div v-if="showStoriesList" class="stories-sidebar">
      <div class="sidebar-header">
        <h3>Saved Stories</h3>
        <button class="close-btn" @click="showStoriesList = false">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
      <div class="stories-list">
        <div
          v-for="story in stories"
          :key="story.id"
          class="story-item"
          :class="{ active: currentStory?.id === story.id }"
          @click="loadStory(story.id)"
        >
          <div class="story-info">
            <span class="story-title">{{ story.title || story.product_name }}</span>
            <span class="story-meta">{{ story.target_platform }} · {{ story.total_duration_sec }}s</span>
          </div>
          <span class="story-status" :class="story.status">{{ story.status }}</span>
        </div>
        <div v-if="!stories.length" class="empty-stories">
          <p>No stories yet</p>
          <p class="hint">Create your first UGC ad story below</p>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Step 1: Product & Character Setup -->
      <div v-if="currentStep === 0" class="setup-panel">
        <div class="panel-header">
          <h2>Step 1: Product & Character</h2>
          <p>Tell us about your product and the influencer character</p>
        </div>

        <div class="form-grid">
          <!-- Product Section -->
          <div class="form-section">
            <h3>Product Information</h3>
            
            <div class="form-group">
              <label>Product Name *</label>
              <input v-model="form.productName" type="text" placeholder="e.g., Ankira Perfume" />
            </div>
            
            <div class="form-group">
              <label>Product Category</label>
              <select v-model="form.productCategory">
                <option value="">Select category</option>
                <option value="perfume">Perfume / Fragrance</option>
                <option value="beauty">Beauty / Cosmetics</option>
                <option value="fashion">Fashion / Apparel</option>
                <option value="food">Food / Beverage</option>
                <option value="tech">Tech / Gadgets</option>
                <option value="lifestyle">Lifestyle</option>
                <option value="fitness">Fitness</option>
                <option value="jewelry">Jewelry / Accessories</option>
                <option value="other">Other</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Product Description *</label>
              <textarea v-model="form.productDescription" rows="3" placeholder="Describe your product's key features and benefits..."></textarea>
            </div>
            
            <div class="form-group">
              <label>Product Reference Image (Optional)</label>
              <div class="image-upload">
                <input type="file" accept="image/*" @change="handleProductImage" ref="productImageInput" />
                <div class="upload-preview" v-if="form.productReferenceUrl">
                  <img :src="form.productReferenceUrl" alt="Product reference" />
                  <button class="remove-btn" @click="removeProductImage">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                  </button>
                </div>
                <div v-else class="upload-placeholder" @click="$refs.productImageInput.click()">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <rect x="3" y="3" width="18" height="18" rx="2"/>
                    <circle cx="8.5" cy="8.5" r="1.5"/>
                    <path d="M21 15l-5-5L5 21"/>
                  </svg>
                  <span>Click to upload product image</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Character Section -->
          <div class="form-section">
            <h3>Influencer Character</h3>
            
            <div class="form-group">
              <label>Character Name</label>
              <input v-model="form.characterName" type="text" placeholder="e.g., Maya" />
            </div>
            
            <div class="form-group">
              <label>Character Description</label>
              <textarea v-model="form.characterDescription" rows="3" placeholder="Describe the influencer's appearance, style, and personality..."></textarea>
            </div>
            
            <div class="form-group">
              <label>Character Reference Image (Optional)</label>
              <div class="image-upload">
                <input type="file" accept="image/*" @change="handleCharacterImage" ref="characterImageInput" />
                <div class="upload-preview" v-if="form.characterReferenceUrl">
                  <img :src="form.characterReferenceUrl" alt="Character reference" />
                  <button class="remove-btn" @click="removeCharacterImage">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                  </button>
                </div>
                <div v-else class="upload-placeholder" @click="$refs.characterImageInput.click()">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                  <span>Click to upload character image</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Ad Settings -->
        <div class="ad-settings">
          <h3>Ad Settings</h3>
          <div class="settings-grid">
            <div class="form-group">
              <label>Target Platform</label>
              <select v-model="form.platform">
                <option value="Instagram">Instagram Reels</option>
                <option value="TikTok">TikTok</option>
                <option value="YouTube">YouTube Shorts</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Ad Goal</label>
              <select v-model="form.adGoal">
                <option value="product_awareness">Product Awareness</option>
                <option value="conversion">Drive Conversions</option>
                <option value="engagement">Boost Engagement</option>
                <option value="brand_intro">Brand Introduction</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Tone</label>
              <select v-model="form.tone">
                <option value="authentic">Authentic & Natural</option>
                <option value="luxury">Luxury & Elegant</option>
                <option value="fun">Fun & Playful</option>
                <option value="emotional">Emotional & Heartfelt</option>
                <option value="energetic">Energetic & Exciting</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Duration</label>
              <select v-model="form.duration">
                <option :value="15">15 seconds</option>
                <option :value="30">30 seconds</option>
                <option :value="45">45 seconds</option>
                <option :value="60">60 seconds</option>
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label>Target Audience (Optional)</label>
            <input v-model="form.targetAudience" type="text" placeholder="e.g., Young professionals aged 25-35" />
          </div>
          
          <div class="form-group">
            <label>Setting Preference (Optional)</label>
            <input v-model="form.settingPreference" type="text" placeholder="e.g., Rooftop garden at night, cozy cafe, urban street" />
          </div>
        </div>

        <!-- Generate Button -->
        <div class="form-actions">
          <button
            class="btn-primary generate-btn"
            :disabled="isGenerating || !form.productName.trim() || !form.productDescription.trim()"
            @click="createStory"
          >
            <svg v-if="isGenerating" class="spinner" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-dasharray="31.4 31.4" transform="rotate(-90 12 12)"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
            {{ isGenerating ? 'Generating Story...' : 'Generate UGC Ad Story' }}
          </button>
        </div>
      </div>

      <!-- Step 2: Story Preview & Editing -->
      <div v-if="currentStep === 1 && currentStory" class="story-panel">
        <div class="panel-header">
          <h2>Step 2: Story Preview</h2>
          <p>Review and customize your UGC ad story</p>
        </div>

        <!-- Story Overview -->
        <div class="story-overview">
          <div class="overview-header">
            <h3>{{ currentStory.title }}</h3>
            <div class="story-badges">
              <span class="badge platform">{{ currentStory.target_platform }}</span>
              <span class="badge duration">{{ currentStory.total_duration_sec }}s</span>
              <span class="badge status" :class="currentStory.status">{{ currentStory.status }}</span>
            </div>
          </div>
          
          <div class="overview-content">
            <div class="overview-section">
              <h4>Hook</h4>
              <p class="hook-text">"{{ currentStory.hook }}"</p>
            </div>
            
            <div class="overview-section">
              <h4>Call to Action</h4>
              <p class="cta-text">"{{ currentStory.cta }}"</p>
            </div>
            
            <div class="overview-section">
              <h4>Setting</h4>
              <p>{{ currentStory.setting_description }}</p>
            </div>
          </div>
          
          <!-- Characters -->
          <div v-if="currentStory.characters?.length" class="characters-section">
            <h4>Characters</h4>
            <div class="characters-list">
              <div v-for="char in currentStory.characters" :key="char.name" class="character-card">
                <div class="char-name">{{ char.name }}</div>
                <div class="char-role">{{ char.role }}</div>
                <div class="char-details">
                  <span v-if="char.age">{{ char.age }} years old</span>
                  <span v-if="char.gender">{{ char.gender }}</span>
                </div>
                <p class="char-appearance">{{ char.appearance }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Scenes & Shots -->
        <div class="scenes-section">
          <div class="section-header">
            <h3>Scenes & Shots</h3>
            <div class="section-actions">
              <button
                class="btn-small"
                :disabled="isGeneratingAssets"
                @click="generateAssets"
              >
                {{ isGeneratingAssets ? 'Generating...' : 'Generate All Assets' }}
              </button>
            </div>
          </div>
          
          <div class="scenes-list">
            <div v-for="scene in currentStory.scenes" :key="scene.id" class="scene-block">
              <div class="scene-header">
                <span class="scene-number">Scene {{ scene.scene_num }}</span>
                <span class="scene-name">{{ scene.scene_name }}</span>
                <span class="scene-meta">{{ scene.mood }}</span>
              </div>
              
              <div class="shots-list">
                <div v-for="shot in scene.shots" :key="shot.id" class="shot-card">
                  <div class="shot-preview">
                    <img v-if="shot.first_frame_url" :src="shot.first_frame_url" alt="" />
                    <div v-else class="preview-placeholder">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <rect x="3" y="3" width="18" height="18" rx="2"/>
                        <circle cx="8.5" cy="8.5" r="1.5"/>
                        <path d="M21 15l-5-5L5 21"/>
                      </svg>
                    </div>
                    
                    <!-- Video Preview -->
                    <video v-if="shot.video_url" :src="shot.video_url" controls muted loop class="video-preview"></video>
                    
                    <div class="shot-badges">
                      <span class="badge" :class="shot.first_frame_status">{{ shot.first_frame_status }}</span>
                      <span class="badge" :class="shot.video_status">{{ shot.video_status }}</span>
                    </div>
                  </div>
                  
                  <div class="shot-info">
                    <div class="shot-header">
                      <span class="shot-number">Shot {{ shot.shot_num }}</span>
                      <span class="shot-duration">{{ shot.duration_sec }}s</span>
                    </div>
                    
                    <div class="shot-content">
                      <p class="shot-description">{{ shot.frame_description }}</p>
                      <p v-if="shot.dialogue" class="shot-dialogue">"{{ shot.dialogue }}"</p>
                      <p v-if="shot.action" class="shot-action">{{ shot.action }}</p>
                    </div>
                    
                    <div class="shot-meta">
                      <span v-if="shot.camera_angle">{{ shot.camera_angle }}</span>
                      <span v-if="shot.lighting">{{ shot.lighting }}</span>
                    </div>
                    
                    <div class="shot-actions">
                      <button
                        class="btn-tiny"
                        :disabled="shot.first_frame_status === 'processing'"
                        @click="regenerateShot(shot, true, false)"
                      >
                        Regenerate Image
                      </button>
                      <button
                        class="btn-tiny"
                        :disabled="shot.video_status === 'processing' || !shot.first_frame_url"
                        @click="regenerateShot(shot, false, true)"
                      >
                        Regenerate Video
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Navigation -->
        <div class="panel-actions">
          <button class="btn-secondary" @click="currentStep = 0; currentStory = null">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 4v16m0-16L8 8m4-4l4 4"/>
            </svg>
            Create New Story
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'UgcAdsCreator',
  
  data() {
    return {
      currentStep: 0,
      showStoriesList: false,
      isGenerating: false,
      isGeneratingAssets: false,
      pollIntervalId: null,
      
      stories: [],
      currentStory: null,
      
      form: {
        productName: '',
        productCategory: '',
        productDescription: '',
        productReferenceUrl: null,
        characterName: '',
        characterDescription: '',
        characterReferenceUrl: null,
        platform: 'Instagram',
        adGoal: 'product_awareness',
        tone: 'authentic',
        duration: 15,
        targetAudience: '',
        settingPreference: ''
      }
    }
  },
  
  mounted() {
    this.loadStories()
  },
  
  beforeUnmount() {
    // Clear polling interval to prevent memory leaks
    if (this.pollIntervalId) {
      clearInterval(this.pollIntervalId)
      this.pollIntervalId = null
    }
  },
  
  methods: {
    async loadStories() {
      try {
        const response = await api.getUgcStories()
        this.stories = response.items || []
      } catch (error) {
        console.error('Failed to load stories:', error)
      }
    },
    
    async loadStory(storyId) {
      try {
        this.currentStory = await api.getUgcStory(storyId)
        this.currentStep = 1
        this.showStoriesList = false
      } catch (error) {
        console.error('Failed to load story:', error)
      }
    },
    
    async createStory() {
      this.isGenerating = true
      
      try {
        const story = await api.createUgcStory({
          productName: this.form.productName,
          productCategory: this.form.productCategory,
          productDescription: this.form.productDescription,
          productReferenceUrl: this.form.productReferenceUrl,
          characterName: this.form.characterName,
          characterDescription: this.form.characterDescription,
          characterReferenceUrl: this.form.characterReferenceUrl,
          platform: this.form.platform,
          adGoal: this.form.adGoal,
          tone: this.form.tone,
          totalDurationSec: this.form.duration,
          targetAudience: this.form.targetAudience,
          settingPreference: this.form.settingPreference
        })
        
        this.currentStory = story
        this.currentStep = 1
        this.loadStories()
        
      } catch (error) {
        console.error('Failed to create story:', error)
        alert('Failed to create story: ' + (error.response?.data?.detail || error.message))
      } finally {
        this.isGenerating = false
      }
    },
    
    async generateAssets() {
      if (!this.currentStory) return
      
      this.isGeneratingAssets = true
      
      try {
        await api.generateUgcStoryAssets(this.currentStory.id, {
          generateImages: true,
          generateVideos: true,
          aspectRatio: this.form.platform === 'TikTok' ? '9:16' : '16:9'
        })
        
        // Start polling for updates
        this.pollStoryStatus()
        
      } catch (error) {
        console.error('Failed to generate assets:', error)
        alert('Failed to generate assets: ' + (error.response?.data?.detail || error.message))
        this.isGeneratingAssets = false
      }
    },
    
    async pollStoryStatus() {
      // Clear any existing interval first
      if (this.pollIntervalId) {
        clearInterval(this.pollIntervalId)
      }
      
      this.pollIntervalId = setInterval(async () => {
        try {
          const story = await api.getUgcStory(this.currentStory.id)
          this.currentStory = story
          
          // Check if all done
          const allImagesDone = story.scenes.every(s => 
            s.shots.every(sh => sh.first_frame_status === 'completed' || sh.first_frame_status === 'failed')
          )
          const allVideosDone = story.scenes.every(s => 
            s.shots.every(sh => sh.video_status === 'completed' || sh.video_status === 'failed')
          )
          
          if (allImagesDone && allVideosDone) {
            clearInterval(this.pollIntervalId)
            this.pollIntervalId = null
            this.isGeneratingAssets = false
          }
          
        } catch (error) {
          console.error('Failed to poll story status:', error)
          clearInterval(this.pollIntervalId)
          this.pollIntervalId = null
          this.isGeneratingAssets = false
        }
      }, 5000)
    },
    
    async regenerateShot(shot, regenerateImage, regenerateVideo) {
      try {
        await api.regenerateUgcShot(this.currentStory.id, shot.id, {
          regenerateImage,
          regenerateVideo
        })
        
        // Poll for updates
        this.pollStoryStatus()
        
      } catch (error) {
        console.error('Failed to regenerate shot:', error)
        alert('Failed to regenerate shot: ' + (error.response?.data?.detail || error.message))
      }
    },
    
    handleProductImage(event) {
      const file = event.target.files[0]
      if (!file) return
      
      // Validate file type
      if (!file.type.startsWith('image/')) {
        alert('Please select a valid image file')
        return
      }
      
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert('Image must be smaller than 10MB')
        return
      }
      
      const reader = new FileReader()
      reader.onload = (e) => {
        this.form.productReferenceUrl = e.target.result
      }
      reader.onerror = () => {
        alert('Failed to read image file')
      }
      reader.readAsDataURL(file)
    },
    
    handleCharacterImage(event) {
      const file = event.target.files[0]
      if (!file) return
      
      // Validate file type
      if (!file.type.startsWith('image/')) {
        alert('Please select a valid image file')
        return
      }
      
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert('Image must be smaller than 10MB')
        return
      }
      
      const reader = new FileReader()
      reader.onload = (e) => {
        this.form.characterReferenceUrl = e.target.result
      }
      reader.onerror = () => {
        alert('Failed to read image file')
      }
      reader.readAsDataURL(file)
    },
    
    removeProductImage() {
      this.form.productReferenceUrl = null
    },
    
    removeCharacterImage() {
      this.form.characterReferenceUrl = null
    }
  }
}
</script>

<style scoped>
.ugc-ads-page {
  min-height: 100vh;
  background: #0a0a0a;
  color: #fff;
  padding: 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-content h1 {
  font-size: 1.75rem;
  font-weight: 600;
  margin: 0;
  background: linear-gradient(135deg, #f5d0a9 0%, #e8a87c 50%, #d4af37 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-subtitle {
  color: rgba(255, 255, 255, 0.6);
  margin: 0.5rem 0 0 0;
  font-size: 0.9rem;
}

.stories-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.stories-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
}

.stories-toggle svg {
  width: 1.25rem;
  height: 1.25rem;
}

.count-badge {
  background: linear-gradient(135deg, #f5d0a9, #d4af37);
  color: #000;
  padding: 0.125rem 0.5rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
}

/* Sidebar */
.stories-sidebar {
  position: fixed;
  top: 0;
  right: 0;
  width: 320px;
  height: 100vh;
  background: #141414;
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 100;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-header h3 {
  margin: 0;
  font-size: 1.125rem;
}

.close-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  padding: 0.25rem;
}

.close-btn:hover {
  color: #fff;
}

.stories-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.story-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.story-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

.story-item.active {
  background: rgba(212, 175, 55, 0.15);
  border: 1px solid rgba(212, 175, 55, 0.3);
}

.story-title {
  font-weight: 500;
  display: block;
}

.story-meta {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
}

.story-status {
  font-size: 0.625rem;
  text-transform: uppercase;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  background: rgba(255, 255, 255, 0.1);
}

.story-status.completed {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.story-status.generating {
  background: rgba(245, 208, 169, 0.2);
  color: #f5d0a9;
}

.story-status.failed {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.empty-stories {
  text-align: center;
  padding: 2rem;
  color: rgba(255, 255, 255, 0.5);
}

.empty-stories .hint {
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

/* Main Content */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
}

.setup-panel,
.story-panel {
  background: #141414;
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 2rem;
}

.panel-header {
  margin-bottom: 2rem;
}

.panel-header h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
}

.panel-header p {
  margin: 0;
  color: rgba(255, 255, 255, 0.6);
}

/* Form Grid */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.form-section {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.form-section h3 {
  margin: 0 0 1.25rem 0;
  font-size: 1rem;
  color: #f5d0a9;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: rgba(255, 255, 255, 0.8);
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  color: #fff;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: rgba(212, 175, 55, 0.5);
  box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1);
}

.form-group input::placeholder,
.form-group textarea::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.form-group select option {
  background: #1a1a1a;
}

/* Image Upload */
.image-upload input[type="file"] {
  display: none;
}

.upload-preview {
  position: relative;
}

.upload-preview img {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 0.5rem;
}

.remove-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: rgba(0, 0, 0, 0.7);
  border: none;
  color: #fff;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-placeholder {
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 0.5rem;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-placeholder:hover {
  border-color: rgba(212, 175, 55, 0.5);
  background: rgba(255, 255, 255, 0.02);
}

.upload-placeholder svg {
  width: 2rem;
  height: 2rem;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 0.5rem;
}

.upload-placeholder span {
  display: block;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.875rem;
}

/* Ad Settings */
.ad-settings {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.ad-settings h3 {
  margin: 0 0 1.25rem 0;
  font-size: 1rem;
  color: #f5d0a9;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

/* Buttons */
.form-actions {
  display: flex;
  justify-content: center;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #f5d0a9 0%, #d4af37 100%);
  border: none;
  border-radius: 0.5rem;
  color: #000;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
}

.btn-small {
  padding: 0.5rem 1rem;
  background: rgba(212, 175, 55, 0.15);
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-radius: 0.375rem;
  color: #f5d0a9;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-small:hover:not(:disabled) {
  background: rgba(212, 175, 55, 0.25);
}

.btn-small:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-tiny {
  padding: 0.375rem 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.25rem;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-tiny:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.btn-tiny:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  width: 1.25rem;
  height: 1.25rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Story Overview */
.story-overview {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.overview-header h3 {
  margin: 0;
  font-size: 1.25rem;
}

.story-badges {
  display: flex;
  gap: 0.5rem;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.badge.platform {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.badge.duration {
  background: rgba(168, 85, 247, 0.2);
  color: #a855f7;
}

.badge.status {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.overview-content {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.overview-section h4 {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
}

.hook-text,
.cta-text {
  font-style: italic;
  color: #f5d0a9;
}

/* Characters */
.characters-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.characters-section h4 {
  margin: 0 0 1rem 0;
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
}

.characters-list {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.character-card {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 0.5rem;
  padding: 1rem;
  flex: 1;
  min-width: 200px;
}

.char-name {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.char-role {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  text-transform: capitalize;
  margin-bottom: 0.5rem;
}

.char-details {
  display: flex;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 0.5rem;
}

.char-appearance {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.4;
}

/* Scenes */
.scenes-section {
  margin-top: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h3 {
  margin: 0;
  font-size: 1.125rem;
}

.scene-block {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 0.75rem;
  margin-bottom: 1.5rem;
  overflow: hidden;
}

.scene-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background: rgba(0, 0, 0, 0.2);
}

.scene-number {
  font-weight: 600;
  color: #f5d0a9;
}

.scene-name {
  font-weight: 500;
}

.scene-meta {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.5);
}

.shots-list {
  padding: 1rem;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.shot-card {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 0.5rem;
  overflow: hidden;
}

.shot-preview {
  position: relative;
  aspect-ratio: 16/9;
  background: rgba(0, 0, 0, 0.3);
}

.shot-preview img,
.shot-preview video {
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
  color: rgba(255, 255, 255, 0.3);
}

.preview-placeholder svg {
  width: 2.5rem;
  height: 2.5rem;
}

.shot-badges {
  position: absolute;
  bottom: 0.5rem;
  left: 0.5rem;
  display: flex;
  gap: 0.25rem;
}

.shot-badges .badge {
  font-size: 0.625rem;
  padding: 0.125rem 0.5rem;
  text-transform: capitalize;
}

.shot-badges .badge.completed {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.shot-badges .badge.processing {
  background: rgba(245, 208, 169, 0.2);
  color: #f5d0a9;
}

.shot-badges .badge.pending {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.5);
}

.shot-badges .badge.failed {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.shot-info {
  padding: 1rem;
}

.shot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.shot-number {
  font-size: 0.75rem;
  color: #f5d0a9;
}

.shot-duration {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
}

.shot-description {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.4;
  margin-bottom: 0.5rem;
}

.shot-dialogue {
  font-size: 0.8rem;
  font-style: italic;
  color: #f5d0a9;
  margin-bottom: 0.5rem;
}

.shot-action {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
}

.shot-meta {
  display: flex;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 0.75rem;
}

.shot-actions {
  display: flex;
  gap: 0.5rem;
}

.video-preview {
  position: absolute;
  top: 0;
  left: 0;
}

.panel-actions {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

/* Responsive */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .settings-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .overview-content {
    grid-template-columns: 1fr;
  }
  
  .shots-list {
    grid-template-columns: 1fr;
  }
}
</style>
