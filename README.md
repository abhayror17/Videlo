# Videlo

Text-to-Image and Image-to-Video Generation API using deAI. A modern web application for AI-powered media generation with a Vue.js frontend and FastAPI backend.

## Features

- **Text-to-Image Generation** - Generate images from text prompts using AI models
- **Text-to-Video Generation** - Create videos directly from text descriptions
- **Image-to-Video Generation** - Transform images into animated videos
- **Prompt Enhancement** - AI-powered prompt improvement
- **Gallery View** - Browse and manage your generations
- **Real-time Status Polling** - Track generation progress live

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Python 3.11
- **Frontend**: Vue.js 3, Vite, Axios
- **Database**: SQLite
- **AI Provider**: [deAPI](https://api.deapi.ai)

## Project Structure

```
Videlo/
├── backend/
│   ├── app/
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # External API integrations
│   │   ├── models.py        # Database models
│   │   ├── schemas.py       # Pydantic schemas
│   │   └── main.py          # FastAPI app
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/      # Vue components
│   │   ├── views/           # Page views
│   │   └── services/        # API client
│   ├── package.json
│   └── vite.config.js
└── docs/
    └── plans/
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- deAPI API Key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
copy .env.example .env
# Edit .env and add your DEAPI_API_KEY

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The app will be available at `http://localhost:3000`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/generate/text2img` | POST | Generate image from text |
| `/api/generate/txt2video` | POST | Generate video from text |
| `/api/generate/img2video` | POST | Generate video from image |
| `/api/generations` | GET | List all generations |
| `/api/generations/{id}` | GET | Get single generation |
| `/api/generations/{id}/status` | GET | Get generation status |
| `/api/balance` | GET | Check API balance |
| `/api/models` | GET | List available models |
| `/api/health` | GET | Health check |
| `/api/enhance-prompt` | POST | Enhance a prompt |
| `/api/random-prompt` | GET | Get random prompt |

API documentation available at `http://localhost:8000/docs`

## Environment Variables

### Backend

| Variable | Description | Default |
|----------|-------------|---------|
| `DEAPI_API_KEY` | deAPI API key | Required |
| `DEAPI_BASE_URL` | deAPI base URL | `https://api.deapi.ai` |
| `IFLOW_API_KEY` | iFlow API key (prompt enhancement) | Optional |
| `ALLOWED_ORIGINS` | CORS origins (comma-separated) | `*` |
| `DATABASE_URL` | Database connection URL | `sqlite:///./videlo.db` |

## Deployment

### Render (Backend)

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in Render dashboard

### Vercel (Frontend)

1. Import project from GitHub
2. Set root directory to `frontend`
3. Update API base URL in `src/services/api.js` for production

## License

MIT
