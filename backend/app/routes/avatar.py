"""
AI Video Avatar Routes - 3-Step Pipeline

API endpoints for creating talking AI avatars:
- Step 1: Generate Portrait (txt2img - FLUX-2 Klein)
- Step 2: Generate Voice (txt2audio - Kokoro/Chatterbox)
- Step 3: Animate (aud2video - LTX-2.3)

Uses request_id tracking - frontend polls /avatar/{id}/status for updates.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
import asyncio
from typing import Optional

from ..database import get_db
from ..models import AiAvatarProject, Generation
from ..schemas import (
    AiAvatarCreate,
    AiAvatarResponse,
    AiAvatarListResponse,
    AiAvatarStepRequest,
    AiAvatarRegenerateRequest
)
from ..services.deapi import get_deapi_client

router = APIRouter(prefix="/api", tags=["avatar"])


@router.get("/avatar/health")
async def avatar_health():
    """Health check for avatar routes."""
    from ..database import SessionLocal
    try:
        db = SessionLocal()
        count = db.query(AiAvatarProject).count()
        db.close()
        return {"status": "ok", "table_exists": True, "project_count": count}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ==============================================================================
# PROJECT MANAGEMENT
# ==============================================================================

@router.post("/avatar", response_model=AiAvatarResponse)
async def create_avatar_project(
    request: AiAvatarCreate,
    db: Session = Depends(get_db)
):
    """Create a new AI Avatar project."""
    project = AiAvatarProject(
        name=request.name,
        portrait_prompt=request.portrait_prompt,
        speech_text=request.speech_text,
        motion_prompt=request.motion_prompt,
        voice_model=request.voice_model,
        voice_id=request.voice_id,
        voice_speed=request.voice_speed,
        voice_lang=request.voice_lang,
        portrait_model=request.portrait_model,
        portrait_width=request.portrait_width,
        portrait_height=request.portrait_height,
        animation_model=request.animation_model,
        animation_frames=request.animation_frames,
        animation_fps=request.animation_fps
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return project


@router.get("/avatar", response_model=AiAvatarListResponse)
async def list_avatar_projects(
    page: int = 1,
    per_page: int = 10,
    db: Session = Depends(get_db)
):
    """List all AI Avatar projects."""
    offset = (page - 1) * per_page
    
    total = db.query(AiAvatarProject).count()
    projects = db.query(AiAvatarProject)\
        .order_by(desc(AiAvatarProject.created_at))\
        .offset(offset)\
        .limit(per_page)\
        .all()
    
    pages = (total + per_page - 1) // per_page
    
    return AiAvatarListResponse(
        items=projects,
        total=total,
        page=page,
        pages=pages
    )


@router.get("/avatar/{project_id}", response_model=AiAvatarResponse)
async def get_avatar_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific AI Avatar project."""
    project = db.query(AiAvatarProject).filter(AiAvatarProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Avatar project not found")
    return project


@router.delete("/avatar/{project_id}")
async def delete_avatar_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Delete an AI Avatar project."""
    project = db.query(AiAvatarProject).filter(AiAvatarProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Avatar project not found")
    
    db.delete(project)
    db.commit()
    return {"message": "Project deleted", "id": project_id}


# ==============================================================================
# STATUS CHECK - Frontend polls this endpoint
# ==============================================================================

@router.get("/avatar/{project_id}/status", response_model=AiAvatarResponse)
async def check_avatar_status(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Check status of avatar generation by querying deAPI for pending request_ids.
    
    Frontend should poll this endpoint every 3-5 seconds.
    This endpoint checks the API status and updates the database.
    """
    project = db.query(AiAvatarProject).filter(AiAvatarProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Avatar project not found")
    
    client = get_deapi_client()
    
    # Check portrait status if we have a request_id but no result
    if project.portrait_request_id and project.portrait_status == "processing":
        try:
            status = await client.get_request_status(project.portrait_request_id)
            data = status.get("data", {})
            if data.get("status") == "done":
                project.portrait_url = data.get("result_url")
                project.portrait_status = "completed"
                project.current_step = 2
            elif data.get("status") == "error":
                project.portrait_status = "failed"
                project.error_message = data.get("error", "Portrait generation failed")
            db.commit()
        except Exception as e:
            print(f"[Avatar] Error checking portrait status: {e}")
    
    # Check audio status if we have a request_id but no result
    if project.audio_request_id and project.audio_status == "processing":
        try:
            status = await client.get_request_status(project.audio_request_id)
            data = status.get("data", {})
            if data.get("status") == "done":
                project.audio_url = data.get("result_url")
                project.audio_status = "completed"
                project.current_step = 3
            elif data.get("status") == "error":
                project.audio_status = "failed"
                project.error_message = data.get("error", "Audio generation failed")
            db.commit()
        except Exception as e:
            print(f"[Avatar] Error checking audio status: {e}")
    
    # Check video status if we have a request_id but no result
    if project.video_request_id and project.video_status == "processing":
        try:
            status = await client.get_request_status(project.video_request_id)
            data = status.get("data", {})
            if data.get("status") == "done":
                project.video_url = data.get("result_url") or data.get("download_url")
                project.video_status = "completed"
                project.overall_status = "completed"
                project.completed_at = datetime.utcnow()
            elif data.get("status") == "error":
                project.video_status = "failed"
                project.error_message = data.get("error", "Video generation failed")
            db.commit()
        except Exception as e:
            print(f"[Avatar] Error checking video status: {e}")
    
    # Auto-trigger next steps when previous completes
    if project.portrait_status == "completed" and project.audio_status == "pending" and not project.audio_request_id:
        # Start audio generation
        await start_audio_generation(project, client, db)
    
    if project.portrait_status == "completed" and project.audio_status == "completed" and project.video_status == "pending" and not project.video_request_id:
        # Start video generation
        await start_video_generation(project, client, db)
    
    db.refresh(project)
    return project


# ==============================================================================
# GENERATION HELPERS - Start generation and store request_id
# ==============================================================================

async def start_portrait_generation(project: AiAvatarProject, client, db: Session):
    """Start portrait generation and store request_id."""
    try:
        print(f"[Avatar] Starting portrait generation for project {project.id}")
        result = await client.generate_text2img(
            prompt=project.portrait_prompt,
            model=project.portrait_model,
            width=project.portrait_width,
            height=project.portrait_height
        )
        
        request_id = result.get("data", {}).get("request_id") or result.get("request_id")
        if request_id:
            project.portrait_request_id = request_id
            project.portrait_status = "processing"
            project.overall_status = "processing"
            print(f"[Avatar] Portrait request_id: {request_id}")
        else:
            project.portrait_status = "failed"
            project.error_message = result.get("error", "Failed to start portrait generation")
        
        db.commit()
    except Exception as e:
        print(f"[Avatar] Portrait generation error: {e}")
        project.portrait_status = "failed"
        project.error_message = str(e)
        db.commit()


async def start_audio_generation(project: AiAvatarProject, client, db: Session):
    """Start audio generation and store request_id."""
    try:
        print(f"[Avatar] Starting audio generation for project {project.id}")
        result = await client.generate_txt2audio(
            text=project.speech_text,
            model=project.voice_model,
            voice=project.voice_id,
            lang=project.voice_lang,
            speed=project.voice_speed
        )
        
        request_id = result.get("data", {}).get("request_id") or result.get("request_id")
        if request_id:
            project.audio_request_id = request_id
            project.audio_status = "processing"
            print(f"[Avatar] Audio request_id: {request_id}")
        else:
            project.audio_status = "failed"
            project.error_message = result.get("error", "Failed to start audio generation")
        
        db.commit()
    except Exception as e:
        print(f"[Avatar] Audio generation error: {e}")
        project.audio_status = "failed"
        project.error_message = str(e)
        db.commit()


async def start_video_generation(project: AiAvatarProject, client, db: Session):
    """Start video generation and store request_id."""
    if not project.portrait_url or not project.audio_url:
        project.video_status = "failed"
        project.error_message = "Portrait and audio must be generated first"
        db.commit()
        return
    
    try:
        print(f"[Avatar] Starting video generation for project {project.id}")
        motion_prompt = project.motion_prompt or "natural head movement, blinking, lip sync, expressive"
        
        # Ensure valid values for LTX-2.3 constraints
        frames = max(49, project.animation_frames or 97)  # min 49
        fps = min(24, project.animation_fps or 24)  # max 24
        width = max(512, project.portrait_width or 512)  # min 512
        height = max(512, project.portrait_height or 512)  # min 512
        
        print(f"[Avatar] Video params: frames={frames}, fps={fps}, width={width}, height={height}")
        
        result = await client.generate_aud2video(
            image_url=project.portrait_url,
            audio_url=project.audio_url,
            prompt=motion_prompt,
            model=project.animation_model,
            width=width,
            height=height,
            frames=frames,
            fps=fps
        )
        
        request_id = result.get("data", {}).get("request_id") or result.get("request_id")
        if request_id:
            project.video_request_id = request_id
            project.video_status = "processing"
            print(f"[Avatar] Video request_id: {request_id}")
        else:
            project.video_status = "failed"
            project.error_message = result.get("error", "Failed to start video generation")
        
        db.commit()
    except Exception as e:
        print(f"[Avatar] Video generation error: {e}")
        project.video_status = "failed"
        project.error_message = str(e)
        db.commit()


# ==============================================================================
# PIPELINE EXECUTION
# ==============================================================================

@router.post("/avatar/{project_id}/generate", response_model=AiAvatarResponse)
async def generate_avatar(
    project_id: int,
    request: AiAvatarStepRequest,
    db: Session = Depends(get_db)
):
    """
    Start generation for a specific step or all steps.
    
    Returns immediately with request_id stored in database.
    Frontend should poll /avatar/{id}/status for progress updates.
    
    Steps:
    - portrait: Generate the avatar portrait (Step 1)
    - audio: Generate the voice audio (Step 2)  
    - video: Animate with LTX-2.3 (Step 3)
    - all: Run complete pipeline (Steps 1-3)
    """
    project = db.query(AiAvatarProject).filter(AiAvatarProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Avatar project not found")
    
    client = get_deapi_client()
    
    if request.step == "video":
        if project.portrait_status != "completed":
            raise HTTPException(status_code=400, detail="Portrait must be generated first")
        if project.audio_status != "completed":
            raise HTTPException(status_code=400, detail="Audio must be generated first")
    
    # Start generation(s)
    if request.step == "portrait" or request.step == "all":
        await start_portrait_generation(project, client, db)
    
    if request.step == "audio":
        if project.portrait_status == "completed":
            await start_audio_generation(project, client, db)
        # Otherwise will be triggered when portrait completes
    
    if request.step == "video":
        await start_video_generation(project, client, db)
    
    db.refresh(project)
    return project


@router.post("/avatar/{project_id}/regenerate", response_model=AiAvatarResponse)
async def regenerate_avatar(
    project_id: int,
    request: AiAvatarRegenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Regenerate with modified parameters.
    
    Resets request_ids and status, then starts new generation.
    """
    project = db.query(AiAvatarProject).filter(AiAvatarProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Avatar project not found")
    
    client = get_deapi_client()
    regenerate_all = False
    regenerate_from_audio = False
    
    # Update parameters
    if request.portrait_prompt:
        project.portrait_prompt = request.portrait_prompt
        project.portrait_status = "pending"
        project.portrait_url = None
        project.portrait_request_id = None
        regenerate_all = True
    
    if request.speech_text:
        project.speech_text = request.speech_text
        project.audio_status = "pending"
        project.audio_url = None
        project.audio_request_id = None
        regenerate_from_audio = True
    
    if request.motion_prompt is not None:
        project.motion_prompt = request.motion_prompt
    
    if request.voice_id:
        project.voice_id = request.voice_id
        regenerate_from_audio = True
    
    if request.voice_speed is not None:
        project.voice_speed = request.voice_speed
        regenerate_from_audio = True
    
    # Reset video if needed
    if regenerate_all or regenerate_from_audio:
        project.video_status = "pending"
        project.video_url = None
        project.video_request_id = None
    
    db.commit()
    
    # Start regeneration
    if regenerate_all:
        project.overall_status = "processing"
        db.commit()
        await start_portrait_generation(project, client, db)
    elif regenerate_from_audio:
        project.audio_status = "pending"
        project.overall_status = "processing"
        db.commit()
        await start_audio_generation(project, client, db)
    
    db.refresh(project)
    return project