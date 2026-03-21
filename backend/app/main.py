import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routes import generations, prompts, ads, workflow

# Create FastAPI app
app = FastAPI(
    title="Videlo API",
    description="Text-to-Image and Image-to-Video Generation API using deAI",
    version="1.1.0"
)

# CORS middleware - configurable for production (Render/Vercel)
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generations.router)
app.include_router(prompts.router)
app.include_router(ads.router)
app.include_router(workflow.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Videlo API", "docs": "/docs"}
