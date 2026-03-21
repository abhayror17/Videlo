"""
AI Ads Generator Pipeline Service - Multi-Phase Agentic Workflow

This service orchestrates the AI ads generation through 10 phases:
1. UNDERSTAND & ASK - Ask clarification questions
2. BUILD CONTEXT - Convert to structured JSON
3. GENERATE AD STRATEGY - Create ad angles
4. SCRIPT GENERATION - Generate UGC scripts
5. AVATAR GENERATION - Create UGC characters
6. STORYBOARD ENGINE - Break into scenes
7. IMAGE PROMPT GENERATION - Scene image prompts
8. VIDEO PROMPT GENERATION - Scene video prompts
9. BATCH OUTPUT - Return structured output
10. ITERATION MODE - Modify outputs
"""

import json
import asyncio
import aiohttp
import socket
import logging
import time
from typing import Optional, List, Dict, Any
from functools import wraps
from openai import OpenAI
from ..config import get_settings

settings = get_settings()

# Configure logger for ads pipeline
logger = logging.getLogger("ads_pipeline")
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s', datefmt='%H:%M:%S')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# In-memory debug log storage for API access
_debug_logs: Dict[int, List[dict]] = {}  # campaign_id -> list of log entries


def log_phase(phase_name: str):
    """Decorator to log phase execution with timing and results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            campaign_id = kwargs.get('campaign_id', args[0] if args and isinstance(args[0], int) else None)
            
            logger.info(f"[Phase: {phase_name}] Starting...")
            _add_debug_log(campaign_id, phase_name, "start", {"args": str(args)[:200]})
            
            try:
                result = await func(*args, **kwargs)
                elapsed = time.time() - start_time
                
                if isinstance(result, dict) and "error" in result:
                    logger.error(f"[Phase: {phase_name}] Failed in {elapsed:.2f}s - {result.get('error')}")
                    _add_debug_log(campaign_id, phase_name, "error", {
                        "error": result.get("error"),
                        "elapsed_ms": int(elapsed * 1000)
                    })
                else:
                    logger.info(f"[Phase: {phase_name}] Completed in {elapsed:.2f}s")
                    _add_debug_log(campaign_id, phase_name, "complete", {
                        "elapsed_ms": int(elapsed * 1000),
                        "result_keys": list(result.keys()) if isinstance(result, dict) else None
                    })
                
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.exception(f"[Phase: {phase_name}] Exception in {elapsed:.2f}s - {str(e)}")
                _add_debug_log(campaign_id, phase_name, "exception", {
                    "error": str(e),
                    "elapsed_ms": int(elapsed * 1000)
                })
                raise
        return wrapper
    return decorator


def _add_debug_log(campaign_id: Optional[int], phase: str, status: str, data: dict):
    """Add a debug log entry for a campaign."""
    if campaign_id is None:
        return
    
    if campaign_id not in _debug_logs:
        _debug_logs[campaign_id] = []
    
    _debug_logs[campaign_id].append({
        "timestamp": time.time(),
        "phase": phase,
        "status": status,
        "data": data
    })


def get_debug_logs(campaign_id: int) -> List[dict]:
    """Get all debug logs for a campaign."""
    return _debug_logs.get(campaign_id, [])


def clear_debug_logs(campaign_id: int):
    """Clear debug logs for a campaign."""
    if campaign_id in _debug_logs:
        del _debug_logs[campaign_id]


# ==============================================================================
# SYSTEM PROMPTS FOR ALL 10 PHASES
# ==============================================================================

PHASE1_CLARIFICATION_SYSTEM = """You are an elite AI Ad Creation Agent that behaves like a full creative team: Performance marketer, Copywriter, Creative director, Casting director, and Video editor.

## PHASE 1: UNDERSTAND & ASK

Your goal is to generate high-converting UGC-style video ads through a conversational, agentic workflow.

When the user gives a brief, DO NOT generate ads immediately. Instead:
1. Analyze the input
2. Identify missing critical information
3. Ask 3–5 highly relevant clarification questions

