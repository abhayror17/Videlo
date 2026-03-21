<template>
  <div class="prompts-gallery">
    <!-- Header -->
    <div class="gallery-header">
      <div class="header-left">
        <h1 class="page-title">{{ $t('prompts.title') }}</h1>
        <p class="page-subtitle">{{ $t('prompts.subtitle') }}</p>
      </div>
      <div class="header-right">
        <div class="view-toggle">
          <button 
            :class="['view-btn', { active: viewMode === 'grid' }]" 
            @click="viewMode = 'grid'"
            title="Grid View"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="7" height="7"/>
              <rect x="14" y="3" width="7" height="7"/>
              <rect x="3" y="14" width="7" height="7"/>
              <rect x="14" y="14" width="7" height="7"/>
            </svg>
          </button>
          <button 
            :class="['view-btn', { active: viewMode === 'list' }]" 
            @click="viewMode = 'list'"
            title="List View"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="8" y1="6" x2="21" y2="6"/>
              <line x1="8" y1="12" x2="21" y2="12"/>
              <line x1="8" y1="18" x2="21" y2="18"/>
              <line x1="3" y1="6" x2="3.01" y2="6"/>
              <line x1="3" y1="12" x2="3.01" y2="12"/>
              <line x1="3" y1="18" x2="3.01" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="prompts-count">
          <svg class="count-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
          <div class="count-content">
            <span class="count-number">{{ totalPrompts.toLocaleString() }}</span>
            <span class="count-label">{{ $t('prompts.prompts') }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="controls-bar">
      <div class="search-wrapper">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35"/>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="$t('prompts.searchPlaceholder')"
          class="search-input"
          @input="debouncedSearch"
        />
        <button v-if="searchQuery" class="clear-search" @click="clearSearch">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <div class="filter-controls">
        <div class="tags-filter">
          <button
            :class="['tag-chip', { active: selectedTag === null }]"
            @click="selectTag(null)"
          >
            {{ $t('prompts.allTags') }}
          </button>
          <button
            v-for="tag in popularTags"
            :key="tag"
            :class="['tag-chip', { active: selectedTag === tag }]"
            @click="selectTag(tag)"
          >
            {{ tag }}
          </button>
        </div>
      </div>
    </div>

    <!-- Active Filters Display -->
    <div v-if="selectedTag || searchQuery" class="active-filters">
      <span class="filter-label">{{ $t('prompts.filteringBy') }}:</span>
      <button v-if="selectedTag" class="active-filter" @click="selectTag(null)">
        {{ selectedTag }}
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
      <button v-if="searchQuery" class="active-filter" @click="clearSearch">
        "{{ searchQuery }}"
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
      <button class="clear-all-btn" @click="clearAllFilters">
        {{ $t('prompts.clearAll') }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="prompts-grid-skeleton">
      <div v-for="i in 12" :key="i" class="skeleton-card">
        <div class="skeleton-image"></div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredPrompts.length === 0" class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="11" cy="11" r="8"/>
        <path d="M21 21l-4.35-4.35"/>
        <path d="M8 11h6"/>
      </svg>
      <p>{{ $t('prompts.noResults') }}</p>
      <span>{{ $t('prompts.tryDifferent') }}</span>
    </div>

    <!-- Prompts Grid -->
    <transition v-else name="stagger-fade">
      <div class="prompts-grid" :class="viewMode + '-view'" :key="selectedTag + '-' + searchQuery + '-' + currentPage">
        <div
          v-for="prompt in paginatedPrompts"
          :key="prompt.id"
          class="prompt-card"
          @click="openPromptModal(prompt)"
        >
          <div class="card-image-wrapper">
            <div class="image-skeleton" v-if="!imageLoaded[prompt.id]"></div>
            <img 
              :src="prompt.image_url" 
              :alt="prompt.title" 
              referrerpolicy="no-referrer"
              class="actual-image"
              :class="{ loaded: imageLoaded[prompt.id] }"
              @load="handleImageLoad(prompt.id)"
              @error="handleImageError($event, prompt.id)"
            />
            <div class="image-error-fallback" v-if="imageError[prompt.id]">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <path d="M21 15l-5-5L5 21"/>
              </svg>
            </div>
            <!-- Multi-image indicator -->
            <div v-if="prompt.image_urls && prompt.image_urls.length > 1" class="multi-image-badge">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <path d="M3 9h18"/>
                <path d="M9 21V9"/>
              </svg>
              <span>{{ prompt.image_urls.length }}</span>
            </div>
            <!-- Copy button -->
            <button class="card-copy-btn" @click.stop="copyPrompt(prompt)" title="Copy prompt">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
              </svg>
            </button>
            <!-- Create button -->
            <button class="card-create-btn" @click.stop="createWithPrompt(prompt)" title="Create with this prompt">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <div class="pagination-info">
        {{ $t('prompts.showing') }} {{ (currentPage - 1) * itemsPerPage + 1 }}-{{ Math.min(currentPage * itemsPerPage, filteredPrompts.length) }} {{ $t('prompts.of') }} {{ filteredPrompts.length }}
      </div>
      <div class="pagination-controls">
        <button
          class="page-btn"
          :disabled="currentPage === 1"
          @click="currentPage = 1"
          :title="$t('prompts.firstPage')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="11 17 6 12 11 7"/>
            <polyline points="18 17 13 12 18 7"/>
          </svg>
        </button>
        <button
          class="page-btn"
          :disabled="currentPage === 1"
          @click="currentPage--"
          :title="$t('prompts.prevPage')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
        </button>
        
        <div class="page-numbers">
          <button
            v-for="p in displayPages"
            :key="p"
            :class="['page-num', { active: p === currentPage, dots: p === '...' }]"
            @click="p !== '...' && (currentPage = p)"
            :disabled="p === '...'"
          >{{ p }}</button>
        </div>
        
        <button
          class="page-btn"
          :disabled="currentPage >= totalPages"
          @click="currentPage++"
          :title="$t('prompts.nextPage')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </button>
        <button
          class="page-btn"
          :disabled="currentPage >= totalPages"
          @click="currentPage = totalPages"
          :title="$t('prompts.lastPage')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="13 17 18 12 13 7"/>
            <polyline points="6 17 11 12 6 7"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Prompt Modal -->
    <Teleport to="body">
      <div v-if="selectedPrompt" class="modal-backdrop" @click.self="closePromptModal">
        <div class="prompt-modal">
          <button class="modal-close" @click="closePromptModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>

          <div class="modal-image">
            <img :src="currentModalImage" :alt="selectedPrompt.title" referrerpolicy="no-referrer" />
            <!-- Create with this image button -->
            <button class="modal-create-btn" @click="createWithPrompt(selectedPrompt, currentModalImage)" title="Create with this image">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
              </svg>
              <span>Create</span>
            </button>
            <!-- Multi-image navigation -->
            <div v-if="modalImages.length > 1" class="image-nav">
              <button class="nav-btn prev" @click="prevModalImage" :disabled="modalImageIndex === 0">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="15 18 9 12 15 6"/>
                </svg>
              </button>
              <div class="image-dots">
                <button 
                  v-for="(img, idx) in modalImages" 
                  :key="idx" 
                  :class="['dot', { active: idx === modalImageIndex }]"
                  @click="modalImageIndex = idx"
                ></button>
              </div>
              <button class="nav-btn next" @click="nextModalImage" :disabled="modalImageIndex === modalImages.length - 1">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9 18 15 12 9 6"/>
                </svg>
              </button>
            </div>
            <div v-if="modalImages.length > 1" class="image-counter">
              {{ modalImageIndex + 1 }} / {{ modalImages.length }}
            </div>
          </div>

          <div class="modal-content">
            <h2 class="modal-title">{{ selectedPrompt.title || 'Prompt' }}</h2>

            <div class="modal-tags">
              <button
                v-for="tag in selectedPrompt.tags"
                :key="tag"
                class="modal-tag"
                @click="selectTag(tag); closePromptModal()"
              >
                {{ tag }}
              </button>
            </div>

            <div class="modal-section">
              <h3>{{ $t('prompts.promptText') }}</h3>
              <div class="prompt-text-wrapper">
                <p class="prompt-text">{{ selectedPrompt.prompt }}</p>
                <button class="copy-prompt-btn" @click="copyPrompt(selectedPrompt)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                    <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
                  </svg>
                  {{ copied ? $t('prompts.copied') : $t('prompts.copyPrompt') }}
                </button>
              </div>
            </div>

            <div class="modal-meta">
              <div class="meta-item" v-if="selectedPrompt.model">
                <span class="meta-label">{{ $t('prompts.model') }}</span>
                <span class="meta-value">{{ selectedPrompt.model }}</span>
              </div>
              <div class="meta-item" v-if="selectedPrompt.id">
                <span class="meta-label">{{ $t('prompts.id') }}</span>
                <span class="meta-value">{{ selectedPrompt.id }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Toast Notification -->
    <Teleport to="body">
      <transition name="toast">
        <div v-if="showToast" class="toast">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          {{ toastMessage }}
        </div>
      </transition>
    </Teleport>

    <!-- Scroll to Top Button -->
    <Teleport to="body">
      <transition name="fade">
        <button 
          v-if="showScrollTop" 
          class="scroll-top-btn"
          @click="scrollToTop"
          title="Scroll to top"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="18 15 12 9 6 15"/>
          </svg>
        </button>
      </transition>
    </Teleport>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

export default {
  name: 'PromptsGallery',
  setup() {
    const { t } = useI18n()
    const router = useRouter()

    const prompts = ref([])
    const loading = ref(true)
    const searchQuery = ref('')
    const selectedTag = ref(null)
    const selectedPrompt = ref(null)
    const modalImageIndex = ref(0)
    const viewMode = ref('grid')
    const sortBy = ref('default')
    const showScrollTop = ref(false)
    
    // Image loading states per card
    const imageLoaded = ref({})
    const imageError = ref({})

    const handleImageLoad = (id) => {
      imageLoaded.value[id] = true
    }

    const handleImageError = (event, id) => {
      imageError.value[id] = true
      console.error('Image failed to load:', id)
    }

    const modalImages = computed(() => {
      if (!selectedPrompt.value) return []
      return selectedPrompt.value.image_urls || [selectedPrompt.value.image_url]
    })
    const currentModalImage = computed(() => {
      return modalImages.value[modalImageIndex.value] || selectedPrompt.value?.image_url
    })
    
    const prevModalImage = () => {
      if (modalImageIndex.value > 0) modalImageIndex.value--
    }
    const nextModalImage = () => {
      if (modalImageIndex.value < modalImages.value.length - 1) modalImageIndex.value++
    }
    const copied = ref(false)
    const showToast = ref(false)
    const toastMessage = ref('')
    const totalPrompts = ref(0)
    
    // Pagination
    const currentPage = ref(1)
    const itemsPerPage = 24

    // Popular tags for filter
    const popularTags = ref([
      'marketing', 'product', 'photography', 'cinematic',
      'minimal', 'food-drink', 'illustration', 'portrait-selfie',
      'abstract-background', 'render-3d', 'text-layout', 'cyberpunk-scifi'
    ])

    // All available tags for API fetching
    const apiTags = ['marketing', 'product', 'photography', 'cinematic']

    // Debounce search
    let searchTimeout = null
    const debouncedSearch = () => {
      clearTimeout(searchTimeout)
    }

    // Filter prompts based on search and tag
    const filteredPrompts = computed(() => {
      let result = prompts.value

      if (selectedTag.value) {
        result = result.filter(p =>
          p.tags && p.tags.includes(selectedTag.value)
        )
      }

      if (searchQuery.value.trim()) {
        const query = searchQuery.value.toLowerCase().trim()
        result = result.filter(p =>
          (p.prompt && p.prompt.toLowerCase().includes(query)) ||
          (p.title && p.title.toLowerCase().includes(query)) ||
          (p.tags && p.tags.some(tag => tag.toLowerCase().includes(query)))
        )
      }

      return result
    })

    // Paginated prompts
    const paginatedPrompts = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage
      const end = start + itemsPerPage
      return filteredPrompts.value.slice(start, end)
    })

    // Total pages
    const totalPages = computed(() => {
      return Math.ceil(filteredPrompts.value.length / itemsPerPage)
    })

    // Display pages for pagination
    const displayPages = computed(() => {
      const pages = []
      const total = totalPages.value
      const current = currentPage.value
      
      if (total <= 7) {
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
    })

    // Fetch prompts from API for multiple tags
    const fetchPrompts = async () => {
      loading.value = true
      prompts.value = []
      imageLoaded.value = {}
      imageError.value = {}
      
      try {
        // Try to load from local file first (more reliable)
        const localResponse = await fetch('/all_prompts.json')
        if (localResponse.ok) {
          const data = await localResponse.json()
          prompts.value = Array.isArray(data) ? data : []
          totalPrompts.value = prompts.value.length
          console.log('Loaded prompts from local file:', prompts.value.length)
        } else {
          // Fallback to API if local file not found
          console.log('Local file not found, trying API...')
          const seenIds = new Set()
          for (const tag of apiTags) {
            try {
              const response = await fetch(`https://nanobananaprompt.club/api/prompts?tags=${tag}&limit=200`)
              const data = await response.json()
              const items = data.items || []
              
              for (const item of items) {
                if (!seenIds.has(item.id)) {
                  seenIds.add(item.id)
                  prompts.value.push({
                    id: item.id,
                    image_url: item.imageUrl || item.sourceUrl || (item.imageUrls && item.imageUrls[0]),
                    prompt: item.prompt || '',
                    tags: item.tags || [],
                    title: item.title || '',
                    model: item.model || '',
                    source_tag: tag
                  })
                }
              }
            } catch (e) {
              console.error(`Failed to fetch tag ${tag}:`, e)
            }
          }
          totalPrompts.value = prompts.value.length
        }

        // Extract all unique tags for filtering
        const allTags = new Set()
        prompts.value.forEach(p => {
          if (p.tags) {
            p.tags.forEach(tag => allTags.add(tag))
          }
        })
        popularTags.value = Array.from(allTags).slice(0, 16)
      } catch (error) {
        console.error('Failed to fetch prompts:', error)
      } finally {
        // Add a small delay for smoother transition
        setTimeout(() => {
          loading.value = false
        }, 600)
      }
    }

    // Select tag filter
    const selectTag = (tag) => {
      selectedTag.value = tag
    }

    // Clear search
    const clearSearch = () => {
      searchQuery.value = ''
    }

    // Clear all filters
    const clearAllFilters = () => {
      selectedTag.value = null
      searchQuery.value = ''
    }

    // Truncate text helper
    const truncateText = (text, maxLength) => {
      if (!text) return ''
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
    }

    // Copy prompt to clipboard
    const copyPrompt = async (prompt) => {
      try {
        await navigator.clipboard.writeText(prompt.prompt)
        copied.value = true
        showToastMessage(t('prompts.copied'))
        setTimeout(() => {
          copied.value = false
        }, 2000)
      } catch (error) {
        console.error('Failed to copy:', error)
      }
    }

    // Navigate to img-gen page with prompt and reference image
    const createWithPrompt = (prompt, imageUrl = null) => {
      const query = { prompt: prompt.prompt }
      // Use provided image URL or first image from prompt
      const refImage = imageUrl || prompt.image_url || (prompt.image_urls && prompt.image_urls[0])
      if (refImage) {
        query.ref = refImage
      }
      router.push({
        path: '/img-gen',
        query
      })
    }

    // Show toast message
    const showToastMessage = (message) => {
      toastMessage.value = message
      showToast.value = true
      setTimeout(() => {
        showToast.value = false
      }, 2000)
    }

    // Open/close modal
    const openPromptModal = (prompt) => {
      selectedPrompt.value = prompt
      modalImageIndex.value = 0
      document.body.style.overflow = 'hidden'
    }

    const closePromptModal = () => {
      selectedPrompt.value = null
      document.body.style.overflow = ''
    }

    // Scroll to top function
    const scrollToTop = () => {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }

    // Handle scroll for scroll-to-top button
    const handleScroll = () => {
      showScrollTop.value = window.scrollY > 400
    }

    // Fetch on mount
    onMounted(() => {
      fetchPrompts()
      window.addEventListener('scroll', handleScroll)
    })

    // Close modal on escape and navigate images with arrows
    const handleKeyboard = (e) => {
      if (!selectedPrompt.value) return
      
      if (e.key === 'Escape') {
        closePromptModal()
      } else if (e.key === 'ArrowLeft') {
        prevModalImage()
      } else if (e.key === 'ArrowRight') {
        nextModalImage()
      }
    }

    // Add/remove keyboard listener
    watch(selectedPrompt, (newVal) => {
      if (newVal) {
        document.addEventListener('keydown', handleKeyboard)
      } else {
        document.removeEventListener('keydown', handleKeyboard)
      }
    })

    // Reset to page 1 when filters change
    watch([selectedTag, searchQuery], () => {
      currentPage.value = 1
    })

    return {
      prompts,
      loading,
      searchQuery,
      selectedTag,
      selectedPrompt,
      copied,
      showToast,
      toastMessage,
      totalPrompts,
      popularTags,
      filteredPrompts,
      paginatedPrompts,
      totalPages,
      displayPages,
      currentPage,
      itemsPerPage,
      debouncedSearch,
      selectTag,
      clearSearch,
      clearAllFilters,
      truncateText,
      copyPrompt,
      createWithPrompt,
      openPromptModal,
      closePromptModal,
      modalImageIndex,
      modalImages,
      currentModalImage,
      prevModalImage,
      nextModalImage,
      handleImageLoad,
      handleImageError,
      imageLoaded,
      imageError,
      viewMode,
      sortBy,
      showScrollTop,
      scrollToTop,
      t
    }
  }
}
</script>

<style scoped>
.prompts-gallery {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  padding: 0 0 40px 0;
  color: var(--text-primary);
}

/* Header */
.gallery-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-shrink: 0;
}

.page-title {
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #fff 0%, #a3a3a3 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 1rem;
  color: var(--text-muted);
}

.prompts-count {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-radius: 16px;
  position: relative;
  overflow: hidden;
}

.prompts-count::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(245, 158, 11, 0.5), transparent);
}

