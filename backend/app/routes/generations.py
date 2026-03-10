from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from math import ceil
from datetime import datetime, timezone

from ..database import get_db
from ..models import Generation
from ..schemas import (
    GenerationCreate,
    GenerationResponse,
    GenerationListResponse,
    HealthResponse,
    BalanceResponse,
    Text2ImgRequest,
    Txt2VideoRequest,
    Img2VideoRequest
)
from ..services.deapi import get_deapi_client

router = APIRouter(prefix="/api", tags=["generations"])


async def poll_for_result(request_id: str, generation_id: int):
    """Background task to poll for generation result from deAPI."""
    import asyncio
    from ..database import SessionLocal
    
    client = get_deapi_client()
    
    for _ in range(120):  # Poll for up to 10 minutes
        await asyncio.sleep(3)  # Poll every 3 seconds for more responsive updates
        
        db = SessionLocal()
        try:
            result = await client.get_request_status(request_id)
            data = result.get("data", {})
            status = data.get("status")
            progress = data.get("progress", 0)  # Real progress from API
            
            generation = db.query(Generation).filter(
                Generation.id == generation_id
            ).first()
            
            if not generation:
                return
            
            if status == "done":  # Completed
                generation.status = "completed"
                generation.progress = 100
                generation.remote_url = data.get("result_url")
                generation.completed_at = datetime.now(timezone.utc)
                db.commit()
                return
            elif status == "error":  # Failed
                generation.status = "failed"
                generation.error_message = data.get("error", "Generation failed")
                db.commit()
                return
            elif status in ("processing", "pending"):
                generation.status = "processing"
                # Use real progress from API, cap at 98% until complete
                generation.progress = min(98, int(progress) if progress else 5)
                db.commit()
                # Continue polling
                
        except Exception as e:
            db.rollback()
            import traceback
            print(f"Polling error: {e}")
            traceback.print_exc()
        finally:
            db.close()


