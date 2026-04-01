"""
UGC AI Ads Creator API Routes

API endpoints for creating UGC-style video ads:
- Prompt search and matching
- Story generation with scenes and shots
- Image generation for shots (Flux2/KLIE HD)
- Video generation for shots (LTX-2.3)
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import Optional, List
import asyncio
import json
import logging
import aiohttp

from ..database import get_db
from ..models import UgcAdStory, UgcScene, UgcShot, Generation
from ..schemas import (
    PromptSearchRequest,
    PromptSearchResponse,
    PromptMatchData,
    UgcStoryCreate,
    UgcStoryResponse,
    UgcStoryListResponse,
    UgcStoryGenerateRequest,
    UgcShotData,
    UgcSceneData,
    UgcShotRegenerateRequest,
    UgcShotRegenerateResponse
)
from ..services.prompt_matcher import get_prompt_matcher, PromptMatcher
from ..services.ugc_story_generator import (
    get_ugc_story_generator,
    UGCStoryGenerator
)
from ..services.deapi import get_deapi_client

router = APIRouter(prefix="/api/ugc-ads", tags=["ugc-ads"])
logger = logging.getLogger("ugc_ads")


# ==============================================================================
# PROMPT SEARCH
# ==============================================================================

@router.post("/prompts/search", response_model=PromptSearchResponse)
async def search_prompts(request: PromptSearchRequest):
    """
    Search for relevant prompts from the nanobanana marketing library.
    
    Matches prompts based on product type, category, mood, and keywords.
    Returns a list of matched prompts with relevance scores.
    """
    matcher = get_prompt_matcher()
    
    matches = matcher.search(
        query=request.query,
        product_type=request.product_type,
        category=request.category,
        mood=request.mood,
        limit=request.limit
    )
    
    # Detect category and mood
    detected_category = matcher._detect_category(request.query)
    detected_mood = matcher._detect_mood(request.query)
    
    return PromptSearchResponse(
        query=request.query,
        detected_category=detected_category,
        detected_mood=detected_mood,
        matches=[
            PromptMatchData(
                id=m.id,
                prompt=m.prompt,
                title=m.title,
                tags=m.tags,
                model=m.model,
                image_url=m.image_url,
                relevance_score=m.relevance_score,
                match_reason=m.match_reason
            )
            for m in matches
        ],
        total=len(matches)
    )


@router.get("/prompts/{prompt_id}")
async def get_prompt(prompt_id: str):
    """Get a specific prompt by ID from the library."""
    matcher = get_prompt_matcher()
    match = matcher.get_prompt_by_id(prompt_id)
    
    if not match:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    return PromptMatchData(
        id=match.id,
        prompt=match.prompt,
        title=match.title,
        tags=match.tags,
        model=match.model,
        image_url=match.image_url,
        relevance_score=match.relevance_score,
        match_reason=match.match_reason
    )


# ==============================================================================
# STORY MANAGEMENT
# ==============================================================================

@router.post("/stories", response_model=UgcStoryResponse)
async def create_story(
    request: UgcStoryCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new UGC ad story.
    
    This endpoint:
    1. Searches for matching prompts from the library
    2. Generates a complete story with scenes and shots
    3. Returns the story structure (without generated images/videos yet)
    """
    # Create story record
    story = UgcAdStory(
        story_id=f"ugc_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        title=f"{request.product_name} UGC Ad",
        product_name=request.product_name,
        product_category=request.product_category,
        product_description=request.product_description,
        target_platform=request.platform,
        hook="",
        cta="",
        status="generating"
    )
    
    if request.character_reference_url:
        story.character_reference_url = request.character_reference_url
    if request.product_reference_url:
        story.product_reference_url = request.product_reference_url
    
    db.add(story)
    db.commit()
    db.refresh(story)
    
    try:
        # Step 1: Search for matching prompts
        matcher = get_prompt_matcher()
        matches = matcher.search(
            query=f"{request.product_name} {request.product_description}",
            product_type=request.product_category,
            limit=5
        )
        
        inspiration_prompts = [
            {
                "id": m.id,
                "prompt": m.prompt,
                "title": m.title,
                "image_url": m.image_url,
                "relevance_score": m.relevance_score
            }
            for m in matches
        ]
        story.inspiration_prompts = inspiration_prompts
        
        # Step 2: Generate story with scenes and shots
        generator = get_ugc_story_generator()
        
        # Build character data if provided
        character_data = None
        if request.character_name or request.character_description:
            character_data = {
                "name": request.character_name or "Alex",
                "description": request.character_description or ""
            }
        
        ugc_story = await generator.generate_story(
            product_name=request.product_name,
            product_description=request.product_description,
            product_category=request.product_category or "product",
            character_name=request.character_name,
            character_description=request.character_description,
            target_audience=request.target_audience,
            platform=request.platform,
            ad_goal=request.ad_goal,
            tone=request.tone,
            setting_preference=request.setting_preference,
            inspiration_prompts=inspiration_prompts
        )
        
        # Update story with generated content
        story.title = ugc_story.title
        story.hook = ugc_story.hook
        story.cta = ugc_story.cta
        story.setting_description = ugc_story.setting
        story.characters = [
            {
                "name": c.name,
                "role": c.role,
                "age": c.age,
                "gender": c.gender,
                "appearance": c.appearance,
                "outfit": c.outfit,
                "personality": c.personality
            }
            for c in ugc_story.characters
        ]
        story.product_key_features = ugc_story.product.key_features
        story.product_visual_description = ugc_story.product.visual_description
        
        # Create scenes and shots
        for scene_data in ugc_story.scenes:
            scene = UgcScene(
                story_id=story.id,
                scene_num=scene_data.scene_num,
                scene_name=scene_data.scene_name,
                setting=scene_data.setting,
                mood=scene_data.mood
            )
            db.add(scene)
            db.flush()  # Get scene ID
            
            for shot_data in scene_data.shots:
                # Generate image and video prompts
                character = ugc_story.characters[0] if ugc_story.characters else None
                if character:
                    image_prompt = generator.generate_image_prompt_for_shot(
                        shot_data, character, ugc_story.product
                    )
                    video_prompt = generator.generate_video_prompt_for_shot(
                        shot_data, character, ugc_story.product
                    )
                else:
                    image_prompt = shot_data.frame_description
                    video_prompt = f"Natural motion, {shot_data.action}"
                
                shot = UgcShot(
                    scene_id=scene.id,
                    shot_num=shot_data.shot_num,
                    duration_sec=shot_data.duration_sec,
                    frame_description=shot_data.frame_description,
                    action=shot_data.action,
                    dialogue=shot_data.dialogue,
                    camera_angle=shot_data.camera_angle,
                    lighting=shot_data.lighting,
                    audio_notes=shot_data.audio_notes,
                    first_frame_prompt=image_prompt,
                    video_prompt=video_prompt
                )
                db.add(shot)
        
        story.status = "draft"
        db.commit()
        db.refresh(story)
        
    except Exception as e:
        story.status = "failed"
        story.error_message = str(e)
        db.commit()
        logger.exception(f"Failed to generate story: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate story: {str(e)}")
    
    return _build_story_response(story, db)


