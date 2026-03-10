# Videlo Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a text-to-image web application using Geminigen AI API with webhook support and history gallery.

**Architecture:** FastAPI backend handles image generation requests, webhooks, and serves Vue.js SPA. SQLite stores generation metadata. Webhook mode for production, polling fallback for local development.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy, Pydantic, Vue.js 3, Vite, Axios

---

## Phase 1: Backend Foundation

### Task 1: Project Setup

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `backend/app/__init__.py`

**Step 1: Create backend directory structure**

Run: `mkdir -p backend/app/routes backend/app/services backend/app/utils`

**Step 2: Create requirements.txt**

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
pydantic==2.5.3
pydantic-settings==2.1.0
httpx==0.26.0
python-multipart==0.0.6
cryptography==42.0.0
aiofiles==23.2.1
```

**Step 3: Create .env.example**

```env
GEMINIGEN_API_KEY=your_api_key_here
GEMINIGEN_API_BASE_URL=https://api.geminigen.ai/uapi/v1
USE_WEBHOOK=false
WEBHOOK_URL=http://localhost:8000/webhook/geminigen
PUBLIC_KEY_PATH=../uapi_public_key.pem
DATABASE_URL=sqlite:///./videlo.db
```

**Step 4: Create app/__init__.py**

```python
# Videlo Backend Application
```

---

### Task 2: Configuration Module

**Files:**
- Create: `backend/app/config.py`

**Step 1: Write config.py**

```python
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    geminigen_api_key: str
    geminigen_api_base_url: str = "https://api.geminigen.ai/uapi/v1"
    use_webhook: bool = False
    webhook_url: str = "http://localhost:8000/webhook/geminigen"
    public_key_path: str = "../uapi_public_key.pem"
    database_url: str = "sqlite:///./videlo.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

---

### Task 3: Database Setup

**Files:**
- Create: `backend/app/database.py`
- Create: `backend/app/models.py`

**Step 1: Write database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}  # SQLite specific
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
```

**Step 2: Write models.py**

```python
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from .database import Base


class Generation(Base):
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True, nullable=True)
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    model = Column(String, default="nano-banana-pro")
    status = Column(String, default="pending")  # pending, processing, completed, failed
    remote_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
```

---

### Task 4: Pydantic Schemas

**Files:**
- Create: `backend/app/schemas.py`

**Step 1: Write schemas.py**

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class GenerationCreate(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    model: str = "nano-banana-pro"
    aspect_ratio: str = "16:9"
    style: str = "Photorealistic"
    output_format: str = "jpeg"
    resolution: str = "1K"


class GenerationResponse(BaseModel):
    id: int
    uuid: Optional[str] = None
    prompt: str
    negative_prompt: Optional[str] = None
    model: str
    status: str
    remote_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GenerationListResponse(BaseModel):
    items: list[GenerationResponse]
    total: int
    page: int
    pages: int


class WebhookPayload(BaseModel):
    event_uuid: str
    signature: str
    data: dict


class HealthResponse(BaseModel):
    status: str
    database: str
```

---

### Task 5: Security Utils

**Files:**
- Create: `backend/app/utils/__init__.py`
- Create: `backend/app/utils/security.py`

**Step 1: Write utils/__init__.py**

```python
# Utils module
```

**Step 2: Write utils/security.py**

```python
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from hashlib import md5
from pathlib import Path


def verify_webhook_signature(event_uuid: str, signature_hex: str, public_key_path: str) -> bool:
    """
    Verify webhook signature using RSA public key.
    
    Args:
        event_uuid: The event UUID from the webhook
        signature_hex: The signature in hex format
        public_key_path: Path to the public key PEM file
    
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Load public key
        key_path = Path(public_key_path)
        if not key_path.exists():
            return False
            
        with open(key_path, "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
        
        # Create MD5 hash of the event UUID
        event_data_hash = md5(event_uuid.encode()).digest()
        
        # Convert hex signature to bytes
        signature_bytes = bytes.fromhex(signature_hex)
        
        # Verify the signature
        public_key.verify(
            signature_bytes,
            event_data_hash,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        print(f"Signature verification failed: {e}")
        return False
```

---

### Task 6: Geminigen API Client