@router.post("/generate/text2img", response_model=GenerationResponse)
async def create_text2img(
    request: Text2ImgRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit a new text-to-image generation request to deAPI."""
    client = get_deapi_client()
    
    # Create pending record
    generation = Generation(
        prompt=request.prompt,
        negative_prompt=request.negative_prompt,
        model=request.model,
        generation_type="text2img",
        width=request.width,
        height=request.height,
        guidance=request.guidance,
        steps=request.steps,
        seed=request.seed,
        status="pending",
        progress=0
    )
    db.add(generation)
    db.commit()
    db.refresh(generation)
    
    try:
        # Call deAPI text2img endpoint
        result = await client.generate_text2img(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            model=request.model,
            width=request.width,
            height=request.height,
            guidance=request.guidance,
            steps=request.steps,
            seed=request.seed
        )
        
        # Update with request_id from deAPI
        data = result.get("data", {})
        generation.uuid = data.get("request_id")
        generation.status = "processing"
        
        db.commit()
        db.refresh(generation)
        
        # Start polling for result
        background_tasks.add_task(
            poll_for_result,
            generation.uuid,
            generation.id
        )
        
        return generation
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        generation.status = "failed"
        generation.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/txt2video", response_model=GenerationResponse)
async def create_txt2video(
    request: Txt2VideoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit a new text-to-video generation request to deAPI."""
    client = get_deapi_client()
    
    # Create pending record
    generation = Generation(
        prompt=request.prompt,
        model=request.model,
        generation_type="txt2video",
        width=request.width,
        height=request.height,
        frames=request.frames,
        fps=request.fps,
        guidance=request.guidance,
        steps=request.steps,
        seed=request.seed,
        status="pending",
        progress=0
    )
    db.add(generation)
    db.commit()
    db.refresh(generation)
    
    try:
        # Call deAPI txt2video endpoint
        result = await client.generate_txt2video(
            prompt=request.prompt,
            model=request.model,
            width=request.width,
            height=request.height,
            guidance=request.guidance,
            steps=request.steps,
            frames=request.frames,
            seed=request.seed,
            fps=request.fps
        )
        
        # Update with request_id from deAPI
        data = result.get("data", {})
        generation.uuid = data.get("request_id")
        generation.status = "processing"
        
        db.commit()
        db.refresh(generation)
        
        # Start polling for result
        background_tasks.add_task(
            poll_for_result,
            generation.uuid,
            generation.id
        )
        
        return generation
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        generation.status = "failed"
        generation.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/img2video", response_model=GenerationResponse)
async def create_img2video(
    background_tasks: BackgroundTasks,
    first_frame: UploadFile = File(None),
    generation_id: int = Form(None),
    prompt: str = Form(...),
    model: str = Form("Ltx2_19B_Dist_FP8"),
    width: int = Form(512),
    height: int = Form(512),
    guidance: float = Form(3.5),
    steps: int = Form(20),
    frames: int = Form(24),
    fps: int = Form(30),
    seed: int = Form(-1),
    db: Session = Depends(get_db)
):
    """Submit a new image-to-video generation request to deAPI.
    
    Either provide first_frame file directly or generation_id to fetch from existing generation.
    """
    import httpx
    client = get_deapi_client()
    
    # Create pending record
    generation = Generation(
        prompt=prompt,
        model=model,
        generation_type="img2video",
        width=width,
        height=height,
        frames=frames,
        fps=fps,
        guidance=guidance,
        steps=steps,
        seed=seed,
        status="pending",
        progress=0
    )
    db.add(generation)
    db.commit()
    db.refresh(generation)
    
    try:
        image_content = None
        
        # Option 1: File uploaded directly
        if first_frame and first_frame.filename:
            if not first_frame.content_type or not first_frame.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="First frame must be an image file")
            image_content = await first_frame.read()
        
        # Option 2: Fetch from existing generation
        elif generation_id:
            source_gen = db.query(Generation).filter(Generation.id == generation_id).first()
            if not source_gen:
                raise HTTPException(status_code=404, detail="Source generation not found")
            if not source_gen.remote_url:
                raise HTTPException(status_code=400, detail="Source generation has no image URL")
            
            # Fetch image from URL (server-side, no CORS issues)
            async with httpx.AsyncClient(verify=False) as http_client:
                response = await http_client.get(source_gen.remote_url, timeout=30.0)
                response.raise_for_status()
                image_content = response.content
        else:
            raise HTTPException(status_code=400, detail="Either first_frame file or generation_id is required")
        
        # Call deAPI img2video endpoint
        result = await client.generate_img2video(
            first_frame_image=image_content,
            prompt=prompt,
            model=model,
            width=width,
            height=height,
            guidance=guidance,
            steps=steps,
            frames=frames,
            seed=seed,
            fps=fps
        )
        
        # Update with request_id from deAPI
        data = result.get("data", {})
        generation.uuid = data.get("request_id")
        generation.status = "processing"
        
        db.commit()
        db.refresh(generation)
        
        # Start polling for result
        background_tasks.add_task(
            poll_for_result,
            generation.uuid,
            generation.id
        )
        
        return generation
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        generation.status = "failed"
        generation.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generations", response_model=GenerationListResponse)
async def list_generations(
    page: int = 1,
    per_page: int = 4,
    generation_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all generations with pagination."""
    offset = (page - 1) * per_page
    
    query = db.query(Generation).filter(Generation.status != 'failed')
    
    if generation_type:
        query = query.filter(Generation.generation_type == generation_type)
    
    total = query.count()
    generations = query.order_by(
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


@router.get("/balance", response_model=BalanceResponse)
async def get_balance():
    """Get deAPI account balance."""
    client = get_deapi_client()
    try:
        result = await client.check_balance()
        data = result.get("data", {})
        return BalanceResponse(
            balance=data.get("balance", 0.0),
            currency=data.get("currency", "USD")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models(inference_type: Optional[str] = None):
    """List available deAPI models."""
    client = get_deapi_client()
    try:
        result = await client.list_models(inference_type=inference_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    return HealthResponse(status="ok", database=db_status)
