# Videlo - Text-to-Image Generator Design

**Date:** 2026-03-05

## Overview

Videlo is a web application that generates images from text prompts using the Geminigen AI API. It supports webhook callbacks for real-time updates and history polling as a fallback for local development.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python + FastAPI |
| Frontend | Vue.js + Vite |
| Database | SQLite |
| Storage | Remote URLs only (no local storage) |
| Response Mode | Webhook (primary) + Polling (dev fallback) |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     FastAPI Backend                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │   API    │  │ Webhook  │  │  Polling Service     │  │
│  │ Routes   │  │ Handler  │  │  (dev fallback)      │  │
│  └────┬─────┘  └────┬─────┘  └──────────┬───────────┘  │
│       │             │                   │               │
│       ▼             ▼                   ▼               │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Geminigen API Client               │   │
│  └─────────────────────────────────────────────────┘   │
│       │                                                  │
│       ▼                                                  │
│  ┌──────────┐                                           │
│  │  SQLite  │                                           │
│  │ Database │                                           │
│  └──────────┘                                           │
└─────────────────────────────────────────────────────────┘
                         ▲
                         │
                    ┌────┴────┐
                    │  Vue.js │
                    │  SPA    │
                    └─────────┘
```

## Database Schema

```sql
CREATE TABLE generations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT UNIQUE NOT NULL,
    prompt TEXT NOT NULL,
    negative_prompt TEXT,
    model TEXT DEFAULT 'nano-banana-pro',
    status TEXT DEFAULT 'pending',
    remote_url TEXT,
    thumbnail_url TEXT,
    file_size INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/generate` | Submit text-to-image generation request |
| GET | `/api/generations` | List all generations (paginated) |
| GET | `/api/generations/{id}` | Get single generation details |
| GET | `/api/generations/{id}/status` | Poll status for pending generations |
| POST | `/webhook/geminigen` | Receive webhook callback from geminigen |
| GET | `/api/health` | Health check endpoint |

## Project Structure

```
videlo/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── generations.py
│   │   │   └── webhook.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── geminigen.py
│   │   └── utils/
│   │       └── security.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── services/
│   │   └── App.vue
│   ├── package.json
│   └── vite.config.js
├── uapi_public_key.pem
└── README.md
```

## Frontend Components

- **PromptForm.vue** - Text input, model selection, generate button
- **ImageCard.vue** - Single generation display (thumbnail, status, prompt)
- **Gallery.vue** - Grid of ImageCards with pagination
- **StatusBadge.vue** - Pending/Processing/Completed/Failed badge
- **ImageModal.vue** - Full-size image viewer
- **Home.vue** - Main page: form + gallery

## Geminigen API Integration

### Generate Image
```
POST https://api.geminigen.ai/uapi/v1/generate_image
Headers: x-api-key, Content-Type: multipart/form-data
Params: prompt, model, aspect_ratio, style, output_format, resolution
```

### History API
```
GET https://api.geminigen.ai/uapi/v1/histories?filter_by=all&items_per_page=10&page=1
Headers: x-api-key
```

### Webhook Signature Verification
- Uses RSA public key verification
- MD5 hash of event UUID
- PKCS1v15 padding with SHA256

## Error Handling

- API key missing/invalid → Return 401
- Geminigen API timeout → Retry with exponential backoff (3 retries)
- Webhook signature verification fails → Log and reject (401)
- Image generation fails → Store error_message, mark status as "failed"
- Image fails to load (expired) → Show placeholder "Image expired"

## Development Mode

When `USE_WEBHOOK=false` in `.env`:
- Backend polls geminigen history API every 5s
- Updates record when status changes
- Simpler for local dev without ngrok

## Future Expansion

- Image-to-image generation
- Video generation from images
- User authentication
- Cloud storage for persistent image storage