**Files:**
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/geminigen.py`

**Step 1: Write services/__init__.py**

```python
# Services module
```

**Step 2: Write services/geminigen.py**

```python
import httpx
from typing import Optional
from ..config import get_settings

settings = get_settings()


class GeminigenClient:
    def __init__(self):
        self.base_url = settings.geminigen_api_base_url
        self.api_key = settings.geminigen_api_key
        self.headers = {"x-api-key": self.api_key}
    
    async def generate_image(
        self,
        prompt: str,
        model: str = "nano-banana-pro",
        aspect_ratio: str = "16:9",
        style: str = "Photorealistic",
        output_format: str = "jpeg",
        resolution: str = "1K",
        file_urls: Optional[str] = None
    ) -> dict:
        """Submit image generation request to Geminigen API."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            data = {
                "prompt": prompt,
                "model": model,
                "aspect_ratio": aspect_ratio,
                "style": style,
                "output_format": output_format,
                "resolution": resolution,
            }
            if file_urls:
                data["file_urls"] = file_urls
            
            response = await client.post(
                f"{self.base_url}/generate_image",
                headers=self.headers,
                data=data
            )
            response.raise_for_status()
            return response.json()
    
    async def get_history(
        self,
        page: int = 1,
        items_per_page: int = 10,
        filter_by: str = "all"
    ) -> dict:
        """Fetch generation history from Geminigen API."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/histories",
                headers=self.headers,
                params={
                    "page": page,
                    "items_per_page": items_per_page,
                    "filter_by": filter_by
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_generation_by_uuid(self, uuid: str) -> Optional[dict]:
        """Find a specific generation by UUID in history."""
        # Search through history to find the generation
        page = 1
        while page <= 10:  # Limit search to 10 pages
            history = await self.get_history(page=page, items_per_page=50)
            items = history.get("data", {}).get("items", [])
            for item in items:
                if item.get("uuid") == uuid:
                    return item
            if len(items) < 50:
                break
            page += 1
        return None


# Singleton client
_client: Optional[GeminigenClient] = None


def get_geminigen_client() -> GeminigenClient:
    global _client
    if _client is None:
        _client = GeminigenClient()
    return _client
```

---

### Task 7: Generations Routes

**Files:**
- Create: `backend/app/routes/__init__.py`
- Create: `backend/app/routes/generations.py`

**Step 1: Write routes/__init__.py**

```python
# Routes module
```

**Step 2: Write routes/generations.py**

```python
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from math import ceil

from ..database import get_db
from ..models import Generation
from ..schemas import (
    GenerationCreate,
    GenerationResponse,
    GenerationListResponse,
    HealthResponse
)
from ..services.geminigen import get_geminigen_client
from ..config import get_settings

router = APIRouter(prefix="/api", tags=["generations"])
settings = get_settings()


async def poll_for_result(uuid: str, generation_id: int):
    """Background task to poll for generation result (dev mode)."""
    import asyncio
    from ..database import SessionLocal
    
    client = get_geminigen_client()
    
    for _ in range(60):  # Poll for up to 5 minutes
        await asyncio.sleep(5)
        
        db = SessionLocal()
        try:
            result = await client.get_generation_by_uuid(uuid)
            if result and result.get("status") == 2:  # Completed
                generation = db.query(Generation).filter(
                    Generation.id == generation_id
                ).first()
                if generation:
                    generation.status = "completed"
                    generation.remote_url = result.get("generate_result")
                    generation.thumbnail_url = result.get("thumbnail_small")
                    generation.file_size = result.get("file_size")
                    from datetime import datetime
                    generation.completed_at = datetime.utcnow()
                    db.commit()
                return
            elif result and result.get("status") == 3:  # Failed
                generation = db.query(Generation).filter(
                    Generation.id == generation_id
                ).first()
                if generation:
                    generation.status = "failed"
                    generation.error_message = result.get("error_message", "Generation failed")
                    db.commit()
                return
        finally:
            db.close()


@router.post("/generate", response_model=GenerationResponse)
async def create_generation(
    request: GenerationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit a new image generation request."""
    client = get_geminigen_client()
    
    # Create pending record
    generation = Generation(
        prompt=request.prompt,
        negative_prompt=request.negative_prompt,
        model=request.model,
        status="pending"
    )
    db.add(generation)
    db.commit()
    db.refresh(generation)
    
    try:
        # Call Geminigen API
        result = await client.generate_image(
            prompt=request.prompt,
            model=request.model,
            aspect_ratio=request.aspect_ratio,
            style=request.style,
            output_format=request.output_format,
            resolution=request.resolution
        )
        
        # Update with UUID
        generation.uuid = result.get("uuid")
        generation.status = "processing"
        db.commit()
        db.refresh(generation)
        
        # If not using webhooks, start polling
        if not settings.use_webhook:
            background_tasks.add_task(
                poll_for_result,
                generation.uuid,
                generation.id
            )
        
        return generation
        
    except Exception as e:
        generation.status = "failed"
        generation.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generations", response_model=GenerationListResponse)
async def list_generations(
    page: int = 1,
    per_page: int = 12,
    db: Session = Depends(get_db)
):
    """List all generations with pagination."""
    offset = (page - 1) * per_page
    
    total = db.query(Generation).count()
    generations = db.query(Generation).order_by(
        Generation.created_at.desc()
    ).offset(offset).limit(per_page).all()
    
    return GenerationListResponse(
        items=[GenerationResponse.model_validate(g) for g in generations],
        total=total,
        page=page,
        pages=ceil(total / per_page) if total > 0 else 1
    )


@router.get("/generations/{generation_id}", response_model=GenerationResponse)
async def get_generation(
    generation_id: int,
    db: Session = Depends(get_db)
):
    """Get a single generation by ID."""
    generation = db.query(Generation).filter(
        Generation.id == generation_id
    ).first()
    
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    return generation


@router.get("/generations/{generation_id}/status", response_model=GenerationResponse)
async def get_generation_status(
    generation_id: int,
    db: Session = Depends(get_db)
):
    """Get the current status of a generation (for polling)."""
    generation = db.query(Generation).filter(
        Generation.id == generation_id
    ).first()
    
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    return generation


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    return HealthResponse(status="ok", database=db_status)
```

---

### Task 8: Webhook Route

**Files:**
- Create: `backend/app/routes/webhook.py`

**Step 1: Write routes/webhook.py**

```python
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from ..models import Generation
from ..utils.security import verify_webhook_signature
from ..config import get_settings

router = APIRouter(tags=["webhook"])
settings = get_settings()


@router.post("/webhook/geminigen")
async def handle_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle webhook callback from Geminigen API."""
    # Parse the webhook payload
    body = await request.json()
    
    event_uuid = body.get("event_uuid")
    signature = body.get("signature")
    data = body.get("data", {})
    
    # Verify signature
    if settings.use_webhook:
        if not event_uuid or not signature:
            raise HTTPException(status_code=400, detail="Missing event_uuid or signature")
        
        if not verify_webhook_signature(
            event_uuid,
            signature,
            settings.public_key_path
        ):
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Find the generation by UUID
    generation_uuid = data.get("uuid")
    if not generation_uuid:
        raise HTTPException(status_code=400, detail="Missing UUID in data")
    
    generation = db.query(Generation).filter(
        Generation.uuid == generation_uuid
    ).first()
    
    if not generation:
        # Generation not found, might be from a different source
        return {"status": "ignored", "reason": "generation not found"}
    
    # Update generation status
    status_map = {
        1: "processing",
        2: "completed",
        3: "failed"
    }
    
    remote_status = data.get("status")
    generation.status = status_map.get(remote_status, "processing")
    
    if generation.status == "completed":
        generation.remote_url = data.get("generate_result")
        generation.thumbnail_url = data.get("thumbnail_small")
        generation.file_size = data.get("file_size")
        generation.completed_at = datetime.utcnow()
    elif generation.status == "failed":
        generation.error_message = data.get("error_message", "Generation failed")
    
    db.commit()
    
    return {"status": "success", "generation_id": generation.id}
```

---

### Task 9: Main Application

**Files:**
- Create: `backend/app/main.py`
- Create: `backend/app/.env` (copy from .env.example)

**Step 1: Write main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .database import init_db
from .routes import generations, webhook

# Create FastAPI app
app = FastAPI(
    title="Videlo API",
    description="Text-to-Image Generation API using Geminigen AI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generations.router)
app.include_router(webhook.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Videlo API", "docs": "/docs"}
```

**Step 2: Create .env file**

Copy .env.example to .env and add your API key:
```bash
cp backend/.env.example backend/.env
```

Then edit backend/.env:
```env
GEMINIGEN_API_KEY=<your_actual_api_key>
GEMINIGEN_API_BASE_URL=https://api.geminigen.ai/uapi/v1
USE_WEBHOOK=false
WEBHOOK_URL=http://localhost:8000/webhook/geminigen
PUBLIC_KEY_PATH=../uapi_public_key (1).pem
DATABASE_URL=sqlite:///./videlo.db
```

---

## Phase 2: Frontend

### Task 10: Frontend Setup

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`

**Step 1: Create frontend directory and initialize**

Run: 
```bash
cd frontend
npm init -y
```

**Step 2: Update package.json**

```json
{
  "name": "videlo-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

**Step 3: Install dependencies**

Run: 
```bash
cd frontend
npm install
```

**Step 4: Create vite.config.js**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/webhook': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

**Step 5: Create index.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Videlo - Text to Image</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

---

### Task 11: Frontend Entry Point

**Files:**
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`

**Step 1: Create src directory**

Run: `mkdir -p frontend/src/components frontend/src/views frontend/src/services`

**Step 2: Create main.js**

```javascript
import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')
```

**Step 3: Create App.vue**

```vue
<template>
  <div id="app">
    <header class="header">
      <h1 class="logo">Videlo</h1>
      <p class="tagline">Transform text into stunning images</p>
    </header>
    <main class="main">
      <Home />
    </main>
  </div>
</template>

<script>
import Home from './views/Home.vue'

export default {
  name: 'App',
  components: {
    Home
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  min-height: 100vh;
  color: #fff;
}

#app {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  padding: 40px 0;
}

.logo {
  font-size: 3rem;
  font-weight: 700;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.tagline {
  color: #a0a0a0;
  margin-top: 10px;
  font-size: 1.1rem;
}

.main {
  padding: 20px 0;
}
</style>
```

---

### Task 12: API Service

**Files:**
- Create: `frontend/src/services/api.js`

**Step 1: Create api.js**

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

export default {
  // Generate image
  async generate(prompt, options = {}) {
    const response = await api.post('/generate', {
      prompt,
      negative_prompt: options.negativePrompt,
      model: options.model || 'nano-banana-pro',
      aspect_ratio: options.aspectRatio || '16:9',
      style: options.style || 'Photorealistic',
      output_format: options.outputFormat || 'jpeg',
      resolution: options.resolution || '1K'
    })
    return response.data
  },

  // List generations
  async getGenerations(page = 1, perPage = 12) {
    const response = await api.get('/generations', {
      params: { page, per_page: perPage }
    })
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

  // Health check
  async health() {
    const response = await api.get('/health')
    return response.data
  }
}
```

---

### Task 13: Vue Components

**Files:**
- Create: `frontend/src/views/Home.vue`
- Create: `frontend/src/components/PromptForm.vue`
- Create: `frontend/src/components/Gallery.vue`
- Create: `frontend/src/components/ImageCard.vue`
- Create: `frontend/src/components/StatusBadge.vue`
- Create: `frontend/src/components/ImageModal.vue`

**Step 1: Create StatusBadge.vue**

```vue
<template>
  <span :class="['status-badge', status]">
    {{ statusText }}
  </span>
</template>

<script>
export default {
  name: 'StatusBadge',
  props: {
    status: {
      type: String,
      required: true
    }
  },
  computed: {
    statusText() {
      const texts = {
        pending: 'Pending',
        processing: 'Processing...',
        completed: 'Completed',
        failed: 'Failed'
      }
      return texts[this.status] || this.status
    }
  }
}
</script>

<style scoped>
.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.pending {
  background: #ffeeba;
  color: #856404;
}

.status-badge.processing {
  background: #b8daff;
  color: #004085;
  animation: pulse 1.5s infinite;
}

.status-badge.completed {
  background: #c3e6cb;
  color: #155724;
}

.status-badge.failed {
  background: #f5c6cb;
  color: #721c24;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
</style>
```

**Step 2: Create ImageCard.vue**

```vue
<template>
  <div class="image-card" @click="$emit('click')">
    <div class="image-container">
      <img
        v-if="generation.thumbnail_url || generation.remote_url"
        :src="generation.thumbnail_url || generation.remote_url"
        :alt="generation.prompt"
        @error="handleImageError"
      />
      <div v-else class="placeholder">
        <span v-if="generation.status === 'processing'" class="spinner"></span>
        <span v-else>No Image</span>
      </div>
    </div>
    <div class="card-content">
      <StatusBadge :status="generation.status" />
      <p class="prompt">{{ truncatedPrompt }}</p>
      <span class="date">{{ formattedDate }}</span>
    </div>
  </div>
</template>

<script>
import StatusBadge from './StatusBadge.vue'

export default {
  name: 'ImageCard',
  components: { StatusBadge },
  props: {
    generation: {
      type: Object,
      required: true
    }
  },
  emits: ['click'],
  computed: {
    truncatedPrompt() {
      if (this.generation.prompt.length > 60) {
        return this.generation.prompt.substring(0, 60) + '...'
      }
      return this.generation.prompt
    },
    formattedDate() {
      return new Date(this.generation.created_at).toLocaleDateString()
    }
  },
  methods: {
    handleImageError(e) {
      e.target.style.display = 'none'
      e.target.parentElement.innerHTML = '<div class="placeholder"><span>Image Expired</span></div>'
    }
  }
}
</script>

<style scoped>
.image-card {
  background: #2a2a4a;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.image-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

.image-container {
  width: 100%;
  aspect-ratio: 16/9;
  overflow: hidden;
  background: #1a1a2e;
}

.image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #333;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.card-content {
  padding: 16px;
}

.prompt {
  color: #fff;
  font-size: 0.9rem;
  margin: 10px 0;
  line-height: 1.4;
}

.date {
  color: #666;
  font-size: 0.75rem;
}
</style>
```

**Step 3: Create Gallery.vue**

```vue
<template>
  <div class="gallery">
    <h2 class="section-title">Your Creations</h2>
    
    <div v-if="loading" class="loading">
      <span class="spinner"></span>
      <p>Loading gallery...</p>
    </div>
    
    <div v-else-if="generations.length === 0" class="empty">
      <p>No images yet. Start creating!</p>
    </div>
    
    <div v-else class="grid">
      <ImageCard
        v-for="gen in generations"
        :key="gen.id"
        :generation="gen"
        @click="$emit('select', gen)"
      />
    </div>
    
    <div v-if="generations.length > 0" class="pagination">
      <button
        :disabled="page === 1"
        @click="changePage(page - 1)"
        class="page-btn"
      >
        Previous
      </button>
      <span class="page-info">Page {{ page }} of {{ totalPages }}</span>
      <button
        :disabled="page >= totalPages"
        @click="changePage(page + 1)"
        class="page-btn"
      >
        Next
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
  emits: ['select'],
  data() {
    return {
      generations: [],
      loading: true,
      page: 1,
      totalPages: 1
    }
  },
  async mounted() {
    await this.loadGenerations()
  },
  methods: {
    async loadGenerations() {
      this.loading = true
      try {
        const response = await api.getGenerations(this.page)
        this.generations = response.items
        this.totalPages = response.pages
      } catch (error) {
        console.error('Failed to load generations:', error)
      } finally {
        this.loading = false
      }
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
  margin-top: 40px;
}

.section-title {
  font-size: 1.5rem;
  margin-bottom: 20px;
  color: #fff;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.loading, .empty {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.loading .spinner {
  display: inline-block;
  width: 40px;
  height: 40px;
  border: 3px solid #333;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 30px;
}

.page-btn {
  padding: 10px 20px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: opacity 0.2s;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #a0a0a0;
}
</style>
```

**Step 4: Create PromptForm.vue**

```vue
<template>
  <div class="prompt-form">
    <div class="form-container">
      <textarea
        v-model="prompt"
        placeholder="Describe the image you want to create..."
        rows="3"
        class="prompt-input"
      ></textarea>
      
      <div class="options">
        <select v-model="model" class="select">
          <option value="nano-banana-pro">Nano Banana Pro</option>
        </select>
        
        <select v-model="aspectRatio" class="select">
          <option value="1:1">Square (1:1)</option>
          <option value="16:9">Landscape (16:9)</option>
          <option value="9:16">Portrait (9:16)</option>
          <option value="4:3">Standard (4:3)</option>
        </select>
        
        <select v-model="style" class="select">
          <option value="Photorealistic">Photorealistic</option>
          <option value="Artistic">Artistic</option>
          <option value="Anime">Anime</option>
          <option value="Digital Art">Digital Art</option>
          <option value="Oil Painting">Oil Painting</option>
        </select>
      </div>
      
      <button
        @click="handleGenerate"
        :disabled="!prompt.trim() || generating"
        class="generate-btn"
      >
        <span v-if="generating" class="btn-spinner"></span>
        <span v-else>Generate Image</span>
      </button>
    </div>
  </div>
</template>

<script>
import api from '../services/api.js'

export default {
  name: 'PromptForm',
  emits: ['generated'],
  data() {
    return {
      prompt: '',
      model: 'nano-banana-pro',
      aspectRatio: '16:9',
      style: 'Photorealistic',
      generating: false
    }
  },
  methods: {
    async handleGenerate() {
      if (!this.prompt.trim() || this.generating) return
      
      this.generating = true
      try {
        const result = await api.generate(this.prompt, {
          model: this.model,
          aspectRatio: this.aspectRatio,
          style: this.style
        })
        
        this.$emit('generated', result)
        this.prompt = ''
      } catch (error) {
        console.error('Generation failed:', error)
        alert('Failed to generate image. Please try again.')
      } finally {
        this.generating = false
      }
    }
  }
}
</script>

<style scoped>
.prompt-form {
  background: #2a2a4a;
  border-radius: 16px;
  padding: 24px;
}

.form-container {
  max-width: 800px;
  margin: 0 auto;
}

.prompt-input {
  width: 100%;
  padding: 16px;
  border: 2px solid #3a3a5a;
  border-radius: 12px;
  background: #1a1a2e;
  color: #fff;
  font-size: 1rem;
  resize: vertical;
  transition: border-color 0.2s;
}

.prompt-input:focus {
  outline: none;
  border-color: #667eea;
}

.prompt-input::placeholder {
  color: #666;
}

.options {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  flex-wrap: wrap;
}

.select {
  flex: 1;
  min-width: 150px;
  padding: 12px 16px;
  border: 2px solid #3a3a5a;
  border-radius: 8px;
  background: #1a1a2e;
  color: #fff;
  font-size: 0.9rem;
  cursor: pointer;
}

.select:focus {
  outline: none;
  border-color: #667eea;
}

.generate-btn {
  width: 100%;
  margin-top: 20px;
  padding: 16px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
```

**Step 5: Create ImageModal.vue**

```vue
<template>
  <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <button class="close-btn" @click="$emit('close')">&times;</button>
      
      <div class="modal-image">
        <img
          v-if="generation.remote_url"
          :src="generation.remote_url"
          :alt="generation.prompt"
        />
        <div v-else class="no-image">Image not available</div>
      </div>
      
      <div class="modal-info">
        <h3>Prompt</h3>
        <p>{{ generation.prompt }}</p>
        
        <div class="meta">
          <div class="meta-item">
            <strong>Status:</strong>
            <StatusBadge :status="generation.status" />
          </div>
          <div class="meta-item">
            <strong>Model:</strong> {{ generation.model }}
          </div>
          <div class="meta-item">
            <strong>Created:</strong> {{ formattedDate }}
          </div>
        </div>
        
        <a
          v-if="generation.remote_url"
          :href="generation.remote_url"
          target="_blank"
          class="download-btn"
        >
          Open Full Image
        </a>
      </div>
    </div>
  </div>
</template>

<script>
import StatusBadge from './StatusBadge.vue'

export default {
  name: 'ImageModal',
  components: { StatusBadge },
  props: {
    visible: Boolean,
    generation: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['close'],
  computed: {
    formattedDate() {
      if (!this.generation.created_at) return ''
      return new Date(this.generation.created_at).toLocaleString()
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  background: #2a2a4a;
  border-radius: 16px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow: auto;
  position: relative;
}

.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  font-size: 24px;
  border-radius: 50%;
  cursor: pointer;
  z-index: 10;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.7);
}

.modal-image {
  width: 100%;
  background: #1a1a2e;
}

.modal-image img {
  width: 100%;
  height: auto;
  max-height: 60vh;
  object-fit: contain;
}

.no-image {
  padding: 100px 20px;
  text-align: center;
  color: #666;
}

.modal-info {
  padding: 24px;
}

.modal-info h3 {
  color: #667eea;
  margin-bottom: 8px;
}

.modal-info p {
  color: #fff;
  line-height: 1.6;
  margin-bottom: 20px;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #a0a0a0;
}

.download-btn {
  display: inline-block;
  padding: 12px 24px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  transition: transform 0.2s;
}

.download-btn:hover {
  transform: translateY(-2px);
}
</style>
```

**Step 6: Create Home.vue**

```vue
<template>
  <div class="home">
    <PromptForm @generated="handleGenerated" />
    <Gallery ref="gallery" @select="openModal" />
    <ImageModal
      :visible="modalVisible"
      :generation="selectedGeneration"
      @close="closeModal"
    />
  </div>
</template>

<script>
import PromptForm from '../components/PromptForm.vue'
import Gallery from '../components/Gallery.vue'
import ImageModal from '../components/ImageModal.vue'
import api from '../services/api.js'

export default {
  name: 'Home',
  components: {
    PromptForm,
    Gallery,
    ImageModal
  },
  data() {
    return {
      modalVisible: false,
      selectedGeneration: {},
      pollingIds: {}
    }
  },
  methods: {
    async handleGenerated(generation) {
      // Refresh gallery
      this.$refs.gallery.refresh()
      
      // Start polling for status updates
      if (generation.status === 'processing' || generation.status === 'pending') {
        this.startPolling(generation.id)
      }
    },
    
    startPolling(generationId) {
      // Poll every 3 seconds for status updates
      const pollId = setInterval(async () => {
        try {
          const updated = await api.getStatus(generationId)
          
          if (updated.status === 'completed' || updated.status === 'failed') {
            this.stopPolling(generationId)
            this.$refs.gallery.refresh()
          }
        } catch (error) {
          console.error('Polling error:', error)
          this.stopPolling(generationId)
        }
      }, 3000)
      
      this.pollingIds[generationId] = pollId
      
      // Stop polling after 5 minutes
      setTimeout(() => this.stopPolling(generationId), 5 * 60 * 1000)
    },
    
    stopPolling(generationId) {
      if (this.pollingIds[generationId]) {
        clearInterval(this.pollingIds[generationId])
        delete this.pollingIds[generationId]
      }
    },
    
    openModal(generation) {
      this.selectedGeneration = generation
      this.modalVisible = true
    },
    
    closeModal() {
      this.modalVisible = false
      this.selectedGeneration = {}
    }
  }
}
</script>

<style scoped>
.home {
  padding-bottom: 40px;
}
</style>
```

---

## Phase 3: Final Setup

### Task 14: Move Public Key

**Files:**
- Move: `uapi_public_key (1).pem` to `backend/uapi_public_key.pem`

**Step 1: Move the public key file**

Run:
```bash
move "C:\Users\abhay\Downloads\PROJ\Videlo\uapi_public_key (1).pem" "C:\Users\abhay\Downloads\PROJ\Videlo\backend\uapi_public_key.pem"
```

---

### Task 15: Run and Test

**Step 1: Start the backend**

Run:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Step 2: Start the frontend (new terminal)**

Run:
```bash
cd frontend
npm run dev
```

**Step 3: Test the application**

1. Open browser to http://localhost:3000
2. Enter a prompt and click "Generate Image"
3. Wait for the image to appear in the gallery
4. Click on an image to view details

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| 1 | 1-9 | Backend API with FastAPI |
| 2 | 10-13 | Vue.js Frontend SPA |
| 3 | 14-15 | Final setup and testing |

**Total: 15 tasks**
