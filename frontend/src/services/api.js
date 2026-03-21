import axios from 'axios'

// Use environment variable for production, fallback to /api for development (proxied by Vite)
const baseURL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL,
  timeout: 30000
})

// Add custom API key headers if user has provided them (BYOK)
api.interceptors.request.use(config => {
  const customKey = localStorage.getItem('deapi_key')
  if (customKey) {
    config.headers['X-DeAPI-Key'] = customKey
  }
  const iflowKey = localStorage.getItem('iflow_key')
  if (iflowKey) {
    config.headers['X-iFlow-Key'] = iflowKey
  }
  return config
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
      model: options.model || 'Ltx2_3_22B_Dist_INT8',
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
    formData.append('model', options.model || 'Ltx2_3_22B_Dist_INT8')
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
    formData.append('model', options.model || 'Ltx2_3_22B_Dist_INT8')
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
    const response = await api.post('/ads/campaigns', data, {
      timeout: 60000
    })
    return response.data
  },

  // Get list of ad campaigns
  async getAdCampaigns(page = 1, perPage = 10) {
    const response = await api.get('/ads/campaigns', {
      params: { page, per_page: perPage }
    })
    return response.data
  },

  // Get a specific ad campaign
  async getAdCampaign(campaignId) {
    const response = await api.get(`/ads/campaigns/${campaignId}`)
    return response.data
  },

  // Get campaign status (for polling)
  async getAdCampaignStatus(campaignId) {
    const response = await api.get(`/ads/campaigns/${campaignId}`)
    return response.data
  },

  // Get full campaign details with avatars and scripts
  async getAdCampaignDetail(campaignId) {
    const response = await api.get(`/ads/campaigns/${campaignId}/detail`)
    return response.data
  },

  // Phase 2: Submit answers to clarification questions
  async submitAdCampaignAnswers(campaignId, answers) {
    const response = await api.post(`/ads/campaigns/${campaignId}/answers`, {
      answers
    })
    return response.data
  },

  // Phase 4: Generate scripts
  async generateAdScripts(campaignId, options = {}) {
    const response = await api.post(`/ads/campaigns/${campaignId}/scripts`, {
      num_scripts: options.numScripts || 5
    })
    return response.data
  },

  // Phase 5: Generate avatars
  async generateAdAvatars(campaignId, numAvatars = 3) {
    const response = await api.post(`/ads/campaigns/${campaignId}/avatars`, null, {
      params: { num_avatars: numAvatars }
    })
    return response.data
  },

  // Phase 6-8: Generate storyboards and prompts
  async generateAdStoryboards(campaignId) {
    const response = await api.post(`/ads/campaigns/${campaignId}/storyboards`)
    return response.data
  },

  async generateAdImagePrompts(campaignId) {
    const response = await api.post(`/ads/campaigns/${campaignId}/image-prompts`)
    return response.data
  },

  async generateAdVideoPrompts(campaignId) {
    const response = await api.post(`/ads/campaigns/${campaignId}/video-prompts`)
    return response.data
  },

  // Phase 9: Get batch output
  async getAdCampaignBatch(campaignId) {
    const response = await api.get(`/ads/campaigns/${campaignId}/batch`)
    return response.data
  },

  // Convenience: Generate all remaining phases
  async generateAllAdCampaign(campaignId, options = {}) {
    const response = await api.post(`/ads/campaigns/${campaignId}/generate-all`, null, {
      params: {
        num_scripts: options.numScripts || 5,
        num_avatars: options.numAvatars || 3
      },
      timeout: 120000
    })
    return response.data
  },

  // Phase 10: Iteration mode
  async iterateAdCampaign(campaignId, command, target = null) {
    const response = await api.post(`/ads/campaigns/${campaignId}/iterate`, {
      command,
      target
    })
    return response.data
  },

  // Redo a specific step (uses iteration mode)
  async redoAdCampaignStep(campaignId, step, feedback = null) {
    const command = feedback || `regenerate ${step}`
    const response = await api.post(`/ads/campaigns/${campaignId}/iterate`, {
      command,
      target: step
    })
    return response.data
  },

  // Redo/restart from a specific phase
  async redoCampaignPhase(campaignId, phase) {
    const response = await api.post(`/ads/campaigns/${campaignId}/redo/${phase}`, null, {
      timeout: 120000
    })
    return response.data
  },

  // Get debug logs for a campaign
  async getAdCampaignDebugLogs(campaignId) {
    const response = await api.get(`/ads/campaigns/${campaignId}/debug-logs`)
    return response.data
  },

  // Update campaign input (prompt, brand, answers)
  async updateAdCampaignInput(campaignId, data) {
    const response = await api.put(`/ads/campaigns/${campaignId}/input`, null, {
      params: data
    })
    return response.data
  },

  // Text-to-Speech API
  async generateTxt2Audio(text, options = {}) {
    const formData = new FormData()
    formData.append('text', text)
    formData.append('model', options.model || 'Kokoro')
    formData.append('lang', options.lang || 'en-us')
    formData.append('speed', options.speed || 1)
    formData.append('format', options.format || 'flac')
    formData.append('sample_rate', options.sampleRate || 24000)
    formData.append('mode', options.mode || 'custom_voice')
    
    if (options.voice) {
      formData.append('voice', options.voice)
    }
    if (options.refAudio) {
      formData.append('ref_audio', options.refAudio)
    }
    if (options.refText) {
      formData.append('ref_text', options.refText)
    }
    if (options.instruct) {
      formData.append('instruct', options.instruct)
    }

    const response = await api.post('/generate/txt2audio', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 60000
    })
    return response.data
  },

  // Graph/Workflow execution APIs
  async executeGraph(graphData) {
    const response = await api.post('/workflow/execute', graphData, {
      timeout: 30000
    })
    return response.data
  },

  // Get graph execution status
  async getGraphExecution(executionId) {
    const response = await api.get(`/workflow/executions/${executionId}`)
    return response.data
  },

  // Save workflow
  async saveWorkflow(name, nodes, edges, description = null) {
    const response = await api.post('/workflow/save', {
      name,
      description,
      nodes,
      edges
    })
    return response.data
  },

  // List saved workflows
  async listWorkflows() {
    const response = await api.get('/workflow/saved')
    return response.data
  },

  // Get saved workflow
  async getWorkflow(workflowId) {
    const response = await api.get(`/workflow/saved/${workflowId}`)
    return response.data
  },

  // Update workflow
  async updateWorkflow(workflowId, name, nodes, edges, description = null) {
    const response = await api.put(`/workflow/saved/${workflowId}`, {
      name,
      description,
      nodes,
      edges
    })
    return response.data
  },

  // Delete workflow
  async deleteWorkflow(workflowId) {
    const response = await api.delete(`/workflow/saved/${workflowId}`)
    return response.data
  },

  // ============================================================
  // NANOBANANA IMAGE GENERATION (Free/Guest Mode)
  // ============================================================

  // Generate image with NanoBanana (free, no credits required)
  async generateNanoBanana(data) {
    const response = await api.post('/generate/nanobanana', {
      prompt: data.prompt,
      model: data.model || 'nano-banana-2',
      aspect_ratio: data.aspect_ratio || '1:1',
      reference_images: data.reference_images || null
    }, {
      timeout: 150000 // 2.5 minutes timeout
    })
    return response.data
  },

  // Start NanoBanana generation (async, returns task ID)
  async startNanoBanana(data) {
    const response = await api.post('/generate/nanobanana/start', {
      prompt: data.prompt,
      model: data.model || 'nano-banana-2',
      aspect_ratio: data.aspect_ratio || '1:1',
      reference_images: data.reference_images || null
    })
    return response.data
  },

  // Query NanoBanana task status
  async queryNanoBanana(taskId, prompt) {
    const formData = new FormData()
    formData.append('task_id', taskId)
    formData.append('prompt', prompt)
    
    const response = await api.post('/generate/nanobanana/query', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }
}
