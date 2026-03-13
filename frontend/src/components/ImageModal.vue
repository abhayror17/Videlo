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
          :download="downloadFilename"
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
          />
          <img
            v-else-if="mediaUrl"
            :src="mediaUrl"
            :alt="generation.prompt"
            class="media-player"
            @click.stop
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
        
        <div v-if="generation.prompt" class="prompt-bar">
          <p>{{ generation.prompt }}</p>
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
  computed: {
    mediaUrl() {
      return this.generation.remote_url || this.generation.thumbnail_url || null
    },
    isVideo() {
      return this.generation.generation_type === 'img2video' ||
        (this.generation.remote_url && 
         (this.generation.remote_url.endsWith('.mp4') || 
          this.generation.remote_url.endsWith('.webm')))
    },
    downloadFilename() {
      const ext = this.isVideo ? '.mp4' : '.png'
      return `videlo-${this.generation.id}${ext}`
    }
  },
  watch: {
    visible(val) {
      document.body.style.overflow = val ? 'hidden' : ''
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
}

.prompt-bar p {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.875rem;
  text-align: center;
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