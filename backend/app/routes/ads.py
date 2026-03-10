"""
AI Ads Generator Routes

API endpoints for the AI Ads Generator pipeline:
- Create ad campaigns
- Track pipeline progress
- Redo failed/rejected steps
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
import asyncio
import json
from typing import Optional

from ..database import get_db
from ..models import AdCampaign, Generation
from ..schemas import (
    AdCampaignCreate,
    AdCampaignResponse,
    AdCampaignListResponse,
    RedoRequest
)
from ..services.ads_pipeline import (
    enhance_prompt_for_ads,
    generate_ad_script,
    generate_image_prompt_from_script,
    qa_check_content,
    get_pipeline_client
)
from ..services.deapi import get_deapi_client

router = APIRouter(prefix="/api", tags=["ads"])


async def run_ads_pipeline(campaign_id: int, db_url: str):
    """
    Background task that runs the full ads generation pipeline.
    
    Steps:
    1. Enhance prompt
    2. Generate script
    3. Generate image (text2img)
    4. Generate video (img2video)
    5. QA check
    """
    from ..database import SessionLocal
    
    db = SessionLocal()
    pipeline_client = get_pipeline_client()
    
    try:
        campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
        if not campaign:
            return
        
        # Step 1: Enhance Prompt
        campaign.current_step = "enhancing"
        campaign.enhancement_status = "processing"
        campaign.overall_status = "processing"
        db.commit()
        
        try:
            enhancement_result = await enhance_prompt_for_ads(
                campaign.user_prompt,
                campaign.brand_name,
                campaign.brand_description
            )
            campaign.enhanced_prompt = enhancement_result.get("enhanced_prompt", campaign.user_prompt)
            campaign.enhancement_status = "completed"
            campaign.current_step = "script"
            db.commit()
        except Exception as e:
            campaign.enhancement_status = "failed"
            campaign.error_message = f"Prompt enhancement failed: {str(e)}"
            db.commit()
            return
        
        # Step 2: Generate Script
        campaign.script_status = "processing"
        db.commit()
        
        try:
            script_result = await generate_ad_script(
                campaign.enhanced_prompt,
                campaign.brand_name,
                enhancement_result.get("visual_style"),
                duration=15
            )
            campaign.script = json.dumps(script_result, indent=2)
            campaign.script_status = "completed"
            campaign.current_step = "image"
            db.commit()
        except Exception as e:
            campaign.script_status = "failed"
            campaign.error_message = f"Script generation failed: {str(e)}"
            db.commit()
            return
        
        # Step 3: Generate Image (text2img)
        campaign.image_status = "processing"
        db.commit()
        
        try:
            # Create image prompt from script
            script_data = json.loads(campaign.script) if campaign.script else {}
            image_prompt = await generate_image_prompt_from_script(
                script_data,
                enhancement_result,
                campaign.brand_name
            )
            
            # Submit to deAPI
            image_result = await pipeline_client.submit_text2img(
                prompt=image_prompt,
                width=1024,
                height=768
            )
            
            request_id = image_result.get("request_id")
            if not request_id:
                campaign.image_status = "failed"
                campaign.error_message = f"Image generation failed: No request_id returned. Response: {image_result}"
                db.commit()
                return
            
            campaign.image_request_id = request_id
            db.commit()
            
            # Poll for image result
            for _ in range(120):  # Poll for up to 10 minutes
                await asyncio.sleep(3)
                
                status_result = await pipeline_client.get_request_status(request_id)
                status = status_result.get("status")
                
                if status == "done":
                    campaign.image_url = status_result.get("result_url")
                    campaign.image_status = "completed"
                    campaign.current_step = "video"
                    db.commit()
                    break
                elif status in ("failed", "error"):
                    campaign.image_status = "failed"
                    campaign.error_message = f"Image generation failed: {status_result.get('error', 'Unknown error')}"
                    db.commit()
                    return
            
            if campaign.image_status != "completed":
                campaign.image_status = "failed"
                campaign.error_message = "Image generation timeout"
                db.commit()
                return
                
        except Exception as e:
            campaign.image_status = "failed"
            campaign.error_message = f"Image generation failed: {str(e)}"
            db.commit()
            return
        
        # Step 4: Generate Video (img2video)
        if not campaign.image_url:
            campaign.video_status = "failed"
            campaign.error_message = "Cannot generate video: No image URL available"
            db.commit()
            return
        
        campaign.video_status = "processing"
        db.commit()
        
        try:
            # Use script hook/tagline for video prompt
            video_prompt = script_data.get("hook", campaign.enhanced_prompt)
            
            # Submit to deAPI
            video_result = await pipeline_client.submit_img2video(
                image_url=campaign.image_url,
                prompt=video_prompt,
                width=768,
                height=768,
                frames=48
            )
            
            request_id = video_result.get("request_id")
            if not request_id:
                campaign.video_status = "failed"
                campaign.error_message = f"Video generation failed: No request_id returned. Response: {video_result}"
                db.commit()
                return
            
            campaign.video_request_id = request_id
            db.commit()
            
            # Poll for video result
            for _ in range(180):  # Poll for up to 15 minutes (video takes longer)
                await asyncio.sleep(5)
                
                status_result = await pipeline_client.get_request_status(request_id)
                status = status_result.get("status")
                
                if status == "done":
                    campaign.video_url = status_result.get("result_url")
                    campaign.video_status = "completed"
                    campaign.current_step = "qa"
                    db.commit()
                    break
                elif status in ("failed", "error"):
                    campaign.video_status = "failed"
                    campaign.error_message = f"Video generation failed: {status_result.get('error', 'Unknown error')}"
                    db.commit()
                    return
            
            if campaign.video_status != "completed":
                campaign.video_status = "failed"
                campaign.error_message = "Video generation timeout"
                db.commit()
                return
                
        except Exception as e:
            campaign.video_status = "failed"
            campaign.error_message = f"Video generation failed: {str(e)}"
            db.commit()
            return
        
        # Step 5: QA Check
        campaign.qa_status = "processing"
        db.commit()
        
        try:
            qa_result = await qa_check_content(
                script=campaign.script,
                image_url=campaign.image_url,
                video_url=campaign.video_url,
                brand_name=campaign.brand_name,
                brand_description=campaign.brand_description,
                enhanced_prompt=campaign.enhanced_prompt
            )
            
            campaign.qa_feedback = qa_result.get("feedback", "")
            campaign.qa_details = json.dumps(qa_result.get("details", {}))
            campaign.qa_iterations += 1
            
            if qa_result.get("approved", False):
                campaign.qa_status = "approved"
                campaign.overall_status = "completed"
                campaign.current_step = "completed"
            else:
                campaign.qa_status = "rejected"
                campaign.overall_status = "needs_revision"
                campaign.current_step = "revision_needed"
            
            db.commit()
            
        except Exception as e:
            campaign.qa_status = "failed"
            campaign.error_message = f"QA check failed: {str(e)}"
            db.commit()
            
    except Exception as e:
        # Catch-all for unexpected errors
        campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
        if campaign:
            campaign.overall_status = "failed"
            campaign.error_message = f"Pipeline error: {str(e)}"
            db.commit()
    
    finally:
        db.close()


async def redo_step(campaign_id: int, step: str, db_url: str):
    """Background task to redo a specific pipeline step."""
    from ..database import SessionLocal
    
    db = SessionLocal()
    pipeline_client = get_pipeline_client()
    
    try:
        campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
        if not campaign:
            return
        
        if step == "script":
            campaign.script_status = "processing"
            campaign.current_step = "script"
            db.commit()
            
            try:
                # Re-parse enhancement result
                enhancement_result = {"visual_style": "modern"}
                
                script_result = await generate_ad_script(
                    campaign.enhanced_prompt or campaign.user_prompt,
                    campaign.brand_name,
                    enhancement_result.get("visual_style"),
                    duration=15
                )
                campaign.script = json.dumps(script_result, indent=2)
                campaign.script_status = "completed"
                campaign.current_step = "qa"
                db.commit()
            except Exception as e:
                campaign.script_status = "failed"
                campaign.error_message = f"Script redo failed: {str(e)}"
                db.commit()
                
        elif step == "image":
            campaign.image_status = "processing"
            campaign.current_step = "image"
            db.commit()
            
            try:
                script_data = json.loads(campaign.script) if campaign.script else {}
                enhancement_result = {"visual_style": "modern", "mood": "professional"}
                
                image_prompt = await generate_image_prompt_from_script(
                    script_data,
                    enhancement_result,
                    campaign.brand_name
                )
                
                image_result = await pipeline_client.submit_text2img(
                    prompt=image_prompt,
                    width=1024,
                    height=768
                )
                
                request_id = image_result.get("request_id")
                if not request_id:
                    campaign.image_status = "failed"
                    campaign.error_message = f"Image redo failed: No request_id returned. Response: {image_result}"
                    db.commit()
                    return
                
                campaign.image_request_id = request_id
                db.commit()
                
                # Poll for result
                for _ in range(120):
                    await asyncio.sleep(3)
                    status_result = await pipeline_client.get_request_status(request_id)
                    status = status_result.get("status")
                    if status == "done":
                        campaign.image_url = status_result.get("result_url")
                        campaign.image_status = "completed"
                        campaign.current_step = "video"
                        db.commit()
                        break
                    elif status in ("failed", "error"):
                        campaign.image_status = "failed"
                        campaign.error_message = f"Image redo failed: {status_result.get('error', 'Unknown error')}"
                        db.commit()
                        return
                        
            except Exception as e:
                campaign.image_status = "failed"
                campaign.error_message = f"Image redo failed: {str(e)}"
                db.commit()
                
        elif step == "video":
            # Check if image exists before generating video
            if not campaign.image_url:
                campaign.video_status = "failed"
                campaign.error_message = "Cannot generate video: No image available. Please redo the image step first."
                db.commit()
                return
            
            campaign.video_status = "processing"
            campaign.current_step = "video"
            db.commit()
            
            try:
                script_data = json.loads(campaign.script) if campaign.script else {}
                video_prompt = script_data.get("hook", campaign.enhanced_prompt)
                
                video_result = await pipeline_client.submit_img2video(
                    image_url=campaign.image_url,
                    prompt=video_prompt,
                    width=768,
                    height=768,
                    frames=48
                )
                
                request_id = video_result.get("request_id")
                if not request_id:
                    campaign.video_status = "failed"
                    campaign.error_message = f"Video redo failed: No request_id returned. Response: {video_result}"
                    db.commit()
                    return
                
                campaign.video_request_id = request_id
                db.commit()
                
                # Poll for result
                for _ in range(180):
                    await asyncio.sleep(5)
                    status_result = await pipeline_client.get_request_status(request_id)
                    status = status_result.get("status")
                    if status == "done":
                        campaign.video_url = status_result.get("result_url")
                        campaign.video_status = "completed"
                        campaign.current_step = "qa"
                        db.commit()
                        break
                    elif status in ("failed", "error"):
                        campaign.video_status = "failed"
                        campaign.error_message = f"Video redo failed: {status_result.get('error', 'Unknown error')}"
                        db.commit()
                        return
                        
            except Exception as e:
                campaign.video_status = "failed"
                campaign.error_message = f"Video redo failed: {str(e)}"
                db.commit()
        
        # After redo, run QA again
        if campaign.image_status == "completed" and campaign.video_status == "completed":
            campaign.qa_status = "processing"
            db.commit()
            
            qa_result = await qa_check_content(
                script=campaign.script,
                image_url=campaign.image_url,
                video_url=campaign.video_url,
                brand_name=campaign.brand_name,
                brand_description=campaign.brand_description,
                enhanced_prompt=campaign.enhanced_prompt
            )
            
            campaign.qa_feedback = qa_result.get("feedback", "")
            campaign.qa_details = json.dumps(qa_result.get("details", {}))
            campaign.qa_iterations += 1
            
            if qa_result.get("approved", False):
                campaign.qa_status = "approved"
                campaign.overall_status = "completed"
                campaign.current_step = "completed"
            else:
                campaign.qa_status = "rejected"
                campaign.overall_status = "needs_revision"
                campaign.current_step = "revision_needed"
            
            db.commit()
            
    except Exception as e:
        campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
        if campaign:
            campaign.overall_status = "failed"
            campaign.error_message = f"Redo error: {str(e)}"
            db.commit()
    
    finally:
        db.close()


@router.post("/ads/generate", response_model=AdCampaignResponse)
async def create_ad_campaign(
    request: AdCampaignCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new ad campaign and start the generation pipeline."""
    # Create campaign record
    campaign = AdCampaign(
        user_prompt=request.user_prompt,
        brand_name=request.brand_name,
        brand_description=request.brand_description,
        current_step="init",
        overall_status="pending"
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    
    # Start pipeline in background
    from ..config import get_settings
    settings = get_settings()
    background_tasks.add_task(
        run_ads_pipeline,
        campaign.id,
        settings.database_url
    )
    
    return campaign


@router.get("/ads", response_model=AdCampaignListResponse)
async def list_ad_campaigns(
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


@router.get("/ads/{campaign_id}", response_model=AdCampaignResponse)
async def get_ad_campaign(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific ad campaign."""
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.get("/ads/{campaign_id}/status", response_model=AdCampaignResponse)
async def get_campaign_status(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Get real-time status of a campaign (for polling)."""
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.post("/ads/{campaign_id}/redo", response_model=AdCampaignResponse)
async def redo_campaign_step(
    campaign_id: int,
    request: RedoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Redo a specific step of the campaign."""
    campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Validate step can be redone
    if request.step == "script" and campaign.script_status not in ["completed", "failed", "rejected"]:
        raise HTTPException(status_code=400, detail="Script step not ready for redo")
    if request.step == "image" and campaign.image_status not in ["completed", "failed", "rejected"]:
        raise HTTPException(status_code=400, detail="Image step not ready for redo")
    if request.step == "video" and campaign.video_status not in ["completed", "failed", "rejected"]:
        raise HTTPException(status_code=400, detail="Video step not ready for redo")
    
    # Store feedback if provided
    if request.feedback:
        if request.step == "script":
            campaign.script_feedback = request.feedback
        elif request.step == "image":
            campaign.image_feedback = request.feedback
        elif request.step == "video":
            campaign.video_feedback = request.feedback
        db.commit()
    
    # Start redo in background
    from ..config import get_settings
    settings = get_settings()
    background_tasks.add_task(
        redo_step,
        campaign.id,
        request.step,
        settings.database_url
    )
    
    return campaign
