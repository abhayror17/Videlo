import os
import asyncio
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import init_db, SessionLocal
from .routes import generations, prompts, ads, workflow, avatar, ugc_ads, ugc_ads
from .models import Generation, AiAvatarProject


def cleanup_stale_processing_generations():
    """Mark generations stuck in 'processing' or 'pending' state for too long as failed.
    
    This should be called on startup to clean up any orphaned generations from
    server restarts or failed background tasks.
    """
    db = SessionLocal()
    try:
        # Mark generations stuck in processing for more than 30 minutes as failed
        stale_cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
        
        stale_generations = db.query(Generation).filter(
            Generation.status.in_(["processing", "pending"]),
            Generation.created_at < stale_cutoff
        ).all()
        
        for gen in stale_generations:
            gen.status = "failed"
            gen.error_message = "Generation timed out (stale on startup)"
        
        if stale_generations:
            db.commit()
            print(f"[Startup] Marked {len(stale_generations)} stale processing generations as failed")
    except Exception as e:
        print(f"[Startup] Error cleaning stale generations: {e}")
        db.rollback()
    finally:
        db.close()


# Cleanup task - runs every hour
async def cleanup_old_media():
    """Delete generations and avatar projects older than 1 day.
    Also deletes local media files from disk.
    Also marks stale processing generations as failed.
    """
    import os
    
    while True:
        try:
            await asyncio.sleep(3600)  # Run every hour
            
            db = SessionLocal()
            try:
                # First, mark stale processing generations as failed (stuck for > 30 min)
                stale_cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
                stale_count = db.query(Generation).filter(
                    Generation.status.in_(["processing", "pending"]),
                    Generation.created_at < stale_cutoff
                ).update(
                    {"status": "failed", "error_message": "Generation timed out (cleanup)"},
                    synchronize_session=False
                )
                
                if stale_count > 0:
                    print(f"[Cleanup] Marked {stale_count} stale processing generations as failed")
                
                # Calculate cutoff time (1 day ago)
                cutoff = datetime.now(timezone.utc) - timedelta(days=1)
                
                # Get local paths before deleting records
                old_generations = db.query(Generation).filter(
                    Generation.created_at < cutoff,
                    Generation.local_path.isnot(None)
                ).all()
                
                local_paths_to_delete = [g.local_path for g in old_generations]
                
                # Delete old generations
                deleted_gens = db.query(Generation).filter(
                    Generation.created_at < cutoff
                ).delete()
                
                # Delete old avatar projects
                deleted_avatars = db.query(AiAvatarProject).filter(
                    AiAvatarProject.created_at < cutoff
                ).delete()
                
                db.commit()
                
                # Delete local files
                deleted_files = 0
                for local_path in local_paths_to_delete:
                    try:
                        if local_path and os.path.exists(local_path):
                            os.remove(local_path)
                            deleted_files += 1
                    except Exception as e:
                        print(f"[Cleanup] Failed to delete file {local_path}: {e}")
                
                if deleted_gens > 0 or deleted_avatars > 0:
                    print(f"[Cleanup] Deleted {deleted_gens} generations, {deleted_avatars} avatar projects, {deleted_files} local files older than 1 day")
            except Exception as e:
                print(f"[Cleanup] Error: {e}")
                db.rollback()
            finally:
                db.close()
        except Exception as e:
            print(f"[Cleanup] Task error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle - startup and shutdown."""
    # Startup
    init_db()
    
    # Clean up any stale processing generations from previous server runs
    cleanup_stale_processing_generations()
    
    # Start cleanup background task
    cleanup_task = asyncio.create_task(cleanup_old_media())
    
    yield
    
    # Shutdown
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


# Create FastAPI app with lifespan
app = FastAPI(
    title="Videlo API",
    description="Text-to-Image and Image-to-Video Generation API using deAI",
    version="1.1.0",
    lifespan=lifespan
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
app.include_router(avatar.router)
app.include_router(ugc_ads.router)
app.include_router(ugc_ads.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Videlo API", "docs": "/docs"}