@router.get("/stories", response_model=UgcStoryListResponse)
async def list_stories(
    page: int = 1,
    per_page: int = 10,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all UGC ad stories."""
    offset = (page - 1) * per_page
    
    query = db.query(UgcAdStory)
    if status:
        query = query.filter(UgcAdStory.status == status)
    
    total = query.count()
    stories = query.order_by(desc(UgcAdStory.created_at))\
        .offset(offset)\
        .limit(per_page)\
        .all()
    
    pages = (total + per_page - 1) // per_page
    
    return UgcStoryListResponse(
        items=[_build_story_response(s, db) for s in stories],
        total=total,
        page=page,
        pages=pages
    )


@router.get("/stories/{story_id}", response_model=UgcStoryResponse)
async def get_story(story_id: int, db: Session = Depends(get_db)):
    """Get a specific UGC ad story with all scenes and shots."""
    story = db.query(UgcAdStory).filter(UgcAdStory.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    return _build_story_response(story, db)


@router.delete("/stories/{story_id}")
async def delete_story(story_id: int, db: Session = Depends(get_db)):
    """Delete a UGC ad story and all its scenes and shots."""
    story = db.query(UgcAdStory).filter(UgcAdStory.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    db.delete(story)
    db.commit()
    return {"message": "Story deleted", "story_id": story_id}


# ==============================================================================
# GENERATION PIPELINE
# ==============================================================================

@router.post("/stories/{story_id}/generate")
async def generate_story_assets(
    story_id: int,
    request: UgcStoryGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Generate images and videos for all shots in a story.
    
    This starts a background task that:
    1. Generates first frame images using Flux2/KLIE HD
    2. Generates videos using LTX-2.3
    """
    story = db.query(UgcAdStory).filter(UgcAdStory.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    story.status = "generating"
    db.commit()
    
    # Start background generation
    background_tasks.add_task(
        _generate_assets_task,
        story_id,
        request.generate_images,
        request.generate_videos,
        request.model,
        request.video_model,
        request.aspect_ratio
    )
    
    return {
        "message": "Generation started",
        "story_id": story_id,
        "generate_images": request.generate_images,
        "generate_videos": request.generate_videos
    }


async def _poll_deapi_result(deapi, request_id: str, max_polls: int = 30) -> Optional[str]:
    """Poll deAPI for result URL with exponential backoff."""
    import asyncio
    
    min_delay = 5
    max_delay = 15
    
    for poll_count in range(max_polls):
        delay = min(min_delay + poll_count, max_delay)
        await asyncio.sleep(delay)
        
        try:
            result = await deapi.get_request_status(request_id)
            data = result.get("data", {})
            status = data.get("status")
            
            logger.info(f"[Poll] request_id={request_id} status={status}")
            
            if status == "done":
                return data.get("result_url")
            elif status == "error":
                raise Exception(data.get("error", "Generation failed"))
                
        except Exception as e:
            if "404" in str(e):
                raise Exception("Request expired or not found")
            raise
    
    raise Exception("Generation timed out")


async def _generate_assets_task(
    story_id: int,
    generate_images: bool,
    generate_videos: bool,
    image_model: str,
    video_model: str,
    aspect_ratio: str
):
    """Background task to generate all shot assets."""
    from ..database import SessionLocal
    
    db = SessionLocal()
    try:
        story = db.query(UgcAdStory).filter(UgcAdStory.id == story_id).first()
        if not story:
            logger.error(f"Story {story_id} not found")
            return
        
        deapi = get_deapi_client()
        
        # Get all shots
        shots = db.query(UgcShot).join(UgcScene).filter(
            UgcScene.story_id == story_id
        ).order_by(UgcScene.scene_num, UgcShot.shot_num).all()
        
        logger.info(f"Found {len(shots)} shots for story {story_id}")
        
        # Parse aspect ratio
        width, height = _parse_aspect_ratio(aspect_ratio)
        
        # Generate images - deAPI is async, need to poll for results
        if generate_images:
            for shot in shots:
                if shot.first_frame_prompt:
                    try:
                        shot.first_frame_status = "processing"
                        db.commit()
                        
                        logger.info(f"Submitting image generation for shot {shot.id}")
                        
                        result = await deapi.generate_text2img(
                            prompt=shot.first_frame_prompt,
                            model=image_model,
                            width=width,
                            height=height
                        )
                        
                        # deAPI returns request_id, not direct URL
                        request_id = result.get("request_id") or result.get("data", {}).get("request_id")
                        
                        if not request_id:
                            raise Exception(f"No request_id in response: {result}")
                        
                        logger.info(f"Shot {shot.id} image request_id: {request_id}")
                        
                        # Poll for result
                        image_url = await _poll_deapi_result(deapi, request_id)
                        
                        if image_url:
                            shot.first_frame_url = image_url
                            shot.first_frame_status = "completed"
                            logger.info(f"Generated image for shot {shot.id}: {image_url[:50]}...")
                        else:
                            shot.first_frame_status = "failed"
                            shot.error_message = "No URL in result"
                        
                        db.commit()
                        
                    except Exception as e:
                        shot.first_frame_status = "failed"
                        shot.error_message = str(e)
                        db.commit()
                        logger.error(f"Failed to generate image for shot {shot.id}: {e}")
        
        # Generate videos
        if generate_videos:
            async with aiohttp.ClientSession() as http_session:
                for shot in shots:
                    if shot.first_frame_url and shot.video_prompt:
                        try:
                            shot.video_status = "processing"
                            db.commit()
                            
                            logger.info(f"Submitting video generation for shot {shot.id}")
                            
                            # Fetch image from URL and convert to bytes
                            async with http_session.get(shot.first_frame_url) as img_response:
                                img_response.raise_for_status()
                                image_bytes = await img_response.read()
                            
                            result = await deapi.generate_img2video(
                                first_frame_image=image_bytes,
                                prompt=shot.video_prompt,
                                model=video_model,
                                width=max(512, width),
                                height=max(512, height),
                                frames=_calculate_frames(shot.duration_sec)
                            )
                            
                            request_id = result.get("request_id") or result.get("data", {}).get("request_id")
                            
                            if not request_id:
                                raise Exception(f"No request_id in response: {result}")
                            
                            logger.info(f"Shot {shot.id} video request_id: {request_id}")
                            
                            # Poll for result
                            video_url = await _poll_deapi_result(deapi, request_id, max_polls=40)
                            
                            if video_url:
                                shot.video_url = video_url
                                shot.video_status = "completed"
                                logger.info(f"Generated video for shot {shot.id}")
                            else:
                                shot.video_status = "failed"
                                shot.error_message = "No URL in result"
                            
                            db.commit()
                            
                        except Exception as e:
                            shot.video_status = "failed"
                            shot.error_message = str(e)
                            db.commit()
                            logger.error(f"Failed to generate video for shot {shot.id}: {e}")
        
        # Update story status
        all_shots = db.query(UgcShot).join(UgcScene).filter(
            UgcScene.story_id == story_id
        ).all()
        
        images_done = all(s.first_frame_status == "completed" for s in all_shots if s.first_frame_prompt)
        videos_done = all(s.video_status == "completed" for s in all_shots if s.video_prompt)
        
        if images_done and videos_done:
            story.status = "completed"
            story.completed_at = datetime.utcnow()
        else:
            story.status = "partial"
        
        db.commit()
        logger.info(f"Story {story_id} generation complete: status={story.status}")
        
    except Exception as e:
        logger.exception(f"Generation task failed: {e}")
    finally:
        db.close()


@router.post("/stories/{story_id}/shots/regenerate", response_model=UgcShotRegenerateResponse)
async def regenerate_shot(
    story_id: int,
    request: UgcShotRegenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Regenerate a specific shot's image and/or video.
    
    Optionally provide a custom prompt to override the generated one.
    """
    story = db.query(UgcAdStory).filter(UgcAdStory.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    shot = db.query(UgcShot).filter(UgcShot.id == request.shot_id).first()
    if not shot:
        raise HTTPException(status_code=404, detail="Shot not found")
    
    deapi = get_deapi_client()
    
    response = UgcShotRegenerateResponse(
        shot_id=shot.id,
        first_frame_status=shot.first_frame_status,
        video_status=shot.video_status,
        first_frame_url=shot.first_frame_url,
        video_url=shot.video_url
    )
    
    try:
        # Regenerate image
        if request.regenerate_image:
            prompt = request.custom_prompt or shot.first_frame_prompt
            if prompt:
                shot.first_frame_status = "processing"
                db.commit()
                
                result = await deapi.generate_text2img(
                    prompt=prompt,
                    model="Flux_2_Klein_4B_BF16",
                    width=1024,
                    height=576
                )
                
                request_id = result.get("request_id") or result.get("data", {}).get("request_id")
                
                if request_id:
                    image_url = await _poll_deapi_result(deapi, request_id)
                    if image_url:
                        shot.first_frame_url = image_url
                        shot.first_frame_status = "completed"
                        response.first_frame_status = "completed"
                        response.first_frame_url = shot.first_frame_url
                    else:
                        shot.first_frame_status = "failed"
                        shot.error_message = "No URL in result"
                else:
                    shot.first_frame_status = "failed"
                    shot.error_message = f"No request_id in response"
                
                db.commit()
        
        # Regenerate video
        if request.regenerate_video and shot.first_frame_url:
            shot.video_status = "processing"
            db.commit()
            
            # Fetch image and convert to bytes
            async with aiohttp.ClientSession() as http_session:
                async with http_session.get(shot.first_frame_url) as img_response:
                    img_response.raise_for_status()
                    image_bytes = await img_response.read()
            
            result = await deapi.generate_img2video(
                first_frame_image=image_bytes,
                prompt=shot.video_prompt or "Natural motion",
                model="Ltx2_3_22B_Dist_INT8",
                width=768,
                height=768,
                frames=120
            )
            
            request_id = result.get("request_id") or result.get("data", {}).get("request_id")
            
            if request_id:
                video_url = await _poll_deapi_result(deapi, request_id, max_polls=40)
                if video_url:
                    shot.video_url = video_url
                    shot.video_status = "completed"
                    response.video_status = "completed"
                    response.video_url = shot.video_url
                else:
                    shot.video_status = "failed"
                    shot.error_message = "No URL in result"
            else:
                shot.video_status = "failed"
                shot.error_message = "No request_id in response"
            
            db.commit()
    
    except Exception as e:
        if request.regenerate_image:
            shot.first_frame_status = "failed"
        if request.regenerate_video:
            shot.video_status = "failed"
        shot.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))
    
    return response


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def _build_story_response(story: UgcAdStory, db: Session) -> UgcStoryResponse:
    """Build a UgcStoryResponse from a UgcAdStory model."""
    scenes = db.query(UgcScene).filter(
        UgcScene.story_id == story.id
    ).order_by(UgcScene.scene_num).all()
    
    scene_data = []
    for scene in scenes:
        shots = db.query(UgcShot).filter(
            UgcShot.scene_id == scene.id
        ).order_by(UgcShot.shot_num).all()
        
        scene_data.append(UgcSceneData(
            id=scene.id,
            scene_num=scene.scene_num,
            scene_name=scene.scene_name,
            setting=scene.setting,
            mood=scene.mood,
            shots=[
                UgcShotData(
                    id=s.id,
                    shot_num=s.shot_num,
                    duration_sec=s.duration_sec,
                    frame_description=s.frame_description,
                    action=s.action,
                    dialogue=s.dialogue,
                    camera_angle=s.camera_angle,
                    lighting=s.lighting,
                    audio_notes=s.audio_notes,
                    first_frame_prompt=s.first_frame_prompt,
                    first_frame_url=s.first_frame_url,
                    first_frame_status=s.first_frame_status,
                    last_frame_prompt=s.last_frame_prompt,
                    last_frame_url=s.last_frame_url,
                    last_frame_status=s.last_frame_status,
                    video_prompt=s.video_prompt,
                    video_url=s.video_url,
                    video_status=s.video_status,
                    error_message=s.error_message
                )
                for s in shots
            ]
        ))
    
    return UgcStoryResponse(
        id=story.id,
        story_id=story.story_id,
        title=story.title,
        target_platform=story.target_platform,
        total_duration_sec=story.total_duration_sec or 15,
        hook=story.hook,
        cta=story.cta,
        setting_description=story.setting_description,
        characters=story.characters or [],
        product_name=story.product_name,
        product_category=story.product_category,
        product_description=story.product_description,
        product_key_features=story.product_key_features or [],
        product_visual_description=story.product_visual_description,
        character_reference_url=story.character_reference_url,
        product_reference_url=story.product_reference_url,
        inspiration_prompts=story.inspiration_prompts or [],
        status=story.status,
        error_message=story.error_message,
        scenes=scene_data,
        created_at=story.created_at,
        updated_at=story.updated_at,
        completed_at=story.completed_at
    )


def _parse_aspect_ratio(aspect_ratio: str) -> tuple:
    """Parse aspect ratio string to width and height."""
    ratios = {
        "1:1": (1024, 1024),
        "16:9": (1024, 576),
        "9:16": (576, 1024),
        "4:3": (1024, 768),
        "3:4": (768, 1024),
        "4:5": (896, 1120),
        "5:4": (1120, 896),
    }
    return ratios.get(aspect_ratio, (1024, 576))


def _calculate_frames(duration_sec: int) -> int:
    """Calculate number of frames for a duration (24 fps)."""
    # LTX-2.3 requires minimum 49 frames, max 241
    frames = duration_sec * 24
    return max(49, min(241, frames))
