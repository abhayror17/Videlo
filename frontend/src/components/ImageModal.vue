<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
        <button class="close-btn" @click="$emit('close')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
        
        <a
          v-if="mediaUrl"
          :href="mediaUrl"
          target="_blank"
          rel="noopener noreferrer"
          class="download-btn"
          @click.stop
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          <span>{{ $t('imageModal.download') }}</span>
        </a>
        
        <div class="media-container" @click.self="$emit('close')">
          <video
            v-if="isVideo && mediaUrl"
            :src="mediaUrl"
            controls
            autoplay
            loop
            class="media-player"
            @click.stop
            @error="handleMediaError"
          />
          <img
            v-else-if="mediaUrl"
            :src="mediaUrl"
            :alt="generation.prompt"
            class="media-player"
            @click.stop
            @error="handleMediaError"
          />
          <div v-else class="no-media">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10"/>
              <line x1="15" y1="9" x2="9" y2="15"/>
              <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
            <span>{{ $t('imageModal.mediaNotAvailable') }}</span>
          </div>
        </div>
        
        <div v-if="generation.prompt" class="prompt-bar" :class="{ expanded: promptExpanded }">
          <p class="prompt-text" :class="{ expanded: promptExpanded }">{{ generation.prompt }}</p>
          <button 
            v-if="isLongPrompt" 
            class="prompt-toggle" 
            @click.stop="togglePrompt"
          >
            {{ promptExpanded ? $t('common.showLess') : $t('common.showMore') }}
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script>
export default {
  name: 'ImageModal',
  props: {
    visible: Boolean,
    generation: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['close'],
  data() {
    return {
      refreshing: false,
      promptExpanded: false
    }
  },
  computed: {
    mediaUrl() {
      // Prefer local_path if available (won't expire)
      if (this.generation.local_path) {
        return `/api/media/${this.generation.generation_type}/${this.generation.local_path.split('/').pop()}`
      }
      return this.generation.remote_url || this.generation.thumbnail_url || null
    },
    isVideo() {
      return this.generation.generation_type === 'img2video' ||
        this.generation.generation_type === 'txt2video' ||
        this.generation.generation_type === 'audio2video' ||
        (this.generation.remote_url && 
         (this.generation.remote_url.endsWith('.mp4') || 
          this.generation.remote_url.endsWith('.webm')))
    },
    downloadFilename() {
      const ext = this.isVideo ? '.mp4' : '.png'
      return `videlo-${this.generation.id}${ext}`
    },
    isLongPrompt() {
      return this.generation.prompt && this.generation.prompt.length > 80
    }
  },
  watch: {
    visible(val) {
      document.body.style.overflow = val ? 'hidden' : ''
      // Reset expanded state when modal closes
      if (!val) {
        this.promptExpanded = false
      }
    }
  },
  methods: {
    togglePrompt() {
      this.promptExpanded = !this.promptExpanded
    },
    async handleMediaError(e) {
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
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  cursor: pointer;
}

.close-btn {
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
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
  z-index: 10;
}

.close-btn svg {
  width: 18px;
  height: 18px;
}

.close-btn:hover {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #000;
}

.download-btn {
  position: fixed;
  top: 20px;
  right: 72px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.15s ease;
  z-index: 10;
}

.download-btn svg {
  width: 16px;
  height: 16px;
}

.download-btn:hover {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #000;
}

.media-container {
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 95vw;
  max-height: 85vh;
  padding: 20px;
}

.media-player {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
  border-radius: 8px;
  cursor: default;
}

.no-media {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--text-muted);
}

.no-media svg {
  width: 48px;
  height: 48px;
}

.prompt-bar {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  max-width: 80%;
  padding: 14px 24px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  transition: all 0.2s ease;
}

.prompt-bar.expanded {
  max-width: 90%;
  max-height: 30vh;
  overflow-y: auto;
}

.prompt-text {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.875rem;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 70vw;
  cursor: pointer;
}

.prompt-text.expanded {
  white-space: normal;
  text-overflow: unset;
  max-width: unset;
  text-align: left;
  line-height: 1.5;
}

.prompt-toggle {
  display: block;
  margin-top: 8px;
  padding: 4px 12px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--accent-primary);
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.prompt-toggle:hover {
  background: var(--accent-primary);
  color: #000;
  border-color: var(--accent-primary);
}

.modal-enter-active,
.modal-leave-active {
  transition: all 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .media-player,
.modal-leave-to .media-player {
  transform: scale(0.95);
}
</style>
