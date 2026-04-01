"""
AI Ads Generator Routes - Multi-Phase Agentic Workflow

API endpoints for the conversational AI Ads Generator:
- Phase 1: Generate clarification questions
- Phase 2: Build context from answers
- Phase 3: Generate ad strategy/angles
- Phase 4: Generate UGC scripts
- Phase 5: Generate UGC avatars
- Phase 6: Generate storyboards
- Phase 7-8: Generate image/video prompts
- Phase 9: Get batch output
- Phase 10: Iteration mode
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
import asyncio
import json
from typing import Optional, List

from ..database import get_db
from ..models import AdCampaign, AdAvatar, AdScript, AdStoryboard, AdScenePrompt, AdConversation
from ..schemas import (
    AdCampaignCreate,
    AdCampaignResponse,
    AdCampaignListResponse,
    AdCampaignDetailResponse,
    AdAvatarData,
    ScenePromptData,
    StoryboardDetailData,
    ClarificationAnswersRequest,
    ClarificationQuestionsResponse,
    ScriptsGenerateRequest,
    ScriptsResponse,
    IterationRequest,
    IterationResponse
)
from ..services.ads_pipeline import (
    generate_clarification_questions,
    build_context,
    generate_ad_strategy,
    generate_scripts,
    generate_avatars,
    generate_storyboard,
    generate_image_prompts,
    generate_video_prompts,
    generate_batch_output,
    apply_iteration,
    get_pipeline_client,
    _add_debug_log
)
from ..services.nanobanana import get_nanobanana_client, NanoBananaModel, AspectRatio

router = APIRouter(prefix="/api", tags=["ads"])


# ==============================================================================
# CAMPAIGN MANAGEMENT
# ==============================================================================

@router.post("/ads/campaigns", response_model=AdCampaignResponse)
async def create_campaign(
    request: AdCampaignCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new ad campaign and start Phase 1: Generate clarification questions.
    
    The AI will analyze the user's brief and ask 3-5 clarification questions
    before generating any content.
    """
    # Create campaign record
    campaign = AdCampaign(
        user_prompt=request.user_prompt,
        current_phase=1,
        phase_status="processing"
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    
    # Store initial conversation
    conversation = AdConversation(
        campaign_id=campaign.id,
        role="user",
        phase=1,
        content=request.user_prompt,
        message_type="brief"
    )
    db.add(conversation)
    
    # Store brand info in context if provided
    if request.brand_name or request.brand_description:
        campaign.context = {
            "brand": request.brand_name or "",
            "product": request.brand_description or ""
        }
    
    db.commit()
    
    # Generate clarification questions
    result = await generate_clarification_questions(request.user_prompt)
    
    if "error" in result:
        campaign.phase_status = "failed"
        campaign.error_message = result.get("error", "Failed to generate questions")
        db.commit()
        return campaign
    
    # Store questions
    campaign.clarification_questions = result.get("questions", [])
    campaign.phase_status = "completed"
    db.commit()
    
    # Store AI response
    ai_conversation = AdConversation(
        campaign_id=campaign.id,
        role="assistant",
        phase=1,
        content=json.dumps(result.get("questions", [])),
        message_type="questions"
    )
    db.add(ai_conversation)
    db.commit()
    
    return campaign


@router.get("/ads/campaigns", response_model=AdCampaignListResponse)
async def list_campaigns(
    page: int = 1,
    per_page: int = 10,
    db: Session = Depends(get_db)
):
    """List all ad campaigns."""
    offset = (page - 1) * per_page
    
    total = db.query(AdCampaign).count()
    campaigns = db.query(AdCampaign)\
        .order_by(desc(AdCampaign.created_at))\
        .offset(offset)\
        .limit(per_page)\
        .all()
    
    pages = (total + per_page - 1) // per_page
    
    return AdCampaignListResponse(
        items=campaigns,
        total=total,
        page=page,
        pages=pages
    )


@router.get("/ads/campaigns/{campaign_id}", response_model=AdCampaignResponse)
async def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific campaign."""
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.get("/ads/campaigns/{campaign_id}/detail", response_model=AdCampaignDetailResponse)
async def get_campaign_detail(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Get full campaign details with avatars, scripts, storyboards, and scene assets."""
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    avatars = db.query(AdAvatar).filter(AdAvatar.campaign_id == campaign_id).all()
    scripts = db.query(AdScript).filter(AdScript.campaign_id == campaign_id).all()
    storyboards = db.query(AdStoryboard).filter(AdStoryboard.campaign_id == campaign_id).all()

    response = AdCampaignDetailResponse.from_orm(campaign)
    response.avatars = [AdAvatarData.from_orm(a) for a in avatars]
    response.scripts = [{
        "id": s.id,
        "script_id": s.script_id,
        "hook": s.hook,
        "cta": s.cta,
        "framework": s.framework,
        "scenes": s.scenes
    } for s in scripts]
    response.storyboards = []

    for storyboard in storyboards:
        scene_prompts = db.query(AdScenePrompt).filter(
            AdScenePrompt.storyboard_id == storyboard.id
        ).order_by(AdScenePrompt.scene_num.asc()).all()

        response.storyboards.append(StoryboardDetailData(
            id=storyboard.id,
            script_id=storyboard.script_id,
            scenes=storyboard.scenes or [],
            scene_prompts=[
                ScenePromptData(
                    id=scene_prompt.id,
                    scene_num=scene_prompt.scene_num,
                    image_prompt=scene_prompt.image_prompt,
                    video_prompt=scene_prompt.video_prompt,
                    image_generation_id=scene_prompt.image_generation_id,
                    video_generation_id=scene_prompt.video_generation_id,
                    image_url=scene_prompt.image_url,
                    video_url=scene_prompt.video_url,
                    image_status=scene_prompt.image_status or "pending",
                    video_status=scene_prompt.video_status or "pending"
                )
                for scene_prompt in scene_prompts
            ]
        ))

    return response


# ==============================================================================
# PHASE 1: CLARIFICATION QUESTIONS
# ==============================================================================

@router.get("/ads/campaigns/{campaign_id}/questions", response_model=ClarificationQuestionsResponse)
async def get_clarification_questions(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Get clarification questions for a campaign (Phase 1)."""
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if not campaign.clarification_questions:
        raise HTTPException(status_code=400, detail="Questions not generated yet")
    
    return ClarificationQuestionsResponse(
        campaign_id=campaign_id,
        phase=1,
        questions=campaign.clarification_questions
    )


# ==============================================================================
# PHASE 2: BUILD CONTEXT
# ==============================================================================

@router.post("/ads/campaigns/{campaign_id}/answers", response_model=AdCampaignResponse)
async def submit_answers(
    campaign_id: int,
    request: ClarificationAnswersRequest,
    db: Session = Depends(get_db)
):
    """
    Submit answers to clarification questions (Phase 2).
    
    The AI will build structured context from the answers and proceed to
    generate ad strategy.
    """
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Store user answers
    answers_list = [a.dict() for a in request.answers]
    campaign.user_answers = answers_list
    campaign.current_phase = 2
    campaign.phase_status = "processing"
    db.commit()
    
    # Store conversation
    conversation = AdConversation(
        campaign_id=campaign.id,
        role="user",
        phase=2,
        content=json.dumps(answers_list),
        message_type="answers"
    )
    db.add(conversation)
    db.commit()
    
    # Build context
    result = await build_context(
        campaign.user_prompt,
        answers_list
    )
    
    if "error" in result:
        campaign.phase_status = "failed"
        campaign.error_message = result["error"]
        db.commit()
        raise HTTPException(status_code=500, detail=result["error"])
    
    # Store context
    campaign.context = result
    campaign.phase_status = "completed"
    campaign.current_phase = 3
    db.commit()
    
    # Auto-proceed to Phase 3: Generate ad strategy
    strategy_result = await generate_ad_strategy(result)
    
    if "error" not in strategy_result:
        campaign.ad_angles = strategy_result.get("angles", [])
        campaign.phase_status = "completed"
        campaign.current_phase = 4
        db.commit()
    
    return campaign


# ==============================================================================
# PHASE 3: AD STRATEGY (auto-generated after context)
# ==============================================================================

@router.get("/ads/campaigns/{campaign_id}/strategy")
async def get_ad_strategy(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Get ad strategy/angles for a campaign (Phase 3)."""
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if not campaign.ad_angles:
        raise HTTPException(status_code=400, detail="Strategy not generated yet. Complete Phase 2 first.")
    
    return {
        "campaign_id": campaign_id,
        "phase": 3,
        "angles": campaign.ad_angles
    }


# ==============================================================================
# PHASE 4: SCRIPT GENERATION
# ==============================================================================

@router.post("/ads/campaigns/{campaign_id}/scripts", response_model=ScriptsResponse)
async def generate_campaign_scripts(
    campaign_id: int,
    request: ScriptsGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate UGC-style ad scripts (Phase 4).
    
    Creates multiple scripts using different hooks and frameworks.
    """
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if not campaign.context:
        raise HTTPException(status_code=400, detail="Context not built yet. Complete Phase 2 first.")
    
    campaign.current_phase = 4
    campaign.phase_status = "processing"
    campaign.scripts_status = "processing"
    campaign.num_scripts = request.num_scripts
    db.commit()
    
    # Generate scripts
    result = await generate_scripts(
        campaign.context,
        campaign.ad_angles or [],
        request.num_scripts
    )
    
    if "error" in result:
        campaign.scripts_status = "failed"
        campaign.phase_status = "failed"
        campaign.error_message = result["error"]
        db.commit()
        raise HTTPException(status_code=500, detail=result["error"])
    
    # Store scripts
    scripts_data = []
    for idx, script_data in enumerate(result.get("scripts", []), 1):
        script = AdScript(
            campaign_id=campaign_id,
            script_id=idx,
            hook=script_data.get("hook", ""),
            cta=script_data.get("cta", ""),
            framework=script_data.get("framework", ""),
            scenes=script_data.get("scenes", []),
            ad_angle_ref=script_data.get("id")
        )
        db.add(script)
        scripts_data.append({
            "id": idx,
            "hook": script.hook,
            "cta": script.cta,
            "framework": script.framework,
            "scenes": script.scenes
        })
    
    campaign.scripts_status = "completed"
    campaign.phase_status = "completed"
    campaign.current_phase = 5
    db.commit()
    
    return ScriptsResponse(
        campaign_id=campaign_id,
        phase=4,
        scripts=scripts_data
    )


# ==============================================================================
# PHASE 5: AVATAR GENERATION
# ==============================================================================

@router.post("/ads/campaigns/{campaign_id}/avatars")
async def generate_campaign_avatars(
    campaign_id: int,
    num_avatars: int = 3,
    db: Session = Depends(get_db)
):
    """
    Generate UGC character avatars (Phase 5).
    
    Creates diverse, consistent characters for the ads.
    """
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if not campaign.context:
        raise HTTPException(status_code=400, detail="Context not built yet. Complete Phase 2 first.")
    
    campaign.current_phase = 5
    campaign.phase_status = "processing"
    campaign.avatars_status = "processing"
    campaign.num_avatars = num_avatars
    db.commit()
    
    # Generate avatars
    result = await generate_avatars(
        campaign.context,
        num_avatars
    )
    
    if "error" in result:
        campaign.avatars_status = "failed"
        campaign.phase_status = "failed"
        campaign.error_message = result["error"]
        db.commit()
        raise HTTPException(status_code=500, detail=result["error"])
    
    # Store avatars
    avatars_data = []
    for avatar_data in result.get("avatars", []):
        avatar = AdAvatar(
            campaign_id=campaign_id,
            name=avatar_data.get("name", "Unknown"),
            age=avatar_data.get("age"),
            gender=avatar_data.get("gender"),
            region=avatar_data.get("region"),
            appearance=avatar_data.get("appearance", ""),
            outfit_style=avatar_data.get("outfit_style", ""),
            personality_vibe=avatar_data.get("personality_vibe", "")
        )
        db.add(avatar)
        avatars_data.append(avatar_data)
    
    campaign.avatars_status = "completed"
    campaign.phase_status = "completed"
    campaign.current_phase = 6
    db.commit()
    
    return {
        "campaign_id": campaign_id,
        "phase": 5,
        "avatars": avatars_data
    }


# ==============================================================================
# PHASE 6: STORYBOARD ENGINE
# ==============================================================================

@router.post("/ads/campaigns/{campaign_id}/storyboards")
async def generate_campaign_storyboards(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate storyboards for all scripts (Phase 6).
    
    Creates detailed scene breakdowns with visual direction.
    """
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    scripts = db.query(AdScript).filter(AdScript.campaign_id == campaign_id).all()
    avatars = db.query(AdAvatar).filter(AdAvatar.campaign_id == campaign_id).all()
    
    if not scripts:
        raise HTTPException(status_code=400, detail="No scripts generated yet. Complete Phase 4 first.")
    
    campaign.current_phase = 6
    campaign.phase_status = "processing"
    campaign.storyboards_status = "processing"
    db.commit()
    
    storyboards_data = []
    
    for script in scripts:
        # Get avatar for this script (cycle through avatars)
        avatar = avatars[(script.script_id - 1) % len(avatars)] if avatars else None
        avatar_dict = {
            "name": avatar.name,
            "age": avatar.age,
            "gender": avatar.gender,
            "appearance": avatar.appearance
        } if avatar else {}
        
        # Generate storyboard
        result = await generate_storyboard(
            {
                "hook": script.hook,
                "scenes": script.scenes,
                "cta": script.cta
            },
            avatar_dict,
            campaign.context or {}
        )
        
        if "error" not in result:
            storyboard = AdStoryboard(
                campaign_id=campaign_id,
                script_id=script.id,
                scenes=result.get("scenes", [])
            )
            db.add(storyboard)
            db.commit()
            db.refresh(storyboard)
            
            storyboards_data.append({
                "script_id": script.script_id,
                "scenes": result.get("scenes", [])
            })
    
    campaign.storyboards_status = "completed"
    campaign.phase_status = "completed"
    campaign.current_phase = 7
    db.commit()
    
    return {
        "campaign_id": campaign_id,
        "phase": 6,
        "storyboards": storyboards_data
    }


# ==============================================================================
# PHASE 7: IMAGE PROMPT GENERATION
# ==============================================================================

@router.post("/ads/campaigns/{campaign_id}/image-prompts")
async def generate_campaign_image_prompts(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate image prompts for all scenes (Phase 7).
    
    Creates detailed prompts for AI image generation.
    """
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    storyboards = db.query(AdStoryboard).filter(AdStoryboard.campaign_id == campaign_id).all()
    avatars = db.query(AdAvatar).filter(AdAvatar.campaign_id == campaign_id).all()
    
    if not storyboards:
        raise HTTPException(status_code=400, detail="No storyboards generated yet. Complete Phase 6 first.")
    
    campaign.current_phase = 7
    campaign.phase_status = "processing"
    campaign.image_prompts_status = "processing"
    db.commit()
    
    prompts_data = []
    
    for storyboard in storyboards:
        script = db.query(AdScript).filter(AdScript.id == storyboard.script_id).first()
        avatar = avatars[(script.script_id - 1) % len(avatars)] if avatars and script else None
        avatar_dict = {
            "name": avatar.name,
            "age": avatar.age,
            "appearance": avatar.appearance
        } if avatar else {}
        
        # Generate image prompts
        result = await generate_image_prompts(
            {"scenes": storyboard.scenes},
            avatar_dict,
            campaign.context or {}
        )
        
        if "error" not in result:
            for scene_prompt in result.get("scene_prompts", []):
                prompt_record = AdScenePrompt(
                    storyboard_id=storyboard.id,
                    scene_num=scene_prompt.get("scene_num", 1),
                    image_prompt=scene_prompt.get("image_prompt", "")
                )
                db.add(prompt_record)
                
                prompts_data.append({
                    "storyboard_id": storyboard.id,
                    "script_id": script.script_id if script else None,
                    "scene_num": scene_prompt.get("scene_num"),
                    "image_prompt": scene_prompt.get("image_prompt")
                })
    
    db.commit()
    
    campaign.image_prompts_status = "completed"
    campaign.phase_status = "completed"
    campaign.current_phase = 8
    db.commit()
    
    return {
        "campaign_id": campaign_id,
        "phase": 7,
        "image_prompts": prompts_data
    }


# ==============================================================================
# PHASE 8: VIDEO PROMPT GENERATION
# ==============================================================================

@router.post("/ads/campaigns/{campaign_id}/video-prompts")
async def generate_campaign_video_prompts(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate video prompts for all scenes (Phase 8).
    
    Creates prompts for img2video generation.
    """
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    storyboards = db.query(AdStoryboard).filter(AdStoryboard.campaign_id == campaign_id).all()
    
    if not storyboards:
        raise HTTPException(status_code=400, detail="No storyboards generated yet. Complete Phase 6 first.")
    
    campaign.current_phase = 8
    campaign.phase_status = "processing"
    campaign.video_prompts_status = "processing"
    db.commit()
    
    prompts_data = []
    
    for storyboard in storyboards:
        script = db.query(AdScript).filter(AdScript.id == storyboard.script_id).first()
        
        # Generate video prompts
        result = await generate_video_prompts(
            {"scenes": storyboard.scenes},
            {
                "hook": script.hook,
                "scenes": script.scenes,
                "cta": script.cta
            } if script else {},
            campaign.context or {}
        )
        
        if "error" not in result:
            # Update existing scene prompts with video prompts
            for video_prompt in result.get("video_prompts", []):
                scene_prompt = db.query(AdScenePrompt).filter(
                    AdScenePrompt.storyboard_id == storyboard.id,
                    AdScenePrompt.scene_num == video_prompt.get("scene_num", 1)
                ).first()
                
                if scene_prompt:
                    scene_prompt.video_prompt = video_prompt.get("video_prompt", "")
                else:
                    scene_prompt = AdScenePrompt(
                        storyboard_id=storyboard.id,
                        scene_num=video_prompt.get("scene_num", 1),
                        video_prompt=video_prompt.get("video_prompt", "")
                    )
                    db.add(scene_prompt)
                
                prompts_data.append({
                    "storyboard_id": storyboard.id,
                    "scene_num": video_prompt.get("scene_num"),
                    "video_prompt": video_prompt.get("video_prompt")
                })
    
    db.commit()
    
    campaign.video_prompts_status = "completed"
    campaign.phase_status = "completed"
    campaign.current_phase = 9
    db.commit()
    
    return {
        "campaign_id": campaign_id,
        "phase": 8,
        "video_prompts": prompts_data
    }


# ==============================================================================
# PHASE 9: BATCH OUTPUT
# ==============================================================================

@router.get("/ads/campaigns/{campaign_id}/batch")
async def get_batch_output(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """
    Get complete batch output (Phase 9).
    
    Returns all generated content: context, avatars, scripts, storyboards, prompts.
    """
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    result = await generate_batch_output(campaign_id, db)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    campaign.current_phase = 9
    campaign.phase_status = "completed"
    campaign.overall_status = "completed"
    campaign.completed_at = datetime.utcnow()
    db.commit()
    
    return result


# ==============================================================================
# PHASE 10: ITERATION MODE
# ==============================================================================

@router.post("/ads/campaigns/{campaign_id}/iterate", response_model=IterationResponse)
async def iterate_campaign(
    campaign_id: int,
    request: IterationRequest,
    db: Session = Depends(get_db)
):
    """
    Apply iteration commands to modify outputs (Phase 10).
    
    Commands:
    - "make it funnier" - Adjust tone and humor
    - "change avatar" - Modify character appearance
    - "target gym audience" - Adjust targeting
    - "generate more hooks" - Create more hook variations
    - "make it shorter" - Reduce script length
    """
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign.current_phase = 10
    campaign.phase_status = "processing"
    db.commit()
    
    # Store iteration command
    conversation = AdConversation(
        campaign_id=campaign.id,
        role="user",
        phase=10,
        content=request.command,
        message_type="iteration"
    )
    db.add(conversation)
    db.commit()
    
    # Apply iteration
    result = await apply_iteration(
        campaign_id,
        request.command,
        request.target,
        db
    )
    
    if "error" in result:
        campaign.phase_status = "failed"
        campaign.error_message = result["error"]
        db.commit()
        raise HTTPException(status_code=500, detail=result["error"])
    
    campaign.phase_status = "completed"
    db.commit()
    
    return IterationResponse(
        campaign_id=campaign_id,
        iteration_count=campaign.iteration_count,
        changes_made=result.get("changes_made", ""),
        updated_data=result.get("modified_content", {})
    )


# ==============================================================================
# CONVENIENCE: RUN FULL PIPELINE
# ==============================================================================

@router.post("/ads/campaigns/{campaign_id}/generate-all")
async def generate_all(
    campaign_id: int,
    num_scripts: int = 5,
    num_avatars: int = 3,
    db: Session = Depends(get_db)
):
    """
    Run the full pipeline from current state.
    
    This is a convenience endpoint that runs all remaining phases.
    """
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign.overall_status = "processing"
    campaign.phase_status = "processing"
    db.commit()
    
    try:
        # Phase 4: Scripts (if not done)
        if campaign.scripts_status != "completed":
            await generate_campaign_scripts(
                campaign_id,
                ScriptsGenerateRequest(num_scripts=num_scripts),
                db
            )
            db.refresh(campaign)
        
        # Phase 5: Avatars (if not done)
        if campaign.avatars_status != "completed":
            await generate_campaign_avatars(campaign_id, num_avatars, db)
            db.refresh(campaign)
        
        # Phase 6: Storyboards (if not done)
        if campaign.storyboards_status != "completed":
            await generate_campaign_storyboards(campaign_id, db)
            db.refresh(campaign)
        
        # Phase 7: Image prompts (if not done)
        if campaign.image_prompts_status != "completed":
            await generate_campaign_image_prompts(campaign_id, db)
            db.refresh(campaign)
        
        # Phase 8: Video prompts (if not done)
        if campaign.video_prompts_status != "completed":
            await generate_campaign_video_prompts(campaign_id, db)
            db.refresh(campaign)

        # Phase 7.5: Generate scene images
        if db.query(AdScenePrompt).join(AdStoryboard).filter(
            AdStoryboard.campaign_id == campaign_id,
            AdScenePrompt.image_prompt.isnot(None),
            AdScenePrompt.image_status != "completed"
        ).count() > 0:
            await execute_image_generation(campaign_id, db)
            db.refresh(campaign)

        # Phase 8.5: Generate scene videos
        if db.query(AdScenePrompt).join(AdStoryboard).filter(
            AdStoryboard.campaign_id == campaign_id,
            AdScenePrompt.video_prompt.isnot(None),
            AdScenePrompt.image_status == "completed",
            AdScenePrompt.video_status != "completed"
        ).count() > 0:
            await execute_video_generation(campaign_id, db)
            db.refresh(campaign)
        
        # Phase 9: Batch output
        result = await get_batch_output(campaign_id, db)
        
        return result
        
    except Exception as e:
        campaign.overall_status = "failed"
        campaign.phase_status = "failed"
        campaign.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# REDO/RESTART FROM SPECIFIC PHASE
# ==============================================================================

@router.post("/ads/campaigns/{campaign_id}/redo/{phase}")
async def redo_phase(
    campaign_id: int,
    phase: int,
    db: Session = Depends(get_db)
):
    """
    Redo/restart the workflow from a specific phase.
    
    This clears all data from the specified phase onwards and re-runs the pipeline.
    
    Phase mapping:
    - 1: Re-generate clarification questions
    - 2: Re-build context (keeps questions, clears answers)
    - 3: Re-generate ad strategy
    - 4: Re-generate scripts
    - 5: Re-generate avatars
    - 6: Re-generate storyboards
    - 7: Re-generate image prompts
    - 8: Re-generate video prompts
    """
    from ..services.ads_pipeline import clear_debug_logs
    
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Clear data from the specified phase onwards
    if phase <= 1:
        # Reset to beginning
        campaign.clarification_questions = None
        campaign.user_answers = None
        campaign.context = None
        campaign.ad_angles = None
        campaign.current_phase = 1
        campaign.phase_status = "pending"
    
    if phase <= 2:
        campaign.user_answers = None
        campaign.context = None
        campaign.ad_angles = None
        campaign.current_phase = 2
        campaign.phase_status = "pending"
    
    if phase <= 3:
        campaign.ad_angles = None
        campaign.context = None
        campaign.current_phase = 3
        campaign.phase_status = "pending"
    
    if phase <= 4:
        # Delete scripts
        db.query(AdScript).filter(AdScript.campaign_id == campaign_id).delete()
        campaign.scripts_status = "pending"
        campaign.current_phase = 4
        campaign.phase_status = "pending"
    
    if phase <= 5:
        # Delete avatars
        db.query(AdAvatar).filter(AdAvatar.campaign_id == campaign_id).delete()
        campaign.avatars_status = "pending"
        campaign.current_phase = 5
        campaign.phase_status = "pending"
    
    if phase <= 6:
        # Delete storyboards and scene prompts
        storyboards = db.query(AdStoryboard).filter(AdStoryboard.campaign_id == campaign_id).all()
        for sb in storyboards:
            db.query(AdScenePrompt).filter(AdScenePrompt.storyboard_id == sb.id).delete()
        db.query(AdStoryboard).filter(AdStoryboard.campaign_id == campaign_id).delete()
        campaign.storyboards_status = "pending"
        campaign.current_phase = 6
        campaign.phase_status = "pending"
    
    if phase <= 7:
        # Delete image prompts
        storyboards = db.query(AdStoryboard).filter(AdStoryboard.campaign_id == campaign_id).all()
        for sb in storyboards:
            db.query(AdScenePrompt).filter(AdScenePrompt.storyboard_id == sb.id).delete()
        campaign.image_prompts_status = "pending"
        campaign.current_phase = 7
        campaign.phase_status = "pending"
    
    if phase <= 8:
        # Delete video prompts
        storyboards = db.query(AdStoryboard).filter(AdStoryboard.campaign_id == campaign_id).all()
        for sb in storyboards:
            prompts = db.query(AdScenePrompt).filter(AdScenePrompt.storyboard_id == sb.id).all()
            for p in prompts:
                p.video_prompt = None
                p.video_url = None
                p.video_status = "pending"
        campaign.video_prompts_status = "pending"
        campaign.current_phase = 8
        campaign.phase_status = "pending"
    
    # Reset overall status
    campaign.overall_status = "processing"
    campaign.error_message = None
    db.commit()
    
    # Clear debug logs
    clear_debug_logs(campaign_id)
    
    # Re-run from the specified phase
    try:
        # Phase 1: Generate questions if needed
        if phase <= 1:
            result = await generate_clarification_questions(
                campaign.user_prompt,
                campaign_id=campaign_id
            )
            if "error" not in result:
                campaign.clarification_questions = result.get("questions", [])
                campaign.phase_status = "completed"
                db.commit()
                return {"campaign_id": campaign_id, "phase": 1, "status": "needs_answers", "questions": campaign.clarification_questions}
        
        # Phase 2: Build context if needed (requires user_answers)
        if phase <= 2 and campaign.user_answers:
            result = await build_context(
                campaign.user_prompt,
                campaign.user_answers,
                campaign_id=campaign_id
            )
            if "error" not in result:
                campaign.context = result
                campaign.current_phase = 3
                db.commit()
        
        # Phase 3: Generate strategy
        if phase <= 3 and campaign.context:
            result = await generate_ad_strategy(campaign.context, campaign_id=campaign_id)
            if "error" not in result:
                campaign.ad_angles = result.get("angles", [])
                campaign.current_phase = 4
                campaign.phase_status = "completed"
                db.commit()
        
        # Phase 4: Generate scripts
        if phase <= 4 and campaign.context and campaign.ad_angles:
            await generate_campaign_scripts(
                campaign_id,
                ScriptsGenerateRequest(num_scripts=campaign.num_scripts or 5),
                db
            )
            db.refresh(campaign)
        
        # Phase 5: Generate avatars
        if phase <= 5 and campaign.context:
            await generate_campaign_avatars(campaign_id, campaign.num_avatars or 3, db)
            db.refresh(campaign)
        
        # Phase 6: Generate storyboards
        if phase <= 6:
            await generate_campaign_storyboards(campaign_id, db)
            db.refresh(campaign)
        
        # Phase 7: Generate image prompts
        if phase <= 7:
            await generate_campaign_image_prompts(campaign_id, db)
            db.refresh(campaign)
        
        # Phase 8: Generate video prompts
        if phase <= 8:
            await generate_campaign_video_prompts(campaign_id, db)
            db.refresh(campaign)
        
        # Phase 9: Complete
        if phase <= 9:
            result = await get_batch_output(campaign_id, db)
            return result
        
        db.refresh(campaign)
        return {"campaign_id": campaign_id, "current_phase": campaign.current_phase, "status": "success"}
        
    except Exception as e:
        campaign.overall_status = "failed"
        campaign.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# DEBUG LOGS
# ==============================================================================

@router.get("/ads/campaigns/{campaign_id}/debug-logs")
async def get_debug_logs_endpoint(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """
    Get debug logs for a campaign.
    
    Returns all logged events for debugging the workflow.
    """
    from ..services.ads_pipeline import get_debug_logs
    
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    logs = get_debug_logs(campaign_id)
    
    return {
        "campaign_id": campaign_id,
        "current_phase": campaign.current_phase,
        "phase_status": campaign.phase_status,
        "overall_status": campaign.overall_status,
        "logs": logs
    }


# ==============================================================================
# UPDATE CAMPAIGN INPUT (for re-editing)
# ==============================================================================

@router.put("/ads/campaigns/{campaign_id}/input")
async def update_campaign_input(
    campaign_id: int,
    user_prompt: str = None,
    brand_name: str = None,
    answers: List[dict] = None,
    db: Session = Depends(get_db)
):
    """
    Update campaign input data.
    
    This allows users to modify their original input and restart from Phase 1 or 2.
    """
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    updated = False
    
    if user_prompt is not None:
        campaign.user_prompt = user_prompt
        updated = True
    
    if brand_name is not None and campaign.context:
        campaign.context["brand"] = brand_name
        updated = True
    
    if answers is not None:
        campaign.user_answers = answers
        updated = True
    
    if updated:
        db.commit()
    
    return {
        "campaign_id": campaign_id,
        "updated": updated,
        "user_prompt": campaign.user_prompt,
        "context": campaign.context
    }


# ==============================================================================
# LEGACY ENDPOINTS (for backward compatibility)
# ==============================================================================

@router.post("/ads/generate", response_model=AdCampaignResponse)
async def create_ad_campaign_legacy(
    request: AdCampaignCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Legacy endpoint - creates campaign and starts Phase 1."""
    return await create_campaign(request, background_tasks, db)


@router.get("/ads", response_model=AdCampaignListResponse)
async def list_ad_campaigns_legacy(
    page: int = 1,
    per_page: int = 10,
    db: Session = Depends(get_db)
):
    """Legacy endpoint - lists campaigns."""
    return await list_campaigns(page, per_page, db)


@router.get("/ads/{campaign_id}", response_model=AdCampaignResponse)
async def get_ad_campaign_legacy(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Legacy endpoint - gets campaign."""
    return await get_campaign(campaign_id, db)


# ==============================================================================


# PHASE 7.5: EXECUTE IMAGE GENERATION


# ==============================================================================





@router.post("/ads/campaigns/{campaign_id}/generate-images")


async def execute_image_generation(


    campaign_id: int,


    db: Session = Depends(get_db)


):


    """


    Execute actual image generation for all scene prompts (Phase 7.5).





    Uses Nano Banana 2 to generate or recreate the static ad images for each scene.


    """


    from ..models import Generation





    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()


    if not campaign:


        raise HTTPException(status_code=404, detail="Campaign not found")





    scene_prompts = db.query(AdScenePrompt).join(AdStoryboard).filter(


        AdStoryboard.campaign_id == campaign_id


    ).order_by(AdScenePrompt.scene_num.asc()).all()





    if not scene_prompts:


        raise HTTPException(status_code=400, detail="No scene prompts found. Complete Phase 7 first.")





    campaign.image_prompts_status = "processing"


    campaign.phase_status = "processing"


    db.commit()





    nanobanana_client = get_nanobanana_client()


    results = []


    has_failure = False





    for scene_prompt in scene_prompts:


        if not scene_prompt.image_prompt or scene_prompt.image_status == "completed":


            continue





        _add_debug_log(campaign_id, "generate-images", "start", {


            "scene_prompt_id": scene_prompt.id,


            "scene_num": scene_prompt.scene_num,


            "provider": "nanobanana",


            "model": "nano-banana-2",


            "num_requested": 3


        })





        try:


            scene_prompt.image_status = "processing"


            db.commit()





            result = await nanobanana_client.generate_multiple_and_wait(


                prompt=scene_prompt.image_prompt,


                model=NanoBananaModel.NANO_BANANA_2,


                aspect_ratio=AspectRatio.LANDSCAPE_16_9,


                reference_images=[scene_prompt.image_url] if scene_prompt.image_url else None,


                num_images=3,


                max_wait_seconds=120,


                poll_interval=5


            )





            if not result.get("success") or not result.get("image_urls"):


                raise RuntimeError(result.get("error") or "Nano Banana image generation failed")





            image_url = result["image_urls"][0]


            generation = Generation(


                uuid=result.get("primary_task_id"),


                prompt=scene_prompt.image_prompt,


                model="nano-banana-2",


                generation_type="text2img",


                width=1280,


                height=720,


                status="completed",


                progress=100,


                remote_url=image_url,


                completed_at=datetime.utcnow()


            )


            db.add(generation)


            db.commit()


            db.refresh(generation)





            scene_prompt.image_generation_id = generation.id


            scene_prompt.image_url = image_url


            scene_prompt.image_status = "completed"


            db.commit()





            _add_debug_log(campaign_id, "generate-images", "complete", {


                "scene_prompt_id": scene_prompt.id,


                "scene_num": scene_prompt.scene_num,


                "generation_id": generation.id,


                "image_url": image_url,


                "candidate_image_urls": result.get("image_urls", []),


                "num_requested": result.get("num_requested", 3),


                "num_succeeded": result.get("num_succeeded", 0),


                "num_failed": result.get("num_failed", 0),


                "errors": result.get("errors", [])


            })





            results.append({


                "scene_prompt_id": scene_prompt.id,


                "scene_num": scene_prompt.scene_num,


                "image_generation_id": generation.id,


                "image_url": image_url,


                "image_urls": result.get("image_urls", []),


                "num_requested": result.get("num_requested", 3),


                "num_succeeded": result.get("num_succeeded", 0),


                "num_failed": result.get("num_failed", 0),


                "status": "completed"


            })


        except Exception as e:


            has_failure = True


            scene_prompt.image_status = "failed"


            db.commit()


            _add_debug_log(campaign_id, "generate-images", "error", {


                "scene_prompt_id": scene_prompt.id,


                "scene_num": scene_prompt.scene_num,


                "error": str(e),


                "num_requested": 3


            })


            results.append({


                "scene_prompt_id": scene_prompt.id,


                "scene_num": scene_prompt.scene_num,


                "status": "failed",


                "error": str(e),


                "num_requested": 3


            })





    campaign.image_prompts_status = "failed" if has_failure else "completed"


    campaign.phase_status = "failed" if has_failure else "completed"


    if not has_failure:


        campaign.current_phase = max(campaign.current_phase or 7, 8)


    db.commit()





    return {


        "campaign_id": campaign_id,


        "phase": "7.5",


        "results": results


    }








# ==============================================================================


# PHASE 8.5: EXECUTE VIDEO GENERATION


# ==============================================================================





@router.post("/ads/campaigns/{campaign_id}/generate-videos")





async def execute_video_generation(





    campaign_id: int,





    db: Session = Depends(get_db)





):





    """





    Execute actual video generation for all scene prompts (Phase 8.5).











    Uses the LTX 2.3 image-to-video model to turn completed scene images into clips.





    Stores request_ids for polling - frontend should poll /ads/campaigns/{id}/detail for updates.





    """





    from ..models import Generation











    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()





    if not campaign:





        raise HTTPException(status_code=404, detail="Campaign not found")











    scene_prompts = db.query(AdScenePrompt).join(AdStoryboard).filter(





        AdStoryboard.campaign_id == campaign_id,





        AdScenePrompt.image_status == "completed",





        AdScenePrompt.video_status != "completed"





    ).order_by(AdScenePrompt.scene_num.asc()).all()











    if not scene_prompts:





        raise HTTPException(status_code=400, detail="No completed images found. Run Phase 7.5 first.")











    campaign.video_prompts_status = "processing"





    campaign.phase_status = "processing"





    campaign.overall_status = "processing"





    db.commit()











    client = get_pipeline_client()





    results = []











    for scene_prompt in scene_prompts:





        if not scene_prompt.video_prompt or not scene_prompt.image_url:





            continue











        _add_debug_log(campaign_id, "generate-videos", "start", {





            "scene_prompt_id": scene_prompt.id,





            "scene_num": scene_prompt.scene_num,





            "provider": "deapi",





            "model": "Ltx2_3_22B_Dist_INT8"





        })











        try:





            scene_prompt.video_status = "processing"





            db.commit()











            # Submit and get request_id





            result = await client.submit_img2video(





                image_url=scene_prompt.image_url,





                prompt=scene_prompt.video_prompt,





                model="Ltx2_3_22B_Dist_INT8",





                width=768,





                height=768,





                frames=120





            )











            request_id = result.get("request_id")





            if not request_id:





                raise RuntimeError("LTX 2.3 video generation did not return a request_id")











            # Create generation record with request_id for polling





            generation = Generation(





                uuid=request_id,





                prompt=scene_prompt.video_prompt,





                model="Ltx2_3_22B_Dist_INT8",





                generation_type="img2video",





                width=768,





                height=768,





                frames=120,





                fps=24,





                status="processing",





                progress=0





            )





            db.add(generation)





            db.commit()





            db.refresh(generation)











            scene_prompt.video_generation_id = generation.id





            db.commit()











            _add_debug_log(campaign_id, "generate-videos", "submitted", {





                "scene_prompt_id": scene_prompt.id,





                "scene_num": scene_prompt.scene_num,





                "generation_id": generation.id,





                "request_id": request_id





            })











            results.append({





                "scene_prompt_id": scene_prompt.id,





                "scene_num": scene_prompt.scene_num,





                "video_generation_id": generation.id,





                "request_id": request_id,





                "status": "processing"





            })





        except Exception as e:





            scene_prompt.video_status = "failed"





            db.commit()





            _add_debug_log(campaign_id, "generate-videos", "error", {





                "scene_prompt_id": scene_prompt.id,





                "scene_num": scene_prompt.scene_num,





                "error": str(e)





            })





            results.append({





                "scene_prompt_id": scene_prompt.id,





                "scene_num": scene_prompt.scene_num,





                "status": "failed",





                "error": str(e)





            })











    return {





        "campaign_id": campaign_id,





        "phase": "8.5",





        "message": "Video generation started. Poll /api/ads/campaigns/{campaign_id}/detail for status updates.",





        "results": results





    }


# ==============================================================================
# STATUS POLLING ENDPOINT
# ==============================================================================

@router.get("/ads/campaigns/{campaign_id}/check-status")
async def check_campaign_status(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """
    Check and update status of all processing scene generations.
    
    This endpoint polls deAPI for all scene prompts that are in 'processing' state
    and updates their status, URLs, and progress.
    
    Frontend should poll this endpoint every 5-10 seconds during generation.
    """
    from ..models import Generation
    
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Get all scene prompts with processing image or video
    scene_prompts = db.query(AdScenePrompt).join(AdStoryboard).filter(
        AdStoryboard.campaign_id == campaign_id
    ).all()
    
    client = get_pipeline_client()
    deapi_client = get_deapi_client()
    updates = []
    
    for scene_prompt in scene_prompts:
        # Check image generation status
        if scene_prompt.image_status == "processing" and scene_prompt.image_generation_id:
            generation = db.query(Generation).filter(
                Generation.id == scene_prompt.image_generation_id
            ).first()
            
            if generation and generation.uuid and generation.status == "processing":
                try:
                    status = await deapi_client.get_request_status(generation.uuid)
                    data = status.get("data", status)
                    
                    if data.get("status") == "done":
                        image_url = data.get("result_url") or data.get("download_url")
                        if image_url:
                            generation.remote_url = image_url
                            generation.status = "completed"
                            generation.progress = 100
                            generation.completed_at = datetime.utcnow()
                            scene_prompt.image_url = image_url
                            scene_prompt.image_status = "completed"
                            db.commit()
                            updates.append({
                                "scene_num": scene_prompt.scene_num,
                                "type": "image",
                                "status": "completed",
                                "url": image_url
                            })
                    elif data.get("status") == "error":
                        generation.status = "failed"
                        scene_prompt.image_status = "failed"
                        db.commit()
                        updates.append({
                            "scene_num": scene_prompt.scene_num,
                            "type": "image",
                            "status": "failed",
                            "error": data.get("error", "Image generation failed")
                        })
                    elif "progress" in data:
                        generation.progress = data.get("progress", 0)
                        db.commit()
                except Exception as e:
                    _add_debug_log(campaign_id, "check-status", "error", {
                        "scene_num": scene_prompt.scene_num,
                        "type": "image",
                        "error": str(e)
                    })
        
        # Check video generation status
        if scene_prompt.video_status == "processing" and scene_prompt.video_generation_id:
            generation = db.query(Generation).filter(
                Generation.id == scene_prompt.video_generation_id
            ).first()
            
            if generation and generation.uuid and generation.status == "processing":
                try:
                    status = await deapi_client.get_request_status(generation.uuid)
                    data = status.get("data", status)
                    
                    if data.get("status") == "done":
                        video_url = data.get("result_url") or data.get("download_url")
                        if video_url:
                            generation.remote_url = video_url
                            generation.status = "completed"
                            generation.progress = 100
                            generation.completed_at = datetime.utcnow()
                            scene_prompt.video_url = video_url
                            scene_prompt.video_status = "completed"
                            db.commit()
                            updates.append({
                                "scene_num": scene_prompt.scene_num,
                                "type": "video",
                                "status": "completed",
                                "url": video_url
                            })
                    elif data.get("status") == "error":
                        generation.status = "failed"
                        scene_prompt.video_status = "failed"
                        db.commit()
                        updates.append({
                            "scene_num": scene_prompt.scene_num,
                            "type": "video",
                            "status": "failed",
                            "error": data.get("error", "Video generation failed")
                        })
                    elif "progress" in data:
                        generation.progress = data.get("progress", 0)
                        db.commit()
                except Exception as e:
                    _add_debug_log(campaign_id, "check-status", "error", {
                        "scene_num": scene_prompt.scene_num,
                        "type": "video",
                        "error": str(e)
                    })
    
    # Update campaign overall status if all scenes are done
    all_scene_prompts = db.query(AdScenePrompt).join(AdStoryboard).filter(
        AdStoryboard.campaign_id == campaign_id
    ).all()
    
    all_videos_done = all(
        sp.video_status in ("completed", "failed") or not sp.video_prompt
        for sp in all_scene_prompts
    )
    
    if all_videos_done and campaign.overall_status == "processing":
        campaign.overall_status = "completed"
        campaign.completed_at = datetime.utcnow()
        db.commit()
    
    db.refresh(campaign)
    
    return {
        "campaign_id": campaign_id,
        "overall_status": campaign.overall_status,
        "updates": updates
    }


@router.post("/ads/campaigns/{campaign_id}/scenes/{scene_prompt_id}/regenerate-image")
async def regenerate_scene_image(
    campaign_id: int,
    scene_prompt_id: int,
    prompt: str,
    db: Session = Depends(get_db)
):
    """Regenerate a single campaign scene image using Nano Banana 2."""
    from ..models import Generation

    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    scene_prompt = db.query(AdScenePrompt).join(AdStoryboard).filter(
        AdScenePrompt.id == scene_prompt_id,
        AdStoryboard.id == AdScenePrompt.storyboard_id,
        AdStoryboard.campaign_id == campaign_id
    ).first()
    if not scene_prompt:
        raise HTTPException(status_code=404, detail="Scene prompt not found")

    previous_image_url = scene_prompt.image_url
    scene_prompt.image_prompt = prompt
    scene_prompt.image_status = "processing"
    scene_prompt.video_status = "pending"
    scene_prompt.video_generation_id = None
    scene_prompt.video_url = None
    campaign.image_prompts_status = "processing"
    campaign.video_prompts_status = "pending"
    campaign.phase_status = "processing"
    campaign.overall_status = "processing"
    db.commit()

    _add_debug_log(campaign_id, "scene-regenerate-image", "start", {
        "scene_prompt_id": scene_prompt.id,
        "scene_num": scene_prompt.scene_num,
        "model": "nano-banana-2",
        "num_requested": 3
    })

    try:
        result = await get_nanobanana_client().generate_multiple_and_wait(
            prompt=prompt,
            model=NanoBananaModel.NANO_BANANA_2,
            aspect_ratio=AspectRatio.LANDSCAPE_16_9,
            reference_images=[previous_image_url] if previous_image_url else None,
            num_images=3,
            max_wait_seconds=120,
            poll_interval=5
        )

        if not result.get("success") or not result.get("image_urls"):
            raise RuntimeError(result.get("error") or "Nano Banana image regeneration failed")

        image_url = result["image_urls"][0]
        generation = Generation(
            uuid=result.get("primary_task_id"),
            prompt=prompt,
            model="nano-banana-2",
            generation_type="text2img",
            width=1280,
            height=720,
            status="completed",
            progress=100,
            remote_url=image_url,
            completed_at=datetime.utcnow()
        )
        db.add(generation)
        db.commit()
        db.refresh(generation)

        scene_prompt.image_generation_id = generation.id
        scene_prompt.image_url = image_url
        scene_prompt.image_status = "completed"
        campaign.image_prompts_status = "completed"
        campaign.phase_status = "completed"
        db.commit()

        _add_debug_log(campaign_id, "scene-regenerate-image", "complete", {
            "scene_prompt_id": scene_prompt.id,
            "scene_num": scene_prompt.scene_num,
            "generation_id": generation.id,
            "image_url": image_url,
            "candidate_image_urls": result.get("image_urls", []),
            "num_requested": result.get("num_requested", 3),
            "num_succeeded": result.get("num_succeeded", 0),
            "num_failed": result.get("num_failed", 0),
            "errors": result.get("errors", [])
        })

        return {
            "campaign_id": campaign_id,
            "scene_prompt_id": scene_prompt.id,
            "image_generation_id": generation.id,
            "image_url": image_url,
            "image_urls": result.get("image_urls", []),
            "num_requested": result.get("num_requested", 3),
            "num_succeeded": result.get("num_succeeded", 0),
            "num_failed": result.get("num_failed", 0),
            "status": "completed"
        }
    except Exception as e:
        scene_prompt.image_status = "failed"
        campaign.image_prompts_status = "failed"
        campaign.phase_status = "failed"
        db.commit()
        _add_debug_log(campaign_id, "scene-regenerate-image", "error", {
            "scene_prompt_id": scene_prompt.id,
            "scene_num": scene_prompt.scene_num,
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ads/campaigns/{campaign_id}/scenes/{scene_prompt_id}/regenerate-video")
async def regenerate_scene_video(
    campaign_id: int,
    scene_prompt_id: int,
    prompt: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Regenerate a single campaign scene video clip using LTX 2.3.
    
    Returns immediately with request_id - poll /ads/campaigns/{campaign_id}/check-status for updates.
    """
    from ..models import Generation

    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    scene_prompt = db.query(AdScenePrompt).join(AdStoryboard).filter(
        AdScenePrompt.id == scene_prompt_id,
        AdStoryboard.id == AdScenePrompt.storyboard_id,
        AdStoryboard.campaign_id == campaign_id
    ).first()
    if not scene_prompt:
        raise HTTPException(status_code=404, detail="Scene prompt not found")
    if not scene_prompt.image_url:
        raise HTTPException(status_code=400, detail="Scene image is required before regenerating video")

    if prompt:
        scene_prompt.video_prompt = prompt

    if not scene_prompt.video_prompt:
        raise HTTPException(status_code=400, detail="Video prompt is required")

    scene_prompt.video_status = "processing"
    scene_prompt.video_url = None  # Clear previous URL
    campaign.video_prompts_status = "processing"
    campaign.phase_status = "processing"
    campaign.overall_status = "processing"
    db.commit()

    _add_debug_log(campaign_id, "scene-regenerate-video", "start", {
        "scene_prompt_id": scene_prompt.id,
        "scene_num": scene_prompt.scene_num,
        "model": "Ltx2_3_22B_Dist_INT8"
    })

    try:
        result = await get_pipeline_client().submit_img2video(
            image_url=scene_prompt.image_url,
            prompt=scene_prompt.video_prompt,
            model="Ltx2_3_22B_Dist_INT8",
            width=768,
            height=768,
            frames=120
        )

        request_id = result.get("request_id")
        if not request_id:
            raise RuntimeError("LTX 2.3 video regeneration did not return a request_id")

        # Create generation record with processing status
        generation = Generation(
            uuid=request_id,
            prompt=scene_prompt.video_prompt,
            model="Ltx2_3_22B_Dist_INT8",
            generation_type="img2video",
            width=768,
            height=768,
            frames=120,
            fps=24,
            status="processing",
            progress=0
        )
        db.add(generation)
        db.commit()
        db.refresh(generation)

        scene_prompt.video_generation_id = generation.id
        db.commit()

        _add_debug_log(campaign_id, "scene-regenerate-video", "submitted", {
            "scene_prompt_id": scene_prompt.id,
            "scene_num": scene_prompt.scene_num,
            "generation_id": generation.id,
            "request_id": request_id
        })

        return {
            "campaign_id": campaign_id,
            "scene_prompt_id": scene_prompt.id,
            "video_generation_id": generation.id,
            "request_id": request_id,
            "status": "processing",
            "message": "Video generation started. Poll /api/ads/campaigns/{campaign_id}/check-status for updates."
        }
    except Exception as e:
        scene_prompt.video_status = "failed"
        campaign.video_prompts_status = "failed"
        campaign.phase_status = "failed"
        db.commit()
        _add_debug_log(campaign_id, "scene-regenerate-video", "error", {
            "scene_prompt_id": scene_prompt.id,
            "scene_num": scene_prompt.scene_num,
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail=str(e))

