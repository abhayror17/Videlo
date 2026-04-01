<template>
  <div class="gallery">
    <div class="gallery-header">
      <h2 class="section-title">{{ $t('gallery.title') }}</h2>
      
      <div class="filter-tabs">
        <button 
          :class="['filter-btn', { active: filterType === 'all' }]"
          @click="setFilter('all')"
        >{{ $t('gallery.all') }}</button>
        <button 
          :class="['filter-btn', { active: filterType === 'text2img' }]"
          @click="setFilter('text2img')"
        >{{ $t('gallery.images') }}</button>
        <button 
          :class="['filter-btn', { active: filterType === 'img2video' }]"
          @click="setFilter('img2video')"
        >{{ $t('gallery.videos') }}</button>
      </div>
    </div>
    
    <div v-if="initialLoad && loading" class="loading-state">
      <div class="loader"></div>
      <p>{{ $t('gallery.loading') }}</p>
    </div>
    
    <div v-else-if="generations.length === 0" class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <rect x="3" y="3" width="18" height="18" rx="2"/>
        <circle cx="8.5" cy="8.5" r="1.5"/>
        <path d="M21 15l-5-5L5 21"/>
      </svg>
      <p>{{ $t('gallery.noCreationsYet') }}</p>
      <span>{{ $t('gallery.startGenerating') }}</span>
    </div>
    
    <transition v-else name="fade" mode="out-in">
      <div class="grid" :key="page + '-' + filterType">
        <ImageCard
          v-for="gen in generations"
          :key="gen.id"
          :generation="gen"
          @fullscreen="$emit('select', gen)"
          @create-video="$emit('create-video', gen)"
        />
      </div>
    </transition>
    
    <div v-if="totalPages > 1" class="pagination">
      <button
        :disabled="page === 1"
        @click="changePage(page - 1)"
        class="page-btn"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
      </button>
      
      <div class="page-numbers">
        <button
          v-for="p in displayPages"
          :key="p"
          :class="['page-num', { active: p === page, dots: p === '...' }]"
          @click="p !== '...' && changePage(p)"
          :disabled="p === '...'"
        >{{ p }}</button>
      </div>
      
      <button
        :disabled="page >= totalPages"
        @click="changePage(page + 1)"
        class="page-btn"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script>
import ImageCard from './ImageCard.vue'
import api from '../services/api.js'

export default {
  name: 'Gallery',
  components: { ImageCard },
  emits: ['select', 'create-video'],
  data() {
    return {
      generations: [],
      loading: true,
      initialLoad: true,
      page: 1,
      totalPages: 1,
      filterType: 'all'
    }
  },
  async mounted() {
    await this.loadGenerations()
  },
  computed: {
    displayPages() {
      const pages = []
      const total = this.totalPages
      const current = this.page
      
      if (total <= 5) {
        for (let i = 1; i <= total; i++) pages.push(i)
      } else {
        pages.push(1)
        if (current > 3) pages.push('...')
        
        const start = Math.max(2, current - 1)
        const end = Math.min(total - 1, current + 1)
        
        for (let i = start; i <= end; i++) {
          if (!pages.includes(i)) pages.push(i)
        }
        
        if (current < total - 2) pages.push('...')
        if (!pages.includes(total)) pages.push(total)
      }
      
      return pages
    }
  },
  methods: {
    async loadGenerations() {
      this.loading = true
      try {
        const typeParam = this.filterType === 'all' ? null : this.filterType
        const response = await api.getGenerations(this.page, 12, typeParam)
        this.generations = response.items
        this.totalPages = response.pages
      } catch (error) {
        // Silently handle errors
      } finally {
        this.loading = false
        this.initialLoad = false
      }
    },
    async setFilter(type) {
      this.filterType = type
      this.page = 1
      await this.loadGenerations()
    },
    async changePage(newPage) {
      this.page = newPage
      await this.loadGenerations()
    },
    async refresh() {
      await this.loadGenerations()
    }
  }
}
</script>

<style scoped>
.gallery {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.gallery-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.filter-tabs {
  display: flex;
  gap: 4px;
  padding: 4px;
  background: var(--bg-panel);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.filter-btn {
  padding: 8px 16px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--text-muted);
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.filter-btn:hover {
  color: var(--text-secondary);
}

.filter-btn.active {
  background: var(--accent-primary);
  color: #000;
}

.grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  flex: 1;
}

@media (max-width: 1200px) {
  .grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 900px) {
  .grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 600px) {
  .grid { grid-template-columns: 1fr; }
}

.loading-state,
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.loader {
  width: 32px;
  height: 32px;
  border: 2px solid var(--border-color);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state svg {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  font-size: 0.9375rem;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.empty-state span {
  font-size: 0.8125rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.page-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.page-btn svg {
  width: 16px;
  height: 16px;
}

.page-btn:hover:not(:disabled) {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 4px;
}

.page-num {
  min-width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-muted);
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.page-num:hover:not(:disabled):not(.dots) {
  border-color: var(--border-hover);
  color: var(--text-primary);
}

.page-num.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #000;
}

.page-num.dots {
  background: transparent;
  border-color: transparent;
  cursor: default;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>