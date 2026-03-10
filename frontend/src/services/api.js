import axios from 'axios'

// Use environment variable for production, fallback to /api for development (proxied by Vite)
const baseURL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL,
  timeout: 30000
})

export default {
  // Text-to-Image generation
  async generateText2Img(prompt, options = {}) {
    const response = await api.post('/generate/text2img', {
      prompt,
      negative_prompt: options.negativePrompt,
      model: options.model || 'Flux_2_Klein_4B_BF16',
      width: options.width || 1024,
      height: options.height || 768,
      guidance: options.guidance ?? 3.5,
      steps: options.steps || 4,
      seed: options.seed ?? -1
    })
    return response.data
  },

  // Text-to-Video generation
  async generateTxt2Video(prompt, options = {}) {
    const response = await api.post('/generate/txt2video', {
      prompt,
      model: options.model || 'Ltxv_13B_0_9_8_Distilled_FP8',
      width: options.width || 512,
      height: options.height || 512,
      guidance: options.guidance ?? 3.5,
      steps: options.steps || 20,
      frames: options.frames || 24,
      fps: options.fps || 30,
      seed: options.seed ?? -1
    })
    return response.data
  },

  // Image-to-Video generation using gallery image (generation_id)
  async generateImg2Video(generationId, prompt, options = {}) {
    const formData = new FormData()
    formData.append('generation_id', generationId)
    formData.append('prompt', prompt)
    formData.append('model', options.model || 'Ltx2_19B_Dist_FP8')
    formData.append('width', options.width || 512)
    formData.append('height', options.height || 512)
    formData.append('guidance', options.guidance ?? 3.5)
    formData.append('steps', options.steps || 20)
    formData.append('frames', options.frames || 24)
    formData.append('fps', options.fps || 30)
    formData.append('seed', options.seed ?? -1)

    const response = await api.post('/generate/img2video', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 120000
    })
    return response.data
  },

  // Image-to-Video generation with file upload
  async generateImg2VideoWithFile(imageFile, prompt, options = {}) {
    const formData = new FormData()
    formData.append('first_frame', imageFile)
    formData.append('prompt', prompt)
    formData.append('model', options.model || 'Ltx2_19B_Dist_FP8')
    formData.append('width', options.width || 512)
    formData.append('height', options.height || 512)
    formData.append('guidance', options.guidance ?? 3.5)
    formData.append('steps', options.steps || 20)
    formData.append('frames', options.frames || 24)
    formData.append('fps', options.fps || 30)
    formData.append('seed', options.seed ?? -1)

    const response = await api.post('/generate/img2video', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 120000
    })
    return response.data
  },

  // Image-to-Image generation (edit/transform images)
  async generateImg2Img(imageFile, prompt, options = {}) {
    const formData = new FormData()
    formData.append('image', imageFile)
    formData.append('prompt', prompt)
    formData.append('model', options.model || 'QwenImageEdit_Plus_NF4')
    formData.append('guidance', options.guidance ?? 3.5)
    formData.append('steps', options.steps || 20)
    formData.append('seed', options.seed ?? -1)
    if (options.negativePrompt) {
      formData.append('negative_prompt', options.negativePrompt)
    }

    const response = await api.post('/generate/img2img', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 120000
    })
    return response.data
  },

  // Image-to-Image generation using gallery image (generation_id)
  async generateImg2ImgFromGeneration(generationId, prompt, options = {}) {
    const formData = new FormData()
    formData.append('generation_id', generationId)
    formData.append('prompt', prompt)
    formData.append('model', options.model || 'QwenImageEdit_Plus_NF4')
    formData.append('guidance', options.guidance ?? 3.5)
    formData.append('steps', options.steps || 20)
    formData.append('seed', options.seed ?? -1)
    if (options.negativePrompt) {
      formData.append('negative_prompt', options.negativePrompt)
    }

    const response = await api.post('/generate/img2img', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 120000
    })
    return response.data
  },

  // Legacy generate method (defaults to text2img)
  async generate(prompt, options = {}) {
    return this.generateText2Img(prompt, options)
  },

  // List generations
  async getGenerations(page = 1, perPage = 4, generationType = null) {
    const params = { page, per_page: perPage }
    if (generationType) params.generation_type = generationType
    
    const response = await api.get('/generations', { params })
    return response.data
  },

  // Get single generation
  async getGeneration(id) {
    const response = await api.get(`/generations/${id}`)
    return response.data
  },

  // Poll status
  async getStatus(id) {
    const response = await api.get(`/generations/${id}/status`)
    return response.data
  },

  // Get balance
  async getBalance() {
    const response = await api.get('/balance')
    return response.data
  },

  // List models
  async getModels(inferenceType = null) {
    const params = {}
    if (inferenceType) params.inference_type = inferenceType
    
    const response = await api.get('/models', { params })
    return response.data
  },

  // Health check
  async health() {
    const response = await api.get('/health')
    return response.data
  },

  // Enhance prompt
  async enhancePrompt(prompt) {
    const response = await api.post('/enhance-prompt', { prompt }, {
      timeout: 60000
    })
    return response.data
  },

  // Get random prompt
  async getRandomPrompt() {
    const response = await api.get('/random-prompt', {
      timeout: 30000
    })
    return response.data
  },

  // AI Ads Generator APIs
  // Create a new ad campaign
  async createAdCampaign(data) {
    const response = await api.post('/ads/generate', data, {
      timeout: 30000
    })
    return response.data
  },

  // Get list of ad campaigns
  async getAdCampaigns(page = 1, perPage = 10) {
    const response = await api.get('/ads', {
      params: { page, per_page: perPage }
    })
    return response.data
  },

  // Get a specific ad campaign
  async getAdCampaign(campaignId) {
    const response = await api.get(`/ads/${campaignId}`)
    return response.data
  },

  // Get campaign status (for polling)
  async getAdCampaignStatus(campaignId) {
    const response = await api.get(`/ads/${campaignId}/status`)
    return response.data
  },

  // Redo a specific step
  async redoAdCampaignStep(campaignId, step, feedback = null) {
    const response = await api.post(`/ads/${campaignId}/redo`, {
      step,
      feedback
    })
    return response.data
  }
}
