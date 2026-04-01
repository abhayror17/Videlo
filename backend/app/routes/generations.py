from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
from math import ceil
from datetime import datetime, timezone
import random
import json

from ..database import get_db
from ..models import Generation, Transcription
from ..schemas import (
    GenerationCreate,
    GenerationResponse,
    GenerationListResponse,
    HealthResponse,
    BalanceResponse,
    Text2ImgRequest,
    Txt2VideoRequest,
    Img2VideoRequest,
    Txt2MusicRequest,
    Txt2AudioRequest,
    Txt2EmbeddingRequest,
    EmbeddingResponse,
    Vid2TxtRequest,
    Aud2TxtRequest,
    TranscriptionResponse,
    PromptEnhanceRequest,
    PromptEnhanceResponse,
    NanoBananaRequest,
    NanoBananaResponse,
    VideoReplaceRequest
)
from ..services.deapi import get_deapi_client


def get_seed(seed: int) -> int:
    """Return a random positive seed if seed is -1, otherwise return the provided seed."""
    if seed == -1:
        return random.randint(1, 2147483647)
    return seed

router = APIRouter(prefix="/api", tags=["generations"])


async def poll_for_result(request_id: str, generation_id: int):
    """
    Background task to poll for generation result from deAPI.
    
    Optimized polling strategy to minimize API requests:
    - Uses exponential backoff: starts at 10s, increases to 30s max
    - Maximum 20 polls over ~8 minutes (instead of 120 polls in 6 min)
    - Stops immediately on completion, error, or 404 (expired)
    """
    import asyncio
    from ..database import SessionLocal
    
    client = get_deapi_client()
    
    # Exponential backoff polling: 10s -> 15s -> 20s -> 25s -> 30s (max)
    # Total ~8 minutes with 20 polls max
    max_polls = 20
    min_delay = 10  # Start at 10 seconds
    max_delay = 30  # Max 30 seconds between polls
    
    for poll_count in range(max_polls):
        # Calculate delay with exponential backoff (capped at max_delay)
        delay = min(min_delay + (poll_count * 2), max_delay)
        await asyncio.sleep(delay)
        
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
            
            if status == "done":  # Completed - STOP POLLING
                generation.status = "completed"
                generation.progress = 100
                generation.remote_url = data.get("result_url")
                generation.completed_at = datetime.now(timezone.utc)
                db.commit()
                print(f"[Poll] Generation {generation_id} completed after {poll_count + 1} polls")
                return
            elif status == "error":  # Failed - STOP POLLING
                generation.status = "failed"
                generation.error_message = data.get("error", "Generation failed")
                db.commit()
                print(f"[Poll] Generation {generation_id} failed after {poll_count + 1} polls")
                return
            elif status in ("processing", "pending"):
                generation.status = "processing"
                # Use real progress from API, cap at 98% until complete
                generation.progress = min(98, int(progress) if progress else 5)
                db.commit()
                # Continue polling with backoff
                
        except Exception as e:
            db.rollback()
            import traceback
            error_str = str(e)
            print(f"[Poll] Error polling generation {generation_id}: {e}")
            
            # If 404, the request doesn't exist on deAPI - mark as failed and STOP
            if "404" in error_str or "Not Found" in error_str:
                generation = db.query(Generation).filter(Generation.id == generation_id).first()
                if generation:
                    generation.status = "failed"
                    generation.error_message = "Request expired or not found on remote server"
                    db.commit()
                    print(f"[Poll] Generation {generation_id} marked as failed due to 404")
                return
            # For other errors, continue polling
        finally:
            db.close()
    
    # If we exhausted all polls, mark as failed
    print(f"[Poll] Generation {generation_id} timed out after {max_polls} polls")
    db = SessionLocal()
    try:
        generation = db.query(Generation).filter(Generation.id == generation_id).first()
        if generation and generation.status == "processing":
            generation.status = "failed"
            generation.error_message = "Generation timed out"
            db.commit()
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
    
    # Generate random seed if not provided
    actual_seed = get_seed(request.seed)
    
    # Create pending record
    generation = Generation(
        prompt=request.prompt,
        negative_prompt=request.negative_prompt,
        model=request.model or "Flux_2_Klein_4B_BF16",
        generation_type="text2img",
        width=request.width,
        height=request.height,
        guidance=request.guidance,
        steps=request.steps or 4,
        seed=actual_seed,
        loras=request.loras,
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
            seed=actual_seed,
            loras=request.loras
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
    
    # Generate random seed if not provided
    actual_seed = get_seed(request.seed)
    
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
        seed=actual_seed,
        status="pending",
        progress=0
    )
    db.add(generation)
    db.commit()
    db.refresh(generation)
    
    try:
        # Call deAPI txt2video endpoint
        # Note: Ltx2_3_22B_Dist_INT8 doesn't support steps/guidance
        result = await client.generate_txt2video(
            prompt=request.prompt,
            model=request.model,
            width=max(512, request.width or 512),
            height=max(512, request.height or 512),
            frames=max(49, request.frames or 97),
            seed=actual_seed,
            fps=24  # Fixed at 24 for LTX-2.3
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
    last_frame: UploadFile = File(None),
    generation_id: int = Form(None),
    last_frame_generation_id: int = Form(None),
    prompt: str = Form(...),
    model: str = Form("Ltx2_3_22B_Dist_INT8"),
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
    Optionally provide last_frame for end frame control.
    """
    import httpx
    client = get_deapi_client()
    
    # Generate random seed if not provided
    actual_seed = get_seed(seed)
    
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
        seed=actual_seed,
        status="pending",
        progress=0
    )
    db.add(generation)
    db.commit()
    db.refresh(generation)
    
    try:
        image_content = None
        last_frame_content = None
        
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
        
        # Handle last frame (optional)
        if last_frame and last_frame.filename:
            if not last_frame.content_type or not last_frame.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="Last frame must be an image file")
            last_frame_content = await last_frame.read()
        elif last_frame_generation_id:
            last_gen = db.query(Generation).filter(Generation.id == last_frame_generation_id).first()
            if last_gen and last_gen.remote_url:
                async with httpx.AsyncClient(verify=False) as http_client:
                    response = await http_client.get(last_gen.remote_url, timeout=30.0)
                    response.raise_for_status()
                    last_frame_content = response.content
        
        # Call deAPI img2video endpoint
        # Note: Ltx2_3_22B_Dist_INT8 doesn't support steps/guidance
        # Ensure valid constraints: frames>=49, fps=24, width>=512, height>=512
        result = await client.generate_img2video(
            first_frame_image=image_content,
            prompt=prompt,
            model=model,
            width=max(512, width or 512),
            height=max(512, height or 512),
            frames=max(49, frames or 97),
            seed=actual_seed,
            fps=24,  # Fixed at 24 for LTX-2.3
            last_frame_image=last_frame_content
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


@router.post("/generate/img2img", response_model=GenerationResponse)
async def create_img2img(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(None),
    generation_id: int = Form(None),
    prompt: str = Form(...),
    model: str = Form("QwenImageEdit_Plus_NF4"),
    guidance: float = Form(3.5),
    steps: int = Form(20),
    seed: int = Form(-1),
    negative_prompt: str = Form(None),
    loras: str = Form(None),
    db: Session = Depends(get_db)
):
    """Submit a new image-to-image transformation request to deAPI.
    
    Either provide image file directly or generation_id to fetch from existing generation.
    Models: QwenImageEdit_Plus_NF4 (style transfer), Flux_2_Klein_4B_BF16 (general editing)
    """
    import httpx
    client = get_deapi_client()
    
    # Generate random seed if not provided
    actual_seed = get_seed(seed)
    
    # Parse loras if provided
    loras_list = None
    if loras:
        try:
            loras_list = json.loads(loras)
        except:
            loras_list = [loras]
    
    # Create pending record
    generation = Generation(
        prompt=prompt,
        negative_prompt=negative_prompt,
        model=model,
        generation_type="img2img",
        guidance=guidance,
        steps=steps,
        seed=actual_seed,
        loras=loras_list,
        status="pending",
        progress=0
    )
    db.add(generation)
    db.commit()
    db.refresh(generation)
    
    try:
        image_content = None
        image_filename = "image.png"
        
        # Option 1: File uploaded directly
        if image and image.filename:
            if not image.content_type or not image.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="Uploaded file must be an image")
            image_content = await image.read()
            image_filename = image.filename
        
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
            raise HTTPException(status_code=400, detail="Either image file or generation_id is required")
        
        # Call deAPI img2img endpoint
        result = await client.generate_img2img(
            image=image_content,
            prompt=prompt,
            model=model,
            guidance=guidance,
            steps=steps,
            seed=actual_seed,
            negative_prompt=negative_prompt,
            loras=loras_list,
            image_filename=image_filename
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


# ============================================================
# TEXT-TO-MUSIC
# ============================================================

@router.post("/generate/txt2music", response_model=GenerationResponse)
async def create_txt2music(
    request: Txt2MusicRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit a text-to-music generation request to deAPI."""
    client = get_deapi_client()
    
    actual_seed = get_seed(request.seed)
    
    generation = Generation(
        prompt=request.caption,
        model=request.model,
        generation_type="txt2music",
        duration=request.duration,
        bpm=request.bpm,
        steps=request.steps,
        guidance=request.guidance,
        seed=actual_seed,
        status="pending",
        progress=0
    )
    db.add(generation)
    db.commit()
    db.refresh(generation)
    
    try:
        result = await client.generate_txt2music(
            caption=request.caption,
            model=request.model,
            duration=request.duration,
            steps=request.steps,
            bpm=request.bpm,
            guidance=request.guidance,
            seed=actual_seed
        )
        
        data = result.get("data", {})
        generation.uuid = data.get("request_id")
        generation.status = "processing"
        
        db.commit()
        db.refresh(generation)
        
        background_tasks.add_task(poll_for_result, generation.uuid, generation.id)
        
        return generation
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        generation.status = "failed"
        generation.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# TEXT-TO-AUDIO / TTS
# ============================================================

@router.post("/generate/txt2audio", response_model=GenerationResponse)
async def create_txt2audio(
    background_tasks: BackgroundTasks,
    text: str = Form(...),
    model: str = Form("Kokoro"),
    voice: str = Form(None),
    lang: str = Form("en-us"),
    speed: float = Form(1.0),
    format: str = Form("mp3"),
    sample_rate: int = Form(24000),
    mode: str = Form("custom_voice"),
    ref_audio: UploadFile = File(None),
    ref_text: str = Form(None),
    instruct: str = Form(None),
    db: Session = Depends(get_db)
):
    """Submit a text-to-speech generation request to deAPI.
    
    Supported models:
    - Kokoro: Fast, high-quality TTS with multiple languages and voices
    - Chatterbox: 23 languages, custom voice support
    - Qwen3_TTS_12Hz_1_7B_CustomVoice: Custom voice selection
    - Qwen3_TTS_12Hz_1_7B_Base: Voice cloning from reference audio
    - Qwen3_TTS_12Hz_1_7B_VoiceDesign: Voice design from instructions
    
    Modes:
    - custom_voice: Select from predefined voices (default)
    - voice_clone: Clone voice from reference audio (requires ref_audio)
    - voice_design: Design voice from text instructions (requires instruct)
    """
    client = get_deapi_client()
    
    # Set default voice based on model if not provided
    if not voice:
        if model == "Kokoro":
            voice = "af_sky"
        elif model == "Chatterbox":
            voice = "default"
        elif model.startswith("Qwen3_TTS"):
            voice = "Vivian"
        else:
            voice = "default"
    
    # Create pending record
    generation = Generation(
        prompt=text[:500],  # Store truncated text as prompt
        model=model,
        generation_type="txt2audio",
        status="pending",
        progress=0
    )
    db.add(generation)
    db.commit()
    db.refresh(generation)
    
    try:
        # Handle reference audio for voice cloning
        ref_audio_content = None
        if ref_audio and ref_audio.filename:
            ref_audio_content = await ref_audio.read()
        
        # Call deAPI txt2audio endpoint
        result = await client.generate_txt2audio(
            text=text,
            model=model,
            voice=voice,
            lang=lang,
            speed=speed,
            format=format,
            sample_rate=sample_rate,
            mode=mode,
            ref_audio=ref_audio_content,
            ref_text=ref_text,
            instruct=instruct
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


# ============================================================
# TEXT-TO-EMBEDDING
# ============================================================

@router.post("/generate/txt2embedding", response_model=EmbeddingResponse)
async def create_txt2embedding(
    request: Txt2EmbeddingRequest
):
    """Generate text embeddings using BGE M3 model."""
    client = get_deapi_client()
    
    try:
        result = await client.generate_txt2embedding(
            input_text=request.input,
            model=request.model,
            return_result_in_response=True
        )
        
        data = result.get("data", {})
        return EmbeddingResponse(
            request_id=data.get("request_id"),
            embedding=data.get("embedding")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# TRANSCRIPTION POLLING
# ============================================================

async def poll_for_transcription(request_id: str, transcription_id: int):
    """
    Background task to poll for transcription result.
    
    Optimized polling strategy to minimize API requests:
    - Uses exponential backoff: starts at 10s, increases to 30s max
    - Maximum 20 polls over ~8 minutes (instead of 120 polls)
    - Stops immediately on completion or error
    """
    import asyncio
    from ..database import SessionLocal
    
    client = get_deapi_client()
    
    max_polls = 20
    min_delay = 10
    max_delay = 30
    
    for poll_count in range(max_polls):
        delay = min(min_delay + (poll_count * 2), max_delay)
        await asyncio.sleep(delay)
        
        db = SessionLocal()
        try:
            result = await client.get_request_status(request_id)
            data = result.get("data", {})
            status = data.get("status")
            
            transcription = db.query(Transcription).filter(
                Transcription.id == transcription_id
            ).first()
            
            if not transcription:
                return
            
            if status == "done":
                transcription.status = "completed"
                transcription.progress = 100
                transcription.result_text = data.get("result")
                transcription.result_url = data.get("result_url")
                transcription.completed_at = datetime.now(timezone.utc)
                db.commit()
                print(f"[Poll] Transcription {transcription_id} completed after {poll_count + 1} polls")
                return
            elif status == "error":
                transcription.status = "failed"
                transcription.error_message = data.get("error", "Transcription failed")
                db.commit()
                print(f"[Poll] Transcription {transcription_id} failed after {poll_count + 1} polls")
                return
            elif status in ("processing", "pending"):
                transcription.status = "processing"
                transcription.progress = min(98, int(data.get("progress", 5)))
                db.commit()
                
        except Exception as e:
            db.rollback()
            print(f"[Poll] Transcription {transcription_id} error: {e}")
        finally:
            db.close()
    
    # Timeout handling
    print(f"[Poll] Transcription {transcription_id} timed out after {max_polls} polls")
    db = SessionLocal()
    try:
        transcription = db.query(Transcription).filter(Transcription.id == transcription_id).first()
        if transcription and transcription.status == "processing":
            transcription.status = "failed"
            transcription.error_message = "Transcription timed out"
            db.commit()
    finally:
        db.close()


# ============================================================
# VIDEO-TO-TEXT (URL)
# ============================================================

@router.post("/generate/vid2txt", response_model=TranscriptionResponse)
async def create_vid2txt(
    request: Vid2TxtRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Transcribe video from URL (YouTube, X/Twitter, Twitch, Kick)."""
    client = get_deapi_client()
    
    transcription = Transcription(
        source_type="vid2txt",
        source_url=request.video_url,
        model=request.model,
        include_ts=int(request.include_ts),
        status="pending",
        progress=0
    )
    db.add(transcription)
    db.commit()
    db.refresh(transcription)
    
    try:
        result = await client.generate_vid2txt(
            video_url=request.video_url,
            model=request.model,
            include_ts=request.include_ts
        )
        
        data = result.get("data", {})
        transcription.uuid = data.get("request_id")
        transcription.status = "processing"
        
        db.commit()
        db.refresh(transcription)
        
        background_tasks.add_task(poll_for_transcription, transcription.uuid, transcription.id)
        
        return transcription
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        transcription.status = "failed"
        transcription.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# VIDEO FILE TRANSCRIPTION
# ============================================================

@router.post("/generate/videofile2txt", response_model=TranscriptionResponse)
async def create_videofile2txt(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
    model: str = Form("WhisperLargeV3"),
    include_ts: bool = Form(True),
    db: Session = Depends(get_db)
):
    """Transcribe uploaded video file."""
    client = get_deapi_client()
    
    if not video.content_type or not video.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    transcription = Transcription(
        source_type="videofile2txt",
        source_filename=video.filename,
        model=model,
        include_ts=int(include_ts),
        status="pending",
        progress=0
    )
    db.add(transcription)
    db.commit()
    db.refresh(transcription)
    
    try:
        video_content = await video.read()
        
        result = await client.generate_videofile2txt(
            video=video_content,
            model=model,
            include_ts=include_ts,
            video_filename=video.filename
        )
        
        data = result.get("data", {})
        transcription.uuid = data.get("request_id")
        transcription.status = "processing"
        
        db.commit()
        db.refresh(transcription)
        
        background_tasks.add_task(poll_for_transcription, transcription.uuid, transcription.id)
        
        return transcription
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        transcription.status = "failed"
        transcription.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# AUDIO FILE TRANSCRIPTION
# ============================================================

@router.post("/generate/audiofile2txt", response_model=TranscriptionResponse)
async def create_audiofile2txt(
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    model: str = Form("WhisperLargeV3"),
    include_ts: bool = Form(True),
    db: Session = Depends(get_db)
):
    """Transcribe uploaded audio file."""
    client = get_deapi_client()
    
    if not audio.content_type or not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File must be an audio file")
    
    transcription = Transcription(
        source_type="audiofile2txt",
        source_filename=audio.filename,
        model=model,
        include_ts=int(include_ts),
        status="pending",
        progress=0
    )
    db.add(transcription)
    db.commit()
    db.refresh(transcription)
    
    try:
        audio_content = await audio.read()
        
        result = await client.generate_audiofile2txt(
            audio=audio_content,
            model=model,
            include_ts=include_ts,
            audio_filename=audio.filename
        )
        
        data = result.get("data", {})
        transcription.uuid = data.get("request_id")
        transcription.status = "processing"
        
        db.commit()
        db.refresh(transcription)
        
        background_tasks.add_task(poll_for_transcription, transcription.uuid, transcription.id)
        
        return transcription
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        transcription.status = "failed"
        transcription.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# X SPACES TRANSCRIPTION
# ============================================================

@router.post("/generate/aud2txt", response_model=TranscriptionResponse)
async def create_aud2txt(
    request: Aud2TxtRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Transcribe X/Twitter Spaces from URL."""
    client = get_deapi_client()
    
    transcription = Transcription(
        source_type="aud2txt",
        source_url=request.audio_url,
        model=request.model,
        include_ts=int(request.include_ts),
        status="pending",
        progress=0
    )
    db.add(transcription)
    db.commit()
    db.refresh(transcription)
    
    try:
        result = await client.generate_aud2txt(
            audio_url=request.audio_url,
            model=request.model,
            include_ts=request.include_ts
        )
        
        data = result.get("data", {})
        transcription.uuid = data.get("request_id")
        transcription.status = "processing"
        
        db.commit()
        db.refresh(transcription)
        
        background_tasks.add_task(poll_for_transcription, transcription.uuid, transcription.id)
        
        return transcription
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        transcription.status = "failed"
        transcription.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# IMAGE UPSCALE
# ============================================================

@router.post("/generate/img-upscale", response_model=GenerationResponse)
async def create_img_upscale(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(None),
    generation_id: int = Form(None),
    model: str = Form("RealESRGAN_x4"),
    db: Session = Depends(get_db)
):
    """Upscale image using RealESRGAN x4."""
    import httpx
    client = get_deapi_client()
    
    generation = Generation(
        prompt="Image upscale",
        model=model,
        generation_type="img-upscale",
        status="pending",
        progress=0
    )
    db.add(generation)
    db.commit()
    db.refresh(generation)
    
    try:
        image_content = None
        
        if image and image.filename:
            image_content = await image.read()
        elif generation_id:
            source_gen = db.query(Generation).filter(Generation.id == generation_id).first()
            if not source_gen or not source_gen.remote_url:
                raise HTTPException(status_code=404, detail="Source generation not found or has no URL")
            
            async with httpx.AsyncClient(verify=False) as http_client:
                response = await http_client.get(source_gen.remote_url, timeout=30.0)
                response.raise_for_status()
                image_content = response.content
        else:
            raise HTTPException(status_code=400, detail="Either image file or generation_id is required")
        
        result = await client.generate_img_upscale(
            image=image_content,
            model=model
        )
        
        data = result.get("data", {})
        generation.uuid = data.get("request_id")
        generation.status = "processing"
        
        db.commit()
        db.refresh(generation)
        
        background_tasks.add_task(poll_for_result, generation.uuid, generation.id)
        
        return generation
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        generation.status = "failed"
        generation.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# IMAGE BACKGROUND REMOVAL
# ============================================================

@router.post("/generate/img-rmbg", response_model=GenerationResponse)
async def create_img_rmbg(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(None),
    generation_id: int = Form(None),
    model: str = Form("Ben2"),
    db: Session = Depends(get_db)
):
    """Remove background from image."""
    import httpx
    client = get_deapi_client()
    
    generation = Generation(
        prompt="Background removal",
        model=model,
        generation_type="img-rmbg",
        status="pending",
        progress=0
    )
    db.add(generation)
    db.commit()
    db.refresh(generation)
    
    try:
        image_content = None
        
        if image and image.filename:
            image_content = await image.read()
        elif generation_id:
            source_gen = db.query(Generation).filter(Generation.id == generation_id).first()
            if not source_gen or not source_gen.remote_url:
                raise HTTPException(status_code=404, detail="Source generation not found or has no URL")
            
            async with httpx.AsyncClient(verify=False) as http_client:
                response = await http_client.get(source_gen.remote_url, timeout=30.0)
                response.raise_for_status()
                image_content = response.content
        else:
            raise HTTPException(status_code=400, detail="Either image file or generation_id is required")
        
        result = await client.generate_img_rmbg(
            image=image_content,
            model=model
        )
        
        data = result.get("data", {})
        generation.uuid = data.get("request_id")
        generation.status = "processing"
        
        db.commit()
        db.refresh(generation)
        
        background_tasks.add_task(poll_for_result, generation.uuid, generation.id)
        
        return generation
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        generation.status = "failed"
        generation.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# VIDEO BACKGROUND REMOVAL
# ============================================================

@router.post("/generate/vid-rmbg", response_model=GenerationResponse)
async def create_vid_rmbg(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
    model: str = Form("RMBG-1.4"),
    db: Session = Depends(get_db)
):
    """Remove background from video."""
    client = get_deapi_client()
    
    generation = Generation(
        prompt="Video background removal",
        model=model,
        generation_type="vid-rmbg",
        status="pending",
        progress=0
    )
    db.add(generation)
    db.commit()
    db.refresh(generation)
    
    try:
        video_content = await video.read()
        
        result = await client.generate_vid_rmbg(
            video=video_content,
            model=model,
            video_filename=video.filename
        )
        
        data = result.get("data", {})
        generation.uuid = data.get("request_id")
        generation.status = "processing"
        
        db.commit()
        db.refresh(generation)
        
        background_tasks.add_task(poll_for_result, generation.uuid, generation.id)
        
        return generation
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        generation.status = "failed"
        generation.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# VIDEO REPLACE (WAN 2.2 ANIMATE)
# ============================================================

@router.post("/generate/video-replace", response_model=GenerationResponse)
async def create_video_replace(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
    character_image: UploadFile = File(...),
    prompt: str = Form(""),
    model: str = Form("Wan_2_2_14B_Animate_Replace"),
    width: int = Form(None),
    height: int = Form(None),
    steps: int = Form(4),
    seed: int = Form(-1),
    db: Session = Depends(get_db)
):
    """
    Replace a person in a video with a character from a reference image using WAN 2.2 Animate.
    
    This endpoint uses the WAN 2.2 Animate model to:
    - Extract body motion and facial expressions from the input video
    - Replace the person with your character image
    - Apply relighting to match the scene
    - Preserve background, camera movement, and scene lighting
    
    Input:
    - video: Video file with a person whose movements you want to copy
    - character_image: Clear image of the character to insert
    - prompt: Optional text prompt to guide the replacement
    
    Output:
    - Video with the character performing all actions from the original video
    """
    client = get_deapi_client()
    
    # Generate random seed if not provided
    actual_seed = get_seed(seed)
    
    # Create pending record
    generation = Generation(
        prompt=prompt or "Video character replacement",
        model=model,
        generation_type="video-replace",
        width=width,
        height=height,
        steps=steps,
        seed=actual_seed,
        status="pending",
        progress=0
    )
    db.add(generation)
    db.commit()
    db.refresh(generation)
    
    try:
        # Validate video file
        if not video.content_type or not video.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="Video file must be a video format (mp4, mov, avi, etc.)")
        
        # Validate character image
        if not character_image.content_type or not character_image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Character image must be an image file (jpg, png, webp)")
        
        # Read files
        video_content = await video.read()
        image_content = await character_image.read()
        
        # Call deAPI video-replace endpoint
        result = await client.generate_video_replace(
            video=video_content,
            character_image=image_content,
            prompt=prompt,
            model=model,
            width=width,
            height=height,
            steps=steps,
            seed=actual_seed,
            video_filename=video.filename,
            image_filename=character_image.filename
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


# ============================================================
# PROMPT ENHANCEMENT
# ============================================================

@router.post("/prompt/enhance/image", response_model=PromptEnhanceResponse)
async def enhance_prompt_image(request: PromptEnhanceRequest):
    """Enhance a prompt for image generation."""
    client = get_deapi_client()
    
    try:
        result = await client.enhance_prompt_image(prompt=request.prompt)
        data = result.get("data", {})
        return PromptEnhanceResponse(enhanced_prompt=data.get("enhanced_prompt", request.prompt))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prompt/enhance/video", response_model=PromptEnhanceResponse)
async def enhance_prompt_video(request: PromptEnhanceRequest):
    """Enhance a prompt for video generation."""
    client = get_deapi_client()
    
    try:
        result = await client.enhance_prompt_video(prompt=request.prompt)
        data = result.get("data", {})
        return PromptEnhanceResponse(enhanced_prompt=data.get("enhanced_prompt", request.prompt))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prompt/enhance/speech", response_model=PromptEnhanceResponse)
async def enhance_prompt_speech(request: PromptEnhanceRequest):
    """Enhance a prompt for speech generation."""
    client = get_deapi_client()
    
    try:
        result = await client.enhance_prompt_speech(prompt=request.prompt)
        data = result.get("data", {})
        return PromptEnhanceResponse(enhanced_prompt=data.get("enhanced_prompt", request.prompt))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prompt/samples")
async def get_sample_prompts():
    """Get sample prompts for inspiration."""
    client = get_deapi_client()
    
    try:
        result = await client.get_sample_prompts()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# GENERATION LISTING
# ============================================================

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
    
    # Only check deAPI for processing/pending generations (not completed/failed)
    if generation.status in ("processing", "pending") and generation.uuid:
        client = get_deapi_client()
        try:
            status = await client.get_request_status(generation.uuid)
            data = status.get("data", {})
            
            if data.get("status") == "done":
                remote_url = data.get("result_url") or data.get("download_url")
                if remote_url:
                    generation.remote_url = remote_url
                    generation.status = "completed"
                    generation.progress = 100
                    generation.completed_at = datetime.now(timezone.utc)
                    
                    # Download media locally
                    from ..utils.media import download_media
                    local_path, local_url = await download_media(
                        remote_url,
                        generation.id,
                        generation.generation_type
                    )
                    if local_path:
                        generation.local_path = local_path
                    
                    db.commit()
                    db.refresh(generation)
            elif data.get("status") == "error":
                generation.status = "failed"
                generation.error_message = data.get("error", "Generation failed")
                db.commit()
        except Exception as e:
            error_str = str(e)
            print(f"[Status] Error checking status: {e}")
            # If 404, the request doesn't exist on deAPI - mark as failed
            if "404" in error_str or "Not Found" in error_str:
                generation.status = "failed"
                generation.error_message = "Request expired or not found on remote server"
                db.commit()
                print(f"[Status] Marked generation {generation_id} as failed due to 404")
    
    return generation


@router.post("/generations/{generation_id}/refresh-url", response_model=GenerationResponse)
async def refresh_generation_url(
    generation_id: int,
    db: Session = Depends(get_db)
):
    """Refresh the URL for a completed generation by checking deAPI status.
    
    Use this when S3 signed URLs have expired.
    Also downloads and saves media locally if not already saved.
    """
    generation = db.query(Generation).filter(
        Generation.id == generation_id
    ).first()
    
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    if not generation.uuid:
        raise HTTPException(status_code=400, detail="No request_id stored for this generation")
    
    if generation.status != "completed":
        raise HTTPException(status_code=400, detail="Generation is not completed")
    
    # Fetch fresh status from deAPI
    client = get_deapi_client()
    try:
        status = await client.get_request_status(generation.uuid)
        data = status.get("data", {})
        
        if data.get("status") == "done":
            new_url = data.get("result_url") or data.get("download_url")
            if new_url:
                generation.remote_url = new_url
                
                # Download and save locally if not already saved
                if not generation.local_path:
                    from ..utils.media import download_and_save_media
                    local_path = await download_and_save_media(
                        new_url,
                        generation.generation_type,
                        generation.id
                    )
                    if local_path:
                        generation.local_path = local_path
                
                db.commit()
                db.refresh(generation)
        
        return generation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh URL: {str(e)}")


# ============================================================
# LOCAL MEDIA SERVING
# ============================================================

@router.get("/media/{generation_type}/{filename}")
async def serve_local_media(
    generation_type: str,
    filename: str
):
    """Serve locally stored media files.
    
    Args:
        generation_type: Type of generation (text2img, txt2video, etc.)
        filename: The media filename
    """
    from fastapi.responses import FileResponse
    import os
    
    # Construct the path to the media file
    media_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "media")
    file_path = os.path.join(media_dir, generation_type, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Media file not found")
    
    # Determine content type based on extension
    ext = os.path.splitext(filename)[1].lower()
    content_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.webp': 'image/webp',
        '.gif': 'image/gif',
        '.mp4': 'video/mp4',
        '.webm': 'video/webm',
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav'
    }
    media_type = content_types.get(ext, 'application/octet-stream')
    
    return FileResponse(
        file_path,
        media_type=media_type,
        filename=filename
    )


# ============================================================
# TRANSCRIPTION LISTING
# ============================================================

@router.get("/transcriptions", response_model=dict)
async def list_transcriptions(
    page: int = 1,
    per_page: int = 10,
    source_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all transcriptions with pagination."""
    offset = (page - 1) * per_page
    
    query = db.query(Transcription).filter(Transcription.status != 'failed')
    
    if source_type:
        query = query.filter(Transcription.source_type == source_type)
    
    total = query.count()
    transcriptions = query.order_by(
        Transcription.created_at.desc()
    ).offset(offset).limit(per_page).all()
    
    return {
        "items": [TranscriptionResponse.model_validate(t) for t in transcriptions],
        "total": total,
        "page": page,
        "pages": ceil(total / per_page) if total > 0 else 1
    }


@router.get("/transcriptions/{transcription_id}", response_model=TranscriptionResponse)
async def get_transcription(
    transcription_id: int,
    db: Session = Depends(get_db)
):
    """Get a single transcription by ID."""
    transcription = db.query(Transcription).filter(
        Transcription.id == transcription_id
    ).first()
    
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    return transcription


@router.get("/transcriptions/{transcription_id}/status", response_model=TranscriptionResponse)
async def get_transcription_status(
    transcription_id: int,
    db: Session = Depends(get_db)
):
    """Get the current status of a transcription (for polling)."""
    transcription = db.query(Transcription).filter(
        Transcription.id == transcription_id
    ).first()
    
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    return transcription


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


# ============================================================
# NANOBANANA IMAGE GENERATION
# ============================================================

@router.post("/generate/nanobanana", response_model=NanoBananaResponse)
async def create_nanobanana_image(request: NanoBananaRequest):
    """Generate an image using Nano Banana API (no credits required, guest mode)."""
    from ..services.nanobanana import get_nanobanana_client, NanoBananaModel, AspectRatio
    
    client = get_nanobanana_client()
    
    # Validate model
    try:
        model = NanoBananaModel(request.model)
    except ValueError:
        model = NanoBananaModel.NANO_BANANA_2
    
    # Validate aspect ratio
    try:
        aspect_ratio = AspectRatio(request.aspect_ratio)
    except ValueError:
        aspect_ratio = AspectRatio.SQUARE
    
    # Start generation and wait for result
    result = await client.generate_and_wait(
        prompt=request.prompt,
        model=model,
        aspect_ratio=aspect_ratio,
        reference_images=request.reference_images,
        max_wait_seconds=120,
        poll_interval=5
    )
    
    return NanoBananaResponse(
        task_id=result.task_id or "",
        status=result.status or ("success" if result.success else "failed"),
        image_urls=result.image_urls,
        error=result.error
    )


@router.post("/generate/nanobanana/start")
async def start_nanobanana_image(request: NanoBananaRequest):
    """Start a Nano Banana image generation (returns task ID for polling)."""
    from ..services.nanobanana import get_nanobanana_client, NanoBananaModel, AspectRatio
    
    client = get_nanobanana_client()
    
    try:
        model = NanoBananaModel(request.model)
    except ValueError:
        model = NanoBananaModel.NANO_BANANA_2
    
    try:
        aspect_ratio = AspectRatio(request.aspect_ratio)
    except ValueError:
        aspect_ratio = AspectRatio.SQUARE
    
    result = await client.generate_image(
        prompt=request.prompt,
        model=model,
        aspect_ratio=aspect_ratio,
        reference_images=request.reference_images
    )
    
    return {
        "success": result.success,
        "task_id": result.task_id,
        "status": result.status,
        "error": result.error
    }


@router.post("/generate/nanobanana/query")
async def query_nanobanana_task(task_id: str = Form(...), prompt: str = Form(...)):
    """Query the status of a Nano Banana generation task."""
    from ..services.nanobanana import get_nanobanana_client
    
    client = get_nanobanana_client()
    result = await client.query_task(task_id, prompt)
    
    return {
        "success": result.success,
        "task_id": result.task_id,
        "status": result.status,
        "image_urls": result.image_urls,
        "error": result.error
    }


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