/* Controls Bar */
.controls-bar {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 24px;
  padding: 16px 20px;
  background: rgba(11, 11, 11, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid var(--border-color);
}

.search-wrapper {
  position: relative;
  max-width: 500px;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 14px 48px 14px 52px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  color: var(--text-primary);
  font-size: 0.9375rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.search-input:focus {
  outline: none;
  border-color: var(--accent-primary);
  background: var(--bg-elevated);
  box-shadow: 0 0 0 4px rgba(245, 158, 11, 0.15), 0 8px 30px rgba(0, 0, 0, 0.2);
}

.clear-search {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-elevated);
  border: none;
  border-radius: 50%;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-search:hover {
  background: var(--border-hover);
  color: var(--text-primary);
  transform: scale(1.1);
}

/* Tags Filter */
.tags-filter {
  display: flex;
  flex-wrap: nowrap;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.tags-filter::-webkit-scrollbar {
  display: none;
}

.tag-chip {
  flex-shrink: 0;
  padding: 6px 14px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.tag-chip:hover {
  background: var(--bg-panel);
  border-color: var(--border-hover);
  color: var(--text-primary);
}

.tag-chip.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #000;
}

/* Active Filters */
.active-filters {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
  padding: 10px 16px;
  background: rgba(245, 158, 11, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.filter-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 500;
}

.active-filter {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: var(--accent-primary);
  border: none;
  border-radius: 20px;
  color: #000;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.active-filter:hover {
  background: #fbbf24;
}

.active-filter svg {
  width: 12px;
  height: 12px;
}

.clear-all-btn {
  padding: 4px 12px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-left: auto;
}

.clear-all-btn:hover {
  border-color: var(--text-primary);
  color: var(--text-primary);
}

/* Prompts Grid */
.prompts-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  flex: 1;
}

.prompts-grid.list-view {
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.prompts-grid.list-view .card-image-wrapper {
  aspect-ratio: 16/10;
}

/* View Toggle */
.view-toggle {
  display: flex;
  background: var(--bg-panel);
  border-radius: 12px;
  padding: 4px;
  border: 1px solid var(--border-color);
}

.view-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-btn:hover {
  color: var(--text-primary);
}

.view-btn.active {
  background: var(--accent-primary);
  color: #000;
}

.view-btn svg {
  width: 18px;
  height: 18px;
}

/* Enhanced Header Right */
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.count-number {
  font-size: 1.5rem;
  font-weight: 900;
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 50%, #f59e0b 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
}

.count-label {
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.count-icon {
  width: 24px;
  height: 24px;
  color: var(--accent-primary);
  flex-shrink: 0;
}

.count-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}

/* Prompt Card */
.prompt-card {
  background: transparent;
  border: none;
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  display: block;
  position: relative;
}

.prompt-card:hover {
  transform: translateY(-4px);
}

.card-image-wrapper {
  position: relative;
  aspect-ratio: 3/4;
  background: var(--bg-elevated);
  overflow: hidden;
  border-radius: 20px;
  border: 1px solid var(--border-color);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.prompt-card:hover .card-image-wrapper {
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: 
    0 20px 50px rgba(0, 0, 0, 0.5),
    0 0 0 1px rgba(255, 255, 255, 0.1);
}

.actual-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0;
  transition: opacity 0.6s ease, transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.actual-image.loaded {
  opacity: 1;
}

.prompt-card:hover .actual-image {
  transform: scale(1.04);
}

.image-skeleton {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, var(--bg-elevated) 25%, var(--bg-panel) 50%, var(--bg-elevated) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 20px;
}

.image-error-fallback {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-panel);
  border-radius: 20px;
}

.image-error-fallback svg {
  width: 48px;
  height: 48px;
  color: var(--text-muted);
  opacity: 0.3;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Multi-image Badge */
.multi-image-badge {
  position: absolute;
  top: 14px;
  right: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 10px;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.6875rem;
  font-weight: 600;
  z-index: 3;
  transition: all 0.2s ease;
}

.prompt-card:hover .multi-image-badge {
  background: rgba(0, 0, 0, 0.7);
  border-color: rgba(255, 255, 255, 0.2);
}

.multi-image-badge svg {
  width: 12px;
  height: 12px;
}

/* Copy Button */
.card-copy-btn {
  position: absolute;
  top: 14px;
  left: 14px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  z-index: 3;
  opacity: 0;
  transform: translateY(-4px);
  transition: all 0.3s ease;
}

.prompt-card:hover .card-copy-btn {
  opacity: 1;
  transform: translateY(0);
}

.card-copy-btn:hover {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #000;
}

.card-copy-btn svg {
  width: 16px;
  height: 16px;
}

/* Create Button */
.card-create-btn {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  z-index: 3;
  opacity: 0;
  transform: translateY(-4px);
  transition: all 0.3s ease;
}

.prompt-card:hover .card-create-btn {
  opacity: 1;
  transform: translateY(0);
}

.card-create-btn:hover {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #000;
}

.card-create-btn svg {
  width: 16px;
  height: 16px;
}

/* Skeleton Grid */
.prompts-grid-skeleton {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.skeleton-card {
  background: transparent;
  border-radius: 20px;
  overflow: hidden;
}

.skeleton-image {
  aspect-ratio: 3/4;
  background: var(--bg-elevated);
  position: relative;
  overflow: hidden;
  border-radius: 20px;
  border: 1px solid var(--border-color);
}

.skeleton-image::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
  animation: shimmer 1.5s infinite;
}

/* Empty State */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-state svg {
  width: 80px;
  height: 80px;
  color: var(--text-muted);
  opacity: 0.3;
  margin-bottom: 24px;
}

.empty-state p {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.empty-state span {
  font-size: 0.875rem;
  color: var(--text-muted);
}

/* Transitions */
.stagger-fade-enter-active {
  transition: all 0.5s ease;
}

.stagger-fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

/* Pagination */
.pagination {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-top: 32px;
  padding: 20px 24px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 16px;
}

.pagination-info {
  font-size: 0.8125rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.page-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 10px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-btn:hover:not(:disabled) {
  background: var(--bg-elevated);
  border-color: var(--border-color);
  color: var(--text-primary);
}

.page-btn:disabled {
  opacity: 0.25;
  cursor: not-allowed;
}

.page-btn svg {
  width: 16px;
  height: 16px;
}

.page-numbers {
  display: flex;
  gap: 4px;
  margin: 0 8px;
}

.page-num {
  min-width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 10px;
  color: var(--text-muted);
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-num:hover:not(:disabled):not(.dots) {
  background: var(--bg-elevated);
  border-color: var(--border-hover);
  color: var(--text-primary);
  transform: translateY(-2px);
}

.page-num:hover:not(:disabled):not(.dots) {
  background: var(--bg-elevated);
  border-color: var(--border-color);
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
  color: var(--text-muted);
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 24px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.prompt-modal {
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 24px;
  max-width: 1000px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: row;
  position: relative;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5);
  animation: modalSlideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes modalSlideUp {
  from {
    opacity: 0;
    transform: translateY(40px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-close {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  color: #fff;
  cursor: pointer;
  z-index: 100;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: rotate(90deg);
}

.modal-image {
  flex: 1.2;
  position: relative;
  background: var(--bg-elevated);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 500px;
}

.modal-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.modal-create-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--accent-primary);
  border: none;
  border-radius: 8px;
  color: #000;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  z-index: 10;
}

.modal-create-btn:hover {
  background: var(--accent-primary-hover);
  transform: scale(1.02);
}

.modal-create-btn svg {
  width: 16px;
  height: 16px;
}

.image-nav {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(12px);
  border-radius: 30px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-btn:hover:not(:disabled) {
  transform: scale(1.2);
  color: var(--accent-primary);
}

.nav-btn:disabled {
  opacity: 0.2;
  cursor: not-allowed;
}

.image-dots {
  display: flex;
  gap: 8px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0;
}

.dot.active {
  width: 24px;
  background: var(--accent-primary);
}

.modal-content {
  flex: 1;
  padding: 40px;
  overflow-y: auto;
  background: linear-gradient(135deg, var(--bg-panel) 0%, var(--bg-base) 100%);
  display: flex;
  flex-direction: column;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #fff;
  margin-bottom: 24px;
  line-height: 1.3;
}

.modal-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 28px;
}

.modal-tag {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.modal-tag:hover {
  background: rgba(245, 158, 11, 0.1);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
  transform: translateY(-2px);
}

.modal-section {
  margin-bottom: 32px;
}

.modal-section h3 {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

.prompt-text-wrapper {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  position: relative;
}

.prompt-text {
  font-size: 0.9375rem;
  line-height: 1.6;
  color: var(--text-primary);
  margin-bottom: 20px;
  white-space: pre-wrap;
}

.copy-prompt-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  background: var(--accent-primary);
  border: none;
  border-radius: 12px;
  color: #000;
  font-size: 0.875rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.copy-prompt-btn:hover {
  background: #fff;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(245, 158, 11, 0.3);
}

.modal-meta {
  margin-top: auto;
  padding-top: 32px;
  border-top: 1px solid var(--border-color);
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.meta-label {
  display: block;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.meta-value {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
}

/* Toast */
.toast {
  position: fixed;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 28px;
  background: #fff;
  border-radius: 16px;
  color: #000;
  font-weight: 700;
  z-index: 3000;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

.toast-enter-active, .toast-leave-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.toast-enter-from, .toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(40px);
}

/* Scroll to Top Button */
.scroll-top-btn {
  position: fixed;
  bottom: 100px;
  right: 32px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-primary);
  border: none;
  border-radius: 50%;
  color: #000;
  cursor: pointer;
  z-index: 2500;
  box-shadow: 0 8px 30px rgba(245, 158, 11, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.scroll-top-btn:hover {
  transform: translateY(-4px) scale(1.1);
  box-shadow: 0 12px 40px rgba(245, 158, 11, 0.5);
}

.scroll-top-btn svg {
  width: 24px;
  height: 24px;
}

.fade-enter-active, .fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* Responsive */
@media (max-width: 1024px) {
  .prompts-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }
  
  .prompt-modal {
    flex-direction: column;
    max-height: 95vh;
  }
  
  .modal-image {
    min-height: 300px;
  }
}

@media (max-width: 768px) {
  .pagination {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }

  .pagination-info {
    order: 1;
  }

  .pagination-controls {
    order: 0;
  }

  .page-numbers {
    max-width: 200px;
    overflow-x: auto;
  }
}

@media (max-width: 640px) {
  .gallery-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .header-right {
    width: 100%;
    justify-content: space-between;
  }

  .controls-bar {
    padding: 12px 16px;
    gap: 12px;
  }

  .tags-filter {
    gap: 8px;
  }

  .tag-chip {
    padding: 6px 12px;
    font-size: 0.75rem;
  }

  .prompts-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .card-image-wrapper {
    border-radius: 16px;
  }

  .card-copy-btn {
    width: 30px;
    height: 30px;
    opacity: 1;
    transform: translateY(0);
  }

  .multi-image-badge {
    padding: 4px 8px;
    font-size: 0.625rem;
  }

  .pagination {
    padding: 16px;
  }
  
  .page-btn, .page-num {
    width: 32px;
    height: 32px;
    min-width: 32px;
    font-size: 0.75rem;
  }
  
  .modal-content {
    padding: 24px;
  }
}
</style>
