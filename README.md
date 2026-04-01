<div align="center">

# Videlo

**AI-Powered Media Generation Platform**

Generate stunning images and videos from text prompts using state-of-the-art AI models.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D?style=flat-square&logo=vue.js)](https://vuejs.org/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)

[Live Demo](#) · [Report Bug](https://github.com/abhayror17/Videlo/issues) · [Request Feature](https://github.com/abhayror17/Videlo/issues)

</div>

---

## Overview

Videlo is a modern web application that leverages AI to transform text descriptions into beautiful images and videos. Built with a clean, intuitive interface, it makes AI-powered content creation accessible to everyone.

### Key Features

| Feature | Description |
|---------|-------------|
| **Workflow Canvas** | Visual node-based editor with infinite canvas, zoom controls, drag-and-drop connections, undo/redo, and cut connections |
| **BYOK** | Bring Your Own Key - use your own deAPI key for complete control |
| **Text-to-Image** | Generate high-quality images from text prompts using Flux 2 Klein and ZImage Turbo models |
| **Text-to-Video** | Create cinematic videos directly from text descriptions |
| **Image-to-Video** | Transform static images into dynamic video content |
| **Image Edit** | AI-powered image editing and style transfer with Qwen Image Edit |
| **AI Ads Generator** | Complete ad campaign pipeline with automated script, image, and video generation |
| **AI Avatar** | 3-step pipeline for creating talking AI avatars: portrait, voice, and animation |
| **UGC Ads Creator** | Generate realistic influencer-style video ads with AI-generated scripts and scenes |
| **Multi-language** | English and Chinese language support with easy switching |
| **Real-time Progress** | Live progress tracking with visual indicators |
| **Prompt Enhancement** | AI-powered prompt improvement for better results |
| **Gallery View** | Browse, filter, and manage all your generations |
| **Credit Tracking** | Monitor your API balance (cached for efficiency) |

---

## Tech Stack

**Frontend**
- Vue.js 3 with Composition API
- Vue Router for SPA navigation
- VueFlow for visual workflow canvas
- Vue I18n for internationalization
- Vite for fast development
- Modern CSS with CSS Variables
- Axios for API communication

**Backend**
- FastAPI for high-performance APIs
- SQLAlchemy ORM with async support
- Pydantic for data validation
- Background task processing with polling

**AI Provider**
- [deAPI](https://deapi.ai) - Decentralized GPU cloud for AI inference
- iFlow API - For prompt enhancement and LLM tasks

---

## Project Structure

```
Videlo/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── generations.py    # Generation endpoints (text2img, txt2video, img2video, img2img)
│   │   │   ├── prompts.py        # Prompt enhancement
│   │   │   ├── ads.py            # AI Ads Generator pipeline
│   │   │   ├── avatar.py         # AI Avatar creator endpoints
│   │   │   ├── ugc_ads.py        # UGC Ads Creator endpoints
│   │   │   └── workflow.py       # Workflow canvas execution
│   │   ├── services/
│   │   │   ├── deapi.py          # deAPI client
│   │   │   ├── iflow.py          # iFlow API client
│   │   │   ├── nanobanana.py     # Nanobanana API client
│   │   │   ├── ads_pipeline.py   # Ads generation pipeline
│   │   │   ├── prompt_matcher.py # Prompt matching service
│   │   │   └── ugc_story_generator.py # UGC story generation
│   │   ├── utils/
│   │   │   ├── security.py       # Security utilities
│   │   │   └── media.py          # Media utilities
│   │   ├── config.py             # App configuration
│   │   ├── database.py           # Database setup
│   │   ├── main.py               # FastAPI application
│   │   ├── models.py             # SQLAlchemy models
│   │   └── schemas.py            # Pydantic schemas
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Gallery.vue       # Gallery component
│   │   │   ├── ImageCard.vue     # Image/video card with actions
│   │   │   ├── ImageModal.vue    # Fullscreen modal
│   │   │   ├── StatusBadge.vue   # Status indicator
│   │   │   ├── LanguageSwitcher.vue # Language toggle
│   │   │   ├── WorkflowCanvas.vue   # Visual workflow editor
│   │   │   └── nodes/            # Workflow node components
│   │   │       ├── TextInputNode.vue
│   │   │       ├── ImageGenNode.vue
│   │   │       ├── ImageInputNode.vue
│   │   │       ├── ImageEditNode.vue
│   │   │       ├── ImageEnhanceNode.vue
│   │   │       ├── ImageAnalysisNode.vue
│   │   │       ├── ImageBackgroundRemovalNode.vue
│   │   │       ├── ImageToVideoNode.vue
│   │   │       ├── VideoGenNode.vue
│   │   │       ├── VideoToTextNode.vue
│   │   │       ├── VideoReplaceNode.vue
│   │   │       ├── TextToSpeechNode.vue
│ │ │ ├── StickyNoteNode.vue
│ │ │ ├── AIAssistantNode.vue
│ │ │ ├── ImagePromptEnhancerNode.vue
│ │ │ ├── VideoPromptEnhancerNode.vue
│ │ │ └── OutputNode.vue
│   │   ├── views/
│   │   │   ├── Home.vue          # Main generation view
│   │   │   ├── ImageEdit.vue     # Image editing page
│   │   │   ├── AdGenerator.vue   # AI Ads Generator
│   │   │   ├── ImgGen.vue        # Image Generator
│   │   │   ├── PromptsGallery.vue# Prompts gallery view
│   │   │   ├── Workflow.vue      # Workflow canvas page
│   │   │   ├── AiAvatar.vue      # AI Avatar creator
│   │   │   └── UgcAdsCreator.vue # UGC Ads Creator
│   │   ├── services/
│   │   │   └── api.js            # API client
│   │   ├── i18n/                 # Internationalization
│   │   │   ├── index.js
│   │   │   └── locales/
│   │   │       ├── en.js         # English translations
│   │   │       └── zh.js         # Chinese translations
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── vercel.json                    # Vercel deployment config
├── render.yaml                    # Render deployment config
└── docs/
    └── plans/
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- deAPI API Key ([Get one here](https://deapi.ai))

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your DEAPI_API_KEY

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Access the application at `http://localhost:3000`

---

## API Endpoints

### Generation Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/generate/text2img` | Generate image from text |
| `POST` | `/api/generate/txt2video` | Generate video from text |
| `POST` | `/api/generate/img2video` | Generate video from image |
| `POST` | `/api/generate/img2img` | Edit/transform images |

### Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/generations` | List generations (paginated) |
| `GET` | `/api/generations/{id}` | Get single generation |
| `GET` | `/api/generations/{id}/status` | Poll generation status |
| `GET` | `/api/balance` | Check API balance |
| `GET` | `/api/models` | List available models |

### AI Ads Generator Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/ads/generate` | Start new ad campaign |
| `GET` | `/api/ads` | List ad campaigns |
| `GET` | `/api/ads/{id}` | Get campaign details |
| `GET` | `/api/ads/{id}/status` | Poll campaign status |
| `POST` | `/api/ads/{id}/redo` | Redo a specific step |

### AI Avatar Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/avatar` | Create new avatar project |
| `GET` | `/api/avatar` | List avatar projects |
| `GET` | `/api/avatar/{id}` | Get project details |
| `GET` | `/api/avatar/{id}/status` | Poll generation status |
| `POST` | `/api/avatar/{id}/generate` | Start generation for step(s) |
| `POST` | `/api/avatar/{id}/regenerate` | Regenerate with modified params |
| `DELETE` | `/api/avatar/{id}` | Delete project |

### UGC Ads Creator Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/ugc-ads/prompts/search` | Search prompt library |
| `GET` | `/api/ugc-ads/prompts/{id}` | Get specific prompt |
| `POST` | `/api/ugc-ads/stories` | Create new UGC story |
| `GET` | `/api/ugc-ads/stories` | List stories |
| `GET` | `/api/ugc-ads/stories/{id}` | Get story with scenes/shots |
| `POST` | `/api/ugc-ads/stories/{id}/generate` | Generate images/videos for shots |
| `POST` | `/api/ugc-ads/stories/{id}/shots/regenerate` | Regenerate specific shot |
| `DELETE` | `/api/ugc-ads/stories/{id}` | Delete story |

### Workflow Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/workflow/execute` | Execute workflow graph |
| `GET` | `/api/workflow/status/{id}` | Poll workflow execution status |

### Utility Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/enhance-prompt` | Enhance prompt with AI |
| `GET` | `/api/random-prompt` | Get random creative prompt |

Interactive API documentation: `http://localhost:8000/docs`

---

## Routes

| Route | Description |
|-------|-------------|
| `/text2img` | Text to Image generation (default) |
| `/imgedit` | Image editing and style transfer |
| `/txt2video` | Text to Video generation |
| `/img2video` | Image to Video generation |
| `/ads` | AI Ads Generator |
| `/img-gen` | Image Generator |
| `/prompts-gallery` | Browse prompts gallery |
| `/workflow` | Visual workflow canvas with node-based editor |
| `/ai-avatar` | AI Avatar creator (3-step pipeline) |
| `/ugc-ads` | UGC Ads Creator |
| `/gallery` | Browse all generations |

---

## Workflow Canvas

The Workflow Canvas is a visual node-based editor for creating complex AI pipelines:

### Features
- **Infinite Canvas** - Pan and zoom freely like Excalidraw
- **16 Node Types** - Mix and match to create custom workflows with SVG icons
- **Drag & Connect** - Visual connections between nodes
- **Undo/Redo** - Full history support with Ctrl+Z / Ctrl+Y
- **Cut Connections** - Click the ✕ button on selected node connections to delete them
- **Shortcuts Guide** - Getting Started panel with keyboard shortcuts and tips
- **Quick Actions** - One-click to add connected nodes
- **Auto-Output** - Multiple images automatically create output nodes
- **Caching** - Completed nodes skip re-execution
- **BYOK** - Use your own deAPI key
- **Mobile Responsive** - Touch-friendly interface for tablets and phones

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + Z` | Undo last action |
| `Ctrl + Y` | Redo last undone action |
| `Scroll` | Zoom in/out |
| `Drag` | Pan canvas |
| `Right Click` | Open Add Node menu |
| `Select + Click ✕` | Cut/delete connection |

### Available Nodes

| Node | Input | Output | Description |
|------|-------|--------|-------------|
| **Text Input** | - | Text | Enter text prompts |
| **Image Gen** | Text | Image | Generate images from text |
| **Image Input** | - | Image | Upload images |
| **Image Edit** | Image + Text | Image | Edit images with prompts |
| **Image Enhance** | Image | Image | Enhance image quality |
| **Image Analysis** | Image | Text | Analyze image content (OCR) |
| **Background Removal** | Image | Image | Remove image background |
| **Image to Video** | Image | Video | Animate static images |
| **Video Gen** | Text | Video | Generate videos from text |
| **Video to Text** | Video | Text | Extract text/transcribe video |
| **Video Replace** | Video + Image | Video | Replace faces in videos |
| **Text to Speech** | Text | Audio | Convert text to audio |
| **Sticky Note** | - | - | Add notes and annotations |
| **AI Assistant** | Text | Text | AI-powered text assistance |
| **Image Prompt Enhancer** | Text | Text | Enhance image prompts with AI |
| **Video Prompt Enhancer** | Text | Text | Enhance video prompts with AI |
| **Output** | Any | - | Final output display |

---

## Configuration

### Backend Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DEAPI_API_KEY` | Your deAPI key | Yes | - |
| `DEAPI_BASE_URL` | deAPI base URL | No | `https://api.deapi.ai` |
| `IFLOW_API_KEY` | For prompt enhancement | No | - |
| `ALLOWED_ORIGINS` | CORS origins | No | `*` |
| `DATABASE_URL` | Database connection | No | SQLite |

### Frontend Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `VITE_API_URL` | Backend API URL for production | Yes (prod) |

### BYOK (Bring Your Own Key)

Users can provide their own deAPI key directly in the Workflow Canvas:
1. Click the settings icon (bottom-left)
2. Enter your deAPI key
3. Key is stored locally in browser (localStorage)
4. All workflow requests use your custom key

This allows users to use their own deAPI credits and bypass the shared API key.

---

## Deployment

### Deploy Backend to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Create a new **Web Service** on [Render](https://render.com)
2. Connect your GitHub repository
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend`
4. Add environment variables in Render dashboard

### Deploy Frontend to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

1. Import your GitHub repository
2. Set **Root Directory** to `frontend`
3. Add environment variable:
   - `VITE_API_URL` = `https://your-backend.onrender.com/api`
4. Deploy

---

## Available Models

### Image Models

| Model | Best For | Speed |
|-------|----------|-------|
| Flux 2 Klein | High-quality creative images (default) | Fast |
| ZImage Turbo | Photorealistic images | Very Fast |

### Image Edit Models

| Model | Best For |
|-------|----------|
| Qwen Image Edit | Style transfer and transformations |
| Flux 2 Klein | General image editing |

### Video Models

| Model | Best For | Output |
|-------|----------|--------|
| LTX-2 19B | Cinematic motion (default) | 1-4 seconds |
| LTX-Video 13B | Smooth animations | 1-4 seconds |
| Wan 2.1 T2V | Fast video generation | 1-4 seconds |
| Hunyuan Video | High-quality videos | 1-4 seconds |

---

## AI Ads Generator Pipeline

The AI Ads Generator automates the entire ad creation process:

1. **Prompt Enhancement** - AI improves your ad concept
2. **Script Generation** - Creates compelling ad script with hook and CTA
3. **Image Generation** - Produces brand-aligned imagery
4. **Video Generation** - Transforms image into video ad
5. **QA Review** - Automated quality assessment with recommendations

Each step can be redone with feedback for iterative refinement.

---

## AI Avatar Creator

Create talking AI avatars with a 3-step pipeline:

### Step 1: Generate Portrait
- Text-to-image generation using FLUX-2 Klein
- Customizable model, width, and height
- Multiple style options for different avatar looks

### Step 2: Generate Voice
- Text-to-speech using Kokoro or Chatterbox models
- Multiple voice options and languages
- Adjustable speed settings

### Step 3: Animate
- Audio-to-video animation using LTX-2.3
- Syncs lip movement with generated audio
- Natural head movement and expressions

Each step can be regenerated independently with modified parameters.

---

## UGC Ads Creator

Generate realistic influencer-style video ads:

### Features
- **Prompt Library** - Search and match from marketing prompt library
- **Story Generation** - AI generates complete ad scripts with scenes and shots
- **Character Setup** - Define influencer character details
- **Asset Generation** - Automatic image and video generation for each shot
- **Shot Management** - Regenerate individual shots with custom prompts

### Pipeline
1. Enter product info and character details
2. AI generates story with scenes and shots
3. Review and edit the generated script
4. Generate images and videos for all shots
5. Regenerate individual shots as needed

Supported aspect ratios: 1:1, 16:9, 9:16, 4:3, 3:4, 4:5, 5:4

---

## Performance Optimizations

- **Balance caching**: API balance cached for 5 minutes to reduce unnecessary calls
- **Optimized polling**: 5-second intervals for status checks
- **Single refresh**: Consolidated gallery refresh after generation completion
- **Vue Router**: Client-side navigation for faster page transitions
- **Workflow caching**: Nodes with existing results skip re-execution
- **Fast toast**: Success notifications dismiss after 1 second
- **Asset caching**: Static assets cached for 1 year on Vercel

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**[⬆ Back to Top](#videlo)**

Made with ❤️ by [abhayror17](https://github.com/abhayror17)

</div>
