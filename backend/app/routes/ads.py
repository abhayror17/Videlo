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
    get_pipeline_client
)

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
    """Get full campaign details with avatars and scripts."""
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    avatars = db.query(AdAvatar).filter(AdAvatar.campaign_id == campaign_id).all()
    scripts = db.query(AdScript).filter(AdScript.campaign_id == campaign_id).all()
    
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
    
    Uses deAPI to generate images from the prompts created in Phase 7.
    """
    from ..models import Generation
    
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    scene_prompts = db.query(AdScenePrompt).join(AdStoryboard).filter(
        AdStoryboard.campaign_id == campaign_id
    ).all()
    
    if not scene_prompts:
        raise HTTPException(status_code=400, detail="No scene prompts found. Complete Phase 7 first.")
    
    campaign.image_prompts_status = "processing"
    db.commit()
    
    client = get_pipeline_client()
    results = []
    
    for scene_prompt in scene_prompts:
        if scene_prompt.image_prompt and scene_prompt.image_status == "pending":
            try:
                result = await client.submit_text2img(scene_prompt.image_prompt)
                
                generation = Generation(
                    prompt=scene_prompt.image_prompt,
                    generation_type="text2img",
                    model="ZImageTurbo_INT8",
                    status="completed",
                    remote_url=result.get("url") or result.get("image_url")
                )
                db.add(generation)
                db.commit()
                db.refresh(generation)
                
                scene_prompt.image_generation_id = generation.id
                scene_prompt.image_url = generation.remote_url
                scene_prompt.image_status = "completed"
                db.commit()
                
                results.append({
                    "scene_num": scene_prompt.scene_num,
                    "image_url": scene_prompt.image_url,
                    "status": "completed"
                })
            except Exception as e:
                scene_prompt.image_status = "failed"
                db.commit()
                results.append({
                    "scene_num": scene_prompt.scene_num,
                    "status": "failed",
                    "error": str(e)
                })
    
    campaign.image_prompts_status = "completed"
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
    
    Uses deAPI to generate videos from the images and prompts.
    """
    from ..models import Generation
    
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    scene_prompts = db.query(AdScenePrompt).join(AdStoryboard).filter(
        AdStoryboard.campaign_id == campaign_id,
        AdScenePrompt.image_status == "completed"
    ).all()
    
    if not scene_prompts:
        raise HTTPException(status_code=400, detail="No completed images found. Run Phase 7.5 first.")
    
    campaign.video_prompts_status = "processing"
    db.commit()
    
    client = get_pipeline_client()
    results = []
    
    for scene_prompt in scene_prompts:
        if scene_prompt.video_prompt and scene_prompt.image_url and scene_prompt.video_status == "pending":
            try:
                result = await client.submit_img2video(
                    image_url=scene_prompt.image_url,
                    prompt=scene_prompt.video_prompt
                )
                
                generation = Generation(
                    prompt=scene_prompt.video_prompt,
                    generation_type="img2video",
                    model="Ltx2_19B_Dist_FP8",
                    status="completed",
                    remote_url=result.get("url") or result.get("video_url")
                )
                db.add(generation)
                db.commit()
                db.refresh(generation)
                
                scene_prompt.video_generation_id = generation.id
                scene_prompt.video_url = generation.remote_url
                scene_prompt.video_status = "completed"
                db.commit()
                
                results.append({
                    "scene_num": scene_prompt.scene_num,
                    "video_url": scene_prompt.video_url,
                    "status": "completed"
                })
            except Exception as e:
                scene_prompt.video_status = "failed"
                db.commit()
                results.append({
                    "scene_num": scene_prompt.scene_num,
                    "status": "failed",
                    "error": str(e)
                })
    
    campaign.video_prompts_status = "completed"
    campaign.overall_status = "completed"
    db.commit()
    
    return {
        "campaign_id": campaign_id,
        "phase": "8.5",
        "results": results
    }