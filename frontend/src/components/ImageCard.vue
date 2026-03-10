<template>
  <div class="image-card" :class="{ processing: generation.status === 'processing' }">
    <div class="card-media">
      <!-- Video -->
      <video
        v-if="isVideo && (generation.remote_url || generation.thumbnail_url)"
        :src="generation.remote_url || generation.thumbnail_url"
        class="media"
        muted
        loop
        playsinline
        @mouseover="playVideo"
        @mouseleave="pauseVideo"
      />
      <!-- Image -->
      <img
        v-else-if="generation.thumbnail_url || generation.remote_url"
        :src="generation.thumbnail_url || generation.remote_url"
        :alt="generation.prompt"
        class="media"
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
          <span class="progress-label">Generating</span>
        </div>
        <span v-else class="no-media">No preview</span>
      </div>
      
      <!-- Hover Overlay -->
      <div v-if="generation.status === 'completed'" class="hover-overlay">
        <div class="overlay-actions">
          <button class="action-btn" @click.stop="$emit('fullscreen')" title="View">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
            </svg>
          </button>
          <a :href="mediaUrl" :download="downloadFilename" class="action-btn" @click.stop title="Download">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
            </svg>
          </a>
          <button v-if="!isVideo" class="action-btn video" @click.stop="$emit('create-video')" title="Create Video">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z"/>
            </svg>
          </button>
        </div>
      </div>
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
    }
  },
  emits: ['fullscreen', 'create-video'],
  computed: {
    isVideo() {
      return this.generation.generation_type === 'img2video' ||
        (this.generation.remote_url && 
         (this.generation.remote_url.endsWith('.mp4') || 
          this.generation.remote_url.endsWith('.webm')))
    },
    mediaUrl() {
      return this.generation.remote_url || this.generation.thumbnail_url
    },
    downloadFilename() {
      const ext = this.isVideo ? '.mp4' : '.png'
      return `videlo-${this.generation.id}${ext}`
    }
  },
  methods: {
    playVideo(e) {
      e.target.play().catch(() => {})
    },
    pauseVideo(e) {
      e.target.pause()
      e.target.currentTime = 0
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
</style>
