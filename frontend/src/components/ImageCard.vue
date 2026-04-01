<template>
  <div class="image-card" :class="{ processing: generation.status === 'processing' }">
    <div class="card-media">
      <!-- Video -->
      <video
        v-if="isVideo && mediaUrl"
        :src="mediaUrl"
        class="media"
        muted
        loop
        playsinline
        @mouseover="playVideo"
        @mouseleave="pauseVideo"
        @error="handleVideoError"
      />
      <!-- Image -->
      <img
        v-else-if="mediaUrl"
        :src="mediaUrl"
        :alt="generation.prompt"
        class="media"
        @error="handleImageError"
      />
      <!-- Processing Placeholder -->
      <div v-else class="placeholder">
        <div v-if="generation.status === 'processing'" class="progress-container">
          <div class="progress-ring">
            <svg viewBox="0 0 36 36">
              <circle cx="18" cy="18" r="16" fill="none" stroke="var(--bg-elevated)" stroke-width="3"/>
              <circle 
                cx="18" cy="18" r="16" 
                fill="none" 
                stroke="var(--accent-primary)" 
                stroke-width="3"
                stroke-linecap="round"
                :stroke-dasharray="`${(generation.progress || 0) * 1.01}, 100`"
                transform="rotate(-90 18 18)"
              />
            </svg>
            <span class="progress-text">{{ generation.progress || 0 }}%</span>
          </div>
          <span class="progress-label">{{ $t('imageCard.generating') }}</span>
        </div>
        <span v-else class="no-media">{{ $t('imageCard.noPreview') }}</span>
      </div>
      
      <!-- Hover Overlay -->
      <div v-if="generation.status === 'completed'" class="hover-overlay">
        <div class="overlay-actions">
          <button class="action-btn" @click.stop="$emit('fullscreen')" :title="$t('common.view')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
            </svg>
          </button>
          <a :href="mediaUrl" target="_blank" rel="noopener noreferrer" class="action-btn" @click.stop :title="$t('common.download')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
            </svg>
          </a>
          <button v-if="!isVideo && !showUseButton" class="action-btn video" @click.stop="$emit('create-video')" :title="$t('common.createVideo')">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z"/>
            </svg>
          </button>
          <button v-if="showUseButton" class="action-btn use" @click.stop="$emit('use-image')" :title="$t('common.useImage')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Prompt Display (1 line, click to expand) -->
    <div v-if="generation.prompt && generation.status === 'completed'" class="prompt-section">
      <div 
        class="prompt-text" 
        :class="{ expanded: promptExpanded }"
        @click="togglePrompt"
      >
        {{ generation.prompt }}
      </div>
      <button v-if="!promptExpanded && isLongPrompt" class="prompt-more" @click="togglePrompt">
        {{ $t('common.showMore') }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ImageCard',
  props: {
    generation: {
      type: Object,
      required: true
    },
    showUseButton: {
      type: Boolean,
      default: false
    }
  },
  emits: ['fullscreen', 'create-video', 'use-image'],
  data() {
    return {
      refreshing: false,
      promptExpanded: false
    }
  },
  computed: {
    isVideo() {
      return this.generation.generation_type === 'img2video' ||
        this.generation.generation_type === 'txt2video' ||
        this.generation.generation_type === 'audio2video' ||
        (this.generation.remote_url && 
         (this.generation.remote_url.endsWith('.mp4') || 
          this.generation.remote_url.endsWith('.webm')))
    },
    mediaUrl() {
      // Prefer local_path if available (won't expire)
      if (this.generation.local_path) {
        return `/api/media/${this.generation.generation_type}/${this.generation.local_path.split('/').pop()}`
      }
      return this.generation.remote_url || this.generation.thumbnail_url
    },
    downloadFilename() {
      const ext = this.isVideo ? '.mp4' : '.png'
      return `videlo-${this.generation.id}${ext}`
    },
    isLongPrompt() {
      return this.generation.prompt && this.generation.prompt.length > 50
    }
  },
  methods: {
    playVideo(e) {
      e.target.play().catch(() => {})
    },
    pauseVideo(e) {
      e.target.pause()
      e.target.currentTime = 0
    },
    togglePrompt() {
      this.promptExpanded = !this.promptExpanded
    },
    async handleVideoError(e) {
      // Try to refresh the URL if it's expired
      if (this.generation.uuid && !this.refreshing) {
        this.refreshing = true
        try {
          const response = await fetch(`/api/generations/${this.generation.id}/refresh-url`, {
            method: 'POST'
          })
          if (response.ok) {
            const data = await response.json()
            if (data.remote_url) {
              this.generation.remote_url = data.remote_url
              e.target.src = data.remote_url
            }
          }
        } catch (err) {
          // Silently handle refresh errors
        } finally {
          this.refreshing = false
        }
      }
    },
    async handleImageError(e) {
      // Try to refresh the URL if it's expired
      if (this.generation.uuid && !this.refreshing) {
        this.refreshing = true
        try {
          const response = await fetch(`/api/generations/${this.generation.id}/refresh-url`, {
            method: 'POST'
          })
          if (response.ok) {
            const data = await response.json()
            if (data.remote_url) {
              this.generation.remote_url = data.remote_url
              e.target.src = data.remote_url
            }
          }
        } catch (err) {
          // Silently handle refresh errors
        } finally {
          this.refreshing = false
        }
      }
    }
  }
}
</script>

<style scoped>
.image-card {
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  transition: all 0.2s ease;
}

.image-card:hover {
  border-color: var(--border-hover);
  transform: translateY(-2px);
}

.image-card:hover .hover-overlay {
  opacity: 1;
}

.card-media {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
}

.media {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.image-card:hover .media {
  transform: scale(1.05);
}

.placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-elevated);
}

.progress-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.progress-ring {
  position: relative;
  width: 64px;
  height: 64px;
}

.progress-ring svg {
  width: 100%;
  height: 100%;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--accent-primary);
}

.progress-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.no-media {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.hover-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8) 0%, transparent 50%);
  opacity: 0;
  transition: opacity 0.2s ease;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 16px;
  cursor: pointer;
}

.overlay-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(8px);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.15s ease;
  text-decoration: none;
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.action-btn:hover {
  background: var(--accent-primary);
  color: #000;
}

.action-btn.video:hover {
  background: var(--accent-secondary);
}

.action-btn.use:hover {
  background: var(--accent-secondary);
}

/* Prompt Section */
.prompt-section {
  padding: 8px 10px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-elevated);
}

.prompt-text {
  font-size: 0.75rem;
  color: var(--text-secondary);
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
  transition: all 0.2s ease;
}

.prompt-text.expanded {
  white-space: normal;
  display: -webkit-box;
  -webkit-line-clamp: unset;
  -webkit-box-orient: vertical;
}

.prompt-text:hover {
  color: var(--text-primary);
}

.prompt-more {
  display: block;
  margin-top: 4px;
  font-size: 0.6875rem;
  color: var(--accent-primary);
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  text-decoration: underline;
}

.prompt-more:hover {
  color: var(--accent-secondary);
}
</style>