Focus on:
- Hook styles (problem-solution, testimonial, curiosity, etc.)
- Target audience specifics
- Tone (funny, emotional, luxury, aggressive, etc.)
- Avatar preference (gender, age, persona)
- Platform (TikTok, Instagram, YouTube Shorts)
- Ad constraints (length, brand voice, do/don't say)

## OUTPUT FORMAT (JSON):
{
  "analysis": "Brief analysis of the user's brief",
  "questions": [
    {
      "id": "q1",
      "question": "The question text",
      "type": "text/select/multiselect",
      "options": ["option1", "option2"] // only for select/multiselect
    }
  ]
}

Be concise. Do not overwhelm the user. Output ONLY valid JSON, no additional text."""


PHASE2_CONTEXT_SYSTEM = """You are an elite AI Ad Creation Agent building structured context for ad creation.

## PHASE 2: BUILD CONTEXT

Convert all information into structured JSON format:

{
  "brand": "Brand name",
  "product": "Product/service description",
  "target_audience": "Detailed target audience description",
  "platform": "Primary platform (TikTok, Instagram, YouTube Shorts)",
  "hooks": ["hook style 1", "hook style 2"],
  "tone": "Primary tone (funny, emotional, luxury, aggressive, etc.)",
  "ad_angles": ["angle1", "angle2"],
  "avatar_preferences": {
    "gender": "preferred gender or 'any'",
    "age_range": "e.g., '25-35'",
    "persona": "e.g., 'fitness enthusiast', 'busy mom', 'tech-savvy professional'"
  },
  "constraints": ["constraint1", "constraint2"]
}

Infer intelligently if data is missing. Output ONLY valid JSON, no additional text."""


PHASE3_STRATEGY_SYSTEM = """You are an elite AI Ad Creation Agent developing ad strategy.

## PHASE 3: GENERATE AD STRATEGY

Create 5 distinct ad angles. Each must include:
- Hook idea: A compelling opening that stops the scroll
- Emotional trigger: The core emotion to evoke
- Why it will convert: Reasoning for effectiveness

## OUTPUT FORMAT (JSON):
{
  "angles": [
    {
      "id": 1,
      "hook_idea": "The hook concept",
      "emotional_trigger": "The emotion to evoke",
      "why_convert": "Why this angle will convert"
    }
  ]
}

Ensure variety across angles. Each should target different emotional triggers and hook styles. Output ONLY valid JSON."""


PHASE4_SCRIPT_SYSTEM = """You are an elite AI Ad Creation Agent writing UGC-style ad scripts.

## PHASE 4: SCRIPT GENERATION

Generate UGC-style ad scripts. Rules:
- Each script must use a DIFFERENT hook
- Use proven frameworks: PAS (Problem-Agitate-Solution), Testimonial, Before/After, Curiosity hook
- First 2 seconds must be a strong scroll-stopping hook
- Keep duration between 10–30 seconds
- Natural, human-like language (UGC creator style)

## OUTPUT FORMAT (JSON):
{
  "scripts": [
    {
      "id": 1,
      "hook": "The opening hook line",
      "framework": "PAS/Testimonial/BeforeAfter/Curiosity",
      "scenes": [
        {"scene": 1, "dialogue": "Spoken words", "visual": "What's shown", "duration": "0-3s"}
      ],
      "cta": "Call to action line"
    }
  ]
}

Ensure variety across scripts. Output ONLY valid JSON."""


PHASE5_AVATAR_SYSTEM = """You are an elite AI Ad Creation Agent designing UGC characters.

## PHASE 5: AVATAR GENERATION

Create 3–5 consistent UGC characters. Each must include:
- Name (based on region, e.g., India → Maya, Rohan; US → Alex, Jordan)
- Age
- Gender
- Detailed physical appearance (LOCK THIS for consistency)
- Outfit style
- Personality vibe

## OUTPUT FORMAT (JSON):
{
  "avatars": [
    {
      "id": 1,
      "name": "Character name",
      "age": 28,
      "gender": "male/female/non-binary",
      "region": "US/India/Europe/etc",
      "appearance": "Detailed physical description - hair, eyes, skin tone, build, distinctive features",
      "outfit_style": "Typical outfit style for this character",
      "personality_vibe": "e.g., friendly, confident, approachable, enthusiastic"
    }
  ]
}

Ensure diverse representation across avatars. Output ONLY valid JSON."""


PHASE6_STORYBOARD_SYSTEM = """You are an elite AI Ad Creation Agent creating storyboards.

## PHASE 6: STORYBOARD ENGINE

For each script, break into scenes with:
- Visual direction
- Camera angle (UGC handheld, close-up, medium shot, etc.)
- Lighting style
- Emotion
- Environment

## OUTPUT FORMAT (JSON):
{
  "scenes": [
    {
      "scene_num": 1,
      "visual_direction": "What the viewer sees",
      "camera_angle": "UGC handheld close-up / medium shot / etc",
      "lighting": "Natural / studio / warm / cool",
      "emotion": "The emotional tone of this scene",
      "environment": "Setting/background"
    }
  ]
}

Maintain UGC authenticity throughout. Output ONLY valid JSON."""


PHASE7_IMAGE_PROMPT_SYSTEM = """You are an elite AI Ad Creation Agent generating image prompts.

## PHASE 7: IMAGE PROMPT GENERATION

Convert each scene into detailed image generation prompts.

Rules:
- Maintain STRICT character consistency
- Maintain environment consistency
- Add realism: imperfect lighting, slight blur, handheld feel
- Avoid over-polished AI look
- Include specific physical traits from avatar

## OUTPUT FORMAT (JSON):
{
  "scene_prompts": [
    {
      "scene_num": 1,
      "image_prompt": "Detailed image generation prompt for this scene"
    }
  ]
}

Prompts should be detailed and optimized for AI image generation. Output ONLY valid JSON."""


PHASE8_VIDEO_PROMPT_SYSTEM = """You are an elite AI Ad Creation Agent generating video prompts.

## PHASE 8: VIDEO PROMPT GENERATION

Convert each scene into img-to-video prompts.

Include:
- Subtle motion (head tilt, hand gestures, blinking, nodding)
- Natural camera shake
- Realistic pacing
- Match dialogue tone

## OUTPUT FORMAT (JSON):
{
  "video_prompts": [
    {
      "scene_num": 1,
      "video_prompt": "Motion description for video generation"
    }
  ]
}

Keep motions subtle and natural for UGC authenticity. Output ONLY valid JSON."""


PHASE10_ITERATION_SYSTEM = """You are an elite AI Ad Creation Agent in iteration mode.

## PHASE 10: ITERATION MODE

Modify outputs based on user commands without restarting the entire process.

Commands can be:
- "make it funnier" - Adjust tone and humor
- "change avatar" - Modify character appearance/style
- "target gym audience" - Adjust targeting and messaging
- "generate more hooks" - Create additional hook variations
- "make it shorter" - Reduce script length
- "add more emotion" - Increase emotional intensity

## OUTPUT FORMAT (JSON):
{
  "changes_made": "Description of what was changed",
  "modified_content": {
    // The modified scripts/avatars/prompts
  }
}

Apply changes intelligently while maintaining overall coherence. Output ONLY valid JSON."""


# ==============================================================================
# LLM CLIENT
# ==============================================================================

def get_llm_client() -> OpenAI:
    """Get OpenAI-compatible client for LLM calls."""
    return OpenAI(
        base_url=settings.iflow_base_url,
        api_key=settings.iflow_api_key,
    )


async def call_llm(system_prompt: str, user_message: str, temperature: float = 0.7) -> dict:
    """
    Generic LLM call with JSON parsing.
    
    Returns parsed JSON or error dict.
    """
    client = get_llm_client()
    
    try:
        logger.debug(f"[LLM] Calling model with prompt length: {len(user_message)}")
        completion = client.chat.completions.create(
            model="kimi-k2",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=temperature,
            timeout=120.0
        )
        
        response_text = completion.choices[0].message.content.strip()
        logger.debug(f"[LLM] Response length: {len(response_text)}")
        
        # Remove potential markdown code blocks
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            if lines[0].startswith("```json"):
                lines = lines[1:]
            elif lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            response_text = "\n".join(lines)
        
        return json.loads(response_text)
        
    except json.JSONDecodeError as e:
        logger.error(f"[LLM] JSON parsing failed: {str(e)}")
        return {"error": f"JSON parsing failed: {str(e)}", "raw_response": response_text[:500] if 'response_text' in dir() else 'N/A'}
    except Exception as e:
        logger.error(f"[LLM] Exception: {str(e)}")
        return {"error": str(e)}


# ==============================================================================
# PHASE 1: CLARIFICATION QUESTIONS
# ==============================================================================

@log_phase("Phase 1: Clarification Questions")
async def generate_clarification_questions(user_prompt: str, campaign_id: int = None) -> dict:
    """
    Phase 1: Generate 3-5 clarification questions based on user's brief.
    
    Returns dict with questions list.
    """
    logger.debug(f"[Phase 1] Input prompt: {user_prompt[:100]}...")
    result = await call_llm(
        PHASE1_CLARIFICATION_SYSTEM,
        f"User's ad brief: {user_prompt}\n\nAnalyze this brief and generate clarification questions.",
        temperature=0.7
    )
    if "error" not in result:
        logger.debug(f"[Phase 1] Generated {len(result.get('questions', []))} questions")
    return result


# ==============================================================================
# PHASE 2: BUILD CONTEXT
# ==============================================================================

@log_phase("Phase 2: Build Context")
async def build_context(
    user_prompt: str,
    answers: List[dict],
    inferred_context: Optional[dict] = None,
    campaign_id: int = None
) -> dict:
    """
    Phase 2: Build structured context from user prompt and answers.
    
    Returns structured context dict.
    """
    logger.debug(f"[Phase 2] Processing {len(answers)} answers")
    context_input = f"User's ad brief: {user_prompt}\n\n"
    
    if answers:
        context_input += "User's answers to clarification questions:\n"
        for answer in answers:
            context_input += f"- {answer.get('question_id', 'Q')}: {answer.get('answer', 'N/A')}\n"
    
    if inferred_context:
        context_input += f"\nInferred context: {json.dumps(inferred_context)}"
    
    result = await call_llm(
        PHASE2_CONTEXT_SYSTEM,
        context_input,
        temperature=0.5
    )
    if "error" not in result:
        logger.debug(f"[Phase 2] Built context with keys: {list(result.keys())}")
    return result


# ==============================================================================
# PHASE 3: AD STRATEGY
# ==============================================================================

@log_phase("Phase 3: Ad Strategy")
async def generate_ad_strategy(context: dict, campaign_id: int = None) -> dict:
    """
    Phase 3: Generate 5 distinct ad angles.
    
    Returns dict with angles list.
    """
    logger.debug(f"[Phase 3] Generating strategy from context")
    result = await call_llm(
        PHASE3_STRATEGY_SYSTEM,
        f"Build ad strategy based on this context:\n{json.dumps(context, indent=2)}",
        temperature=0.8
    )
    if "error" not in result:
        logger.debug(f"[Phase 3] Generated {len(result.get('angles', []))} ad angles")
    return result


# ==============================================================================
# PHASE 4: SCRIPT GENERATION
# ==============================================================================

@log_phase("Phase 4: Script Generation")
async def generate_scripts(
    context: dict,
    ad_angles: List[dict],
    num_scripts: int = 5,
    campaign_id: int = None
) -> dict:
    """
    Phase 4: Generate UGC-style ad scripts.
    
    Returns dict with scripts list.
    """
    logger.debug(f"[Phase 4] Generating {num_scripts} scripts")
    script_input = f"""Generate {num_scripts} UGC-style ad scripts.

Context:
{json.dumps(context, indent=2)}

Ad Angles to use:
{json.dumps(ad_angles, indent=2)}

Each script should use a DIFFERENT hook and framework. Make them natural and conversational like real UGC creators would say it.
"""
    
    result = await call_llm(
        PHASE4_SCRIPT_SYSTEM,
        script_input,
        temperature=0.9
    )
    if "error" not in result:
        logger.debug(f"[Phase 4] Generated {len(result.get('scripts', []))} scripts")
    return result


# ==============================================================================
# PHASE 5: AVATAR GENERATION
# ==============================================================================

@log_phase("Phase 5: Avatar Generation")
async def generate_avatars(
    context: dict,
    num_avatars: int = 3,
    campaign_id: int = None
) -> dict:
    """
    Phase 5: Generate UGC character avatars.
    
    Returns dict with avatars list.
    """
    logger.debug(f"[Phase 5] Generating {num_avatars} avatars")
    avatar_input = f"""Generate {num_avatars} UGC character avatars for ad creation.

Context:
{json.dumps(context, indent=2)}

Avatar preferences:
{json.dumps(context.get('avatar_preferences', {}), indent=2)}

Create diverse, authentic characters that would resonate with the target audience.
"""
    
    result = await call_llm(
        PHASE5_AVATAR_SYSTEM,
        avatar_input,
        temperature=0.8
    )
    if "error" not in result:
        logger.debug(f"[Phase 5] Generated {len(result.get('avatars', []))} avatars")
    return result


# ==============================================================================
# PHASE 6: STORYBOARD ENGINE
# ==============================================================================

@log_phase("Phase 6: Storyboard Engine")
async def generate_storyboard(
    script: dict,
    avatar: dict,
    context: dict,
    campaign_id: int = None
) -> dict:
    """
    Phase 6: Generate storyboard for a script.
    
    Returns dict with scenes list.
    """
    logger.debug(f"[Phase 6] Generating storyboard for script")
    storyboard_input = f"""Create a storyboard for this UGC ad script.

Script:
{json.dumps(script, indent=2)}

Character (Avatar):
{json.dumps(avatar, indent=2)}

Brand Context:
{json.dumps(context, indent=2)}

Break down each scene with visual direction, camera angles, and emotional beats.
"""
    
    result = await call_llm(
        PHASE6_STORYBOARD_SYSTEM,
        storyboard_input,
        temperature=0.7
    )
    if "error" not in result:
        logger.debug(f"[Phase 6] Generated storyboard with {len(result.get('scenes', []))} scenes")
    return result


# ==============================================================================
# PHASE 7: IMAGE PROMPT GENERATION
# ==============================================================================

@log_phase("Phase 7: Image Prompt Generation")
async def generate_image_prompts(
    storyboard: dict,
    avatar: dict,
    context: dict,
    campaign_id: int = None
) -> dict:
    """
    Phase 7: Generate image prompts for each scene.
    
    Returns dict with scene prompts.
    """
    logger.debug(f"[Phase 7] Generating image prompts")
    prompt_input = f"""Generate detailed image generation prompts for each scene.

Storyboard:
{json.dumps(storyboard, indent=2)}

Character (LOCKED - maintain consistency):
{json.dumps(avatar, indent=2)}

Brand Style:
{json.dumps(context, indent=2)}

Important: Maintain STRICT consistency with the character appearance across all scenes.
Add realism markers: imperfect lighting, slight blur, handheld feel. Avoid over-polished AI look.
"""
    
    result = await call_llm(
        PHASE7_IMAGE_PROMPT_SYSTEM,
        prompt_input,
        temperature=0.6
    )
    if "error" not in result:
        logger.debug(f"[Phase 7] Generated {len(result.get('scene_prompts', []))} image prompts")
    return result


# ==============================================================================
# PHASE 8: VIDEO PROMPT GENERATION
# ==============================================================================

@log_phase("Phase 8: Video Prompt Generation")
async def generate_video_prompts(
    storyboard: dict,
    script: dict,
    context: dict,
    campaign_id: int = None
) -> dict:
    """
    Phase 8: Generate video prompts for each scene.
    
    Returns dict with video prompts.
    """
    logger.debug(f"[Phase 8] Generating video prompts")
    video_input = f"""Generate img-to-video prompts for each scene.

Storyboard:
{json.dumps(storyboard, indent=2)}

Script Dialogue (match motion to dialogue):
{json.dumps(script, indent=2)}

Context:
{json.dumps(context, indent=2)}

Important: Keep motions subtle and natural - head tilts, hand gestures, blinking, nodding.
Match the motion intensity to the emotional tone of the dialogue.
"""
    
    result = await call_llm(
        PHASE8_VIDEO_PROMPT_SYSTEM,
        video_input,
        temperature=0.5
    )
    if "error" not in result:
        logger.debug(f"[Phase 8] Generated {len(result.get('video_prompts', []))} video prompts")
    return result


# ==============================================================================
# PHASE 9: BATCH OUTPUT
# ==============================================================================

async def generate_batch_output(
    campaign_id: int,
    db_session
) -> dict:
    """
    Phase 9: Compile all outputs into a structured batch response.
    
    Returns complete campaign output.
    """
    from ..models import AdCampaign, AdAvatar, AdScript, AdStoryboard, AdScenePrompt
    
    campaign = db_session.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        return {"error": "Campaign not found"}
    
    avatars = db_session.query(AdAvatar).filter(AdAvatar.campaign_id == campaign_id).all()
    scripts = db_session.query(AdScript).filter(AdScript.campaign_id == campaign_id).all()
    storyboards = db_session.query(AdStoryboard).filter(AdStoryboard.campaign_id == campaign_id).all()
    
    # Compile scene prompts
    all_scene_prompts = []
    for storyboard in storyboards:
        prompts = db_session.query(AdScenePrompt).filter(
            AdScenePrompt.storyboard_id == storyboard.id
        ).all()
        all_scene_prompts.extend([{
            "scene_num": p.scene_num,
            "image_prompt": p.image_prompt,
            "video_prompt": p.video_prompt,
            "image_url": p.image_url,
            "video_url": p.video_url
        } for p in prompts])
    
    return {
        "campaign_id": campaign_id,
        "phase": 9,
        "context": campaign.context,
        "ad_angles": campaign.ad_angles,
        "avatars": [{
            "id": a.id,
            "name": a.name,
            "age": a.age,
            "gender": a.gender,
            "region": a.region,
            "appearance": a.appearance,
            "outfit_style": a.outfit_style,
            "personality_vibe": a.personality_vibe
        } for a in avatars],
        "scripts": [{
            "id": s.id,
            "script_id": s.script_id,
            "hook": s.hook,
            "cta": s.cta,
            "framework": s.framework,
            "scenes": s.scenes
        } for s in scripts],
        "storyboards": [{
            "script_id": s.script_id,
            "scenes": s.scenes
        } for s in storyboards],
        "scene_prompts": all_scene_prompts
    }


# ==============================================================================
# PHASE 10: ITERATION MODE
# ==============================================================================

async def apply_iteration(
    campaign_id: int,
    command: str,
    target: Optional[str],
    db_session
) -> dict:
    """
    Phase 10: Apply iteration commands to modify outputs.
    
    Returns dict with changes made and updated data.
    """
    from ..models import AdCampaign, AdAvatar, AdScript
    
    campaign = db_session.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
    if not campaign:
        return {"error": "Campaign not found"}
    
    # Determine what to modify
    target_type = target or "all"
    
    iteration_input = f"""Apply the following iteration command: "{command}"

Target to modify: {target_type}

Current context:
{json.dumps(campaign.context, indent=2) if campaign.context else 'Not set'}

Current ad angles:
{json.dumps(campaign.ad_angles, indent=2) if campaign.ad_angles else 'Not set'}

Iteration count so far: {campaign.iteration_count}

Make targeted modifications that improve the output while maintaining overall coherence.
"""
    
    result = await call_llm(
        PHASE10_ITERATION_SYSTEM,
        iteration_input,
        temperature=0.7
    )
    
    if "error" not in result:
        # Update campaign
        campaign.iteration_count += 1
        campaign.last_iteration_command = command
        
        # Apply modifications if provided
        if "modified_content" in result:
            modified = result["modified_content"]
            
            if "context" in modified and target_type in ["all", "context"]:
                campaign.context = {**(campaign.context or {}), **modified["context"]}
            
            if "ad_angles" in modified and target_type in ["all", "hooks"]:
                campaign.ad_angles = modified["ad_angles"]
            
            if "avatars" in modified and target_type in ["all", "avatars"]:
                # Update avatars
                for avatar_data in modified["avatars"]:
                    avatar = db_session.query(AdAvatar).filter(
                        AdAvatar.campaign_id == campaign_id,
                        AdAvatar.id == avatar_data.get("id")
                    ).first()
                    if avatar:
                        for key, value in avatar_data.items():
                            if key != "id" and hasattr(avatar, key):
                                setattr(avatar, key, value)
            
            if "scripts" in modified and target_type in ["all", "scripts"]:
                # Update scripts
                for script_data in modified["scripts"]:
                    script = db_session.query(AdScript).filter(
                        AdScript.campaign_id == campaign_id,
                        AdScript.id == script_data.get("id")
                    ).first()
                    if script:
                        for key, value in script_data.items():
                            if key != "id" and hasattr(script, key):
                                setattr(script, key, value)
        
        db_session.commit()
    
    return result


# ==============================================================================
# DEAPI INTEGRATION FOR IMAGE/VIDEO GENERATION
# ==============================================================================

class AdsPipelineClient:
    """Client for managing image/video generation with deAPI."""
    
    def __init__(self):
        self.deapi_base_url = settings.deapi_base_url
        self.deapi_api_key = settings.deapi_api_key
        self.headers = {
            "Authorization": f"Bearer {self.deapi_api_key}",
        }
    
    def _create_connector(self) -> aiohttp.TCPConnector:
        """Create an aiohttp connector forced to IPv4."""
        return aiohttp.TCPConnector(
            family=socket.AF_INET,
            ssl=False,
            limit=10
        )
    
    async def submit_text2img(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 768,
        model: str = "ZImageTurbo_INT8"
    ) -> dict:
        """Submit text-to-image request to deAPI."""
        payload = {
            "prompt": prompt,
            "model": model,
            "width": width,
            "height": height,
            "guidance": 3.5,
            "steps": 4,
            "seed": -1
        }
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as session:
            async with session.post(
                f"{self.deapi_base_url}/api/v1/client/txt2img",
                json=payload
            ) as response:
                response.raise_for_status()
                result = await response.json()
                return result.get("data", result)
    
    async def submit_img2video(
        self,
        image_url: str,
        prompt: str,
        width: int = 768,
        height: int = 768,
        model: str = "Ltx2_19B_Dist_FP8",
        frames: int = 48
    ) -> dict:
        """Submit image-to-video request to deAPI."""
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as session:
            # Download the image first
            async with session.get(image_url) as img_response:
                img_response.raise_for_status()
                image_data = await img_response.read()
            
            # Build multipart form data
            data = aiohttp.FormData()
            data.add_field('first_frame_image', image_data, filename='first_frame.png', content_type='image/png')
            data.add_field('prompt', prompt)
            data.add_field('model', model)
            data.add_field('width', str(width))
            data.add_field('height', str(height))
            data.add_field('guidance', '3.5')
            data.add_field('steps', '20')
            data.add_field('frames', str(frames))
            data.add_field('seed', '-1')
            data.add_field('fps', '24')
            
            async with session.post(
                f"{self.deapi_base_url}/api/v1/client/img2video",
                data=data
            ) as response:
                response.raise_for_status()
                result = await response.json()
                return result.get("data", result)
    
    async def get_request_status(self, request_id: str) -> dict:
        """Get the status of a deAPI request."""
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            async with session.get(
                f"{self.deapi_base_url}/api/v1/client/request-status/{request_id}"
            ) as response:
                response.raise_for_status()
                result = await response.json()
                return result.get("data", result)


# Singleton instance
_pipeline_client: Optional[AdsPipelineClient] = None


def get_pipeline_client() -> AdsPipelineClient:
    global _pipeline_client
    if _pipeline_client is None:
        _pipeline_client = AdsPipelineClient()
    return _pipeline_client