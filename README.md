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
| **Text-to-Image** | Generate high-quality images from text prompts using ZImage Turbo and Flux 2 models |
| **Text-to-Video** | Create cinematic videos directly from text descriptions |
| **Image-to-Video** | Transform static images into dynamic video content |
| **Real-time Progress** | Live progress tracking with visual indicators |
| **Prompt Enhancement** | AI-powered prompt improvement for better results |
| **Gallery View** | Browse, filter, and manage all your generations |
| **Credit Tracking** | Monitor your API balance in real-time |

---

## Screenshots

<div align="center">

| Home Interface | Gallery View |
|:--------------:|:------------:|
| ![Home](docs/screenshots/home.png) | ![Gallery](docs/screenshots/gallery.png) |

</div>

---

## Tech Stack

**Frontend**
- Vue.js 3 with Composition API
- Vite for fast development
- Modern CSS with CSS Variables
- Axios for API communication

**Backend**
- FastAPI for high-performance APIs
- SQLAlchemy ORM with async support
- Pydantic for data validation
- Background task processing

**AI Provider**
- [deAPI](https://deapi.ai) - Decentralized GPU cloud for AI inference

---

## Project Structure

```
Videlo/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── generations.py    # Generation endpoints
│   │   │   └── prompts.py        # Prompt enhancement
│   │   ├── services/
│   │   │   └── deapi.py          # deAPI client
│   │   ├── utils/
│   │   │   └── security.py       # Security utilities
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
│   │   │   ├── ImageCard.vue     # Image/video card
│   │   │   └── ImageModal.vue    # Fullscreen modal
│   │   ├── views/
│   │   │   └── Home.vue          # Main view
│   │   ├── services/
│   │   │   └── api.js            # API client
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
└── docs/
    └── plans/
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- deAPI API Key ([Get one here](https://deapi.ai/dashboard))

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

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

## API Reference

### Generation Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/generate/text2img` | Generate image from text |
| `POST` | `/api/generate/txt2video` | Generate video from text |
| `POST` | `/api/generate/img2video` | Generate video from image |

### Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/generations` | List generations (paginated) |
| `GET` | `/api/generations/{id}` | Get single generation |
| `GET` | `/api/generations/{id}/status` | Poll generation status |
| `GET` | `/api/balance` | Check API balance |
| `GET` | `/api/models` | List available models |

### Utility Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/enhance-prompt` | Enhance prompt with AI |
| `GET` | `/api/random-prompt` | Get random creative prompt |

Interactive API documentation: `http://localhost:8000/docs`

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
| ZImage Turbo | Photorealistic images | Fast |
| Flux 2 Klein | High-quality creative images | Medium |

### Video Models

| Model | Best For | Output |
|-------|----------|--------|
| LTX-2 19B | Cinematic motion | 1-4 seconds |
| LTX-Video 13B | Smooth animations | 1-4 seconds |
| Wan 2.1 T2V | Fast video generation | 1-4 seconds |
| Hunyuan Video | High-quality motion | 1-4 seconds |

---

## Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

Please make sure to update tests as appropriate.

---

## Roadmap

- [ ] WebSocket support for real-time updates
- [ ] Batch generation
- [ ] Custom model fine-tuning
- [ ] Image editing capabilities
- [ ] Social sharing features
- [ ] Mobile app

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [deAPI](https://deapi.ai) for providing affordable AI inference
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [Vue.js](https://vuejs.org/) for the reactive frontend framework

---

<div align="center">

**Built with care by [abhayror17](https://github.com/abhayror17)**

</div>