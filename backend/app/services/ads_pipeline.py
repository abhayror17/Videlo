"""
AI Ads Generator Pipeline Service

This service orchestrates the AI ads generation pipeline:
1. Enhance user prompt for ad context
2. Generate ad script
3. Create brand/product image (text2img)
4. Generate video from image (img2video)
5. QA agent checks quality
"""

import json
import asyncio
import aiohttp
import socket
from typing import Optional, Tuple
from openai import OpenAI
from ..config import get_settings

settings = get_settings()


# System prompts for different stages
AD_PROMPT_ENHANCER_SYSTEM = """You are an expert Advertising Prompt Enhancer. Your role is to transform basic ad concepts into rich, detailed creative briefs that will guide AI-generated ad content.

## YOUR TASK:
Transform the user's ad concept into a comprehensive creative brief that includes:
1. Enhanced ad concept description
2. Visual style and mood direction
3. Key messaging points
4. Target audience insights

## GUIDELINES:
- Maintain the core brand identity and messaging
- Add creative direction that enhances visual appeal
- Include emotional and psychological triggers
- Consider platform-appropriate formats (social media, TV, digital)
- Add specific visual cues (colors, lighting, composition)
- Include brand personality elements

## OUTPUT FORMAT (JSON):
{
  "enhanced_prompt": "Detailed ad concept with visual direction...",
  "visual_style": "Description of visual style (modern, minimalist, bold, etc.)",
  "mood": "Emotional tone (energetic, sophisticated, playful, etc.)",
  "color_palette": "Suggested colors for the ad",
  "key_message": "The main message the ad should convey",
  "target_audience": "Who the ad is targeting"
}

Output ONLY valid JSON, no additional text."""

SCRIPT_GENERATOR_SYSTEM = """You are an expert Ad Script Writer. Create compelling, concise ad scripts optimized for video content.

## YOUR TASK:
Generate a professional ad script based on the enhanced prompt and brand information.

## SCRIPT REQUIREMENTS:
- Length: 15-30 seconds (short-form) or 60 seconds (long-form)
- Include clear call-to-action
- Emotional hook in the first 3 seconds
- Clear brand mention
- Memorable tagline or closing

## OUTPUT FORMAT (JSON):
{
  "script": "The full ad script text...",
  "duration_seconds": 15,
  "hook": "The opening hook line",
  "call_to_action": "The CTA line",
  "tagline": "Memorable closing line",
  "visual_notes": "Notes for visual direction",
  "scene_breakdown": [
    {"timestamp": "0-3s", "description": "Opening scene description"},
    {"timestamp": "3-10s", "description": "Main content scene"},
    {"timestamp": "10-15s", "description": "Closing/CTA scene"}
  ]
}

Output ONLY valid JSON, no additional text."""

QA_AGENT_SYSTEM = """You are a QA Specialist for AI-Generated Ad Content. Your role is to critically evaluate ad scripts, images, and videos for quality, brand alignment, and effectiveness.

## EVALUATION CRITERIA:

### Script Quality:
- Clarity and conciseness
- Strong hook and call-to-action
- Brand voice consistency
- Appropriate length for format
- Emotional impact
- Grammar and language quality

### Image Quality:
- Visual appeal and composition
- Brand alignment (colors, style, mood)
- Professional appearance
- Appropriate for target audience
- No visual artifacts or issues

### Video Quality:
- Smooth motion and transitions
- Consistent with image source
- Appropriate pacing
- No flickering or artifacts
- Engaging movement

## BRAND ALIGNMENT CHECK:
- Does it match brand personality?
- Are brand colors/style represented?
- Is messaging consistent?
- Is target audience appropriate?

## OUTPUT FORMAT (JSON):
{
  "approved": true/false,
  "overall_score": 1-10,
  "feedback": "Brief overall feedback",
  "details": {
    "script": {
      "score": 1-10,
      "approved": true/false,
      "issues": ["issue1", "issue2"],
      "strengths": ["strength1", "strength2"]
    },
    "image": {
      "score": 1-10,
      "approved": true/false,
      "issues": ["issue1"],
      "strengths": ["strength1"]
    },
    "video": {
      "score": 1-10,
      "approved": true/false,
      "issues": ["issue1"],
      "strengths": ["strength1"]
    },
    "brand_alignment": {
      "score": 1-10,
      "notes": "Brand alignment assessment"
    }
  },
  "recommendations": ["What should be improved if not approved"]
}

Be strict but fair. Approve content that meets professional standards. Output ONLY valid JSON."""


def get_llm_client() -> OpenAI:
    """Get OpenAI-compatible client for LLM calls."""
    return OpenAI(
        base_url=settings.iflow_base_url,
        api_key=settings.iflow_api_key,
    )


async def enhance_prompt_for_ads(
    user_prompt: str,
    brand_name: Optional[str] = None,
    brand_description: Optional[str] = None
) -> dict:
    """
    Enhance user's ad prompt with detailed creative direction.
    
    Returns dict with enhanced_prompt and additional metadata.
    """
    client = get_llm_client()
    
    context = f"Ad Concept: {user_prompt}"
    if brand_name:
        context += f"\nBrand Name: {brand_name}"
    if brand_description:
        context += f"\nBrand Description: {brand_description}"
    
    completion = client.chat.completions.create(
        model="kimi-k2",
        messages=[
            {"role": "system", "content": AD_PROMPT_ENHANCER_SYSTEM},
            {"role": "user", "content": context}
        ],
        temperature=0.7
    )
    
    response_text = completion.choices[0].message.content.strip()
    
    # Parse JSON response
    try:
        # Remove potential markdown code blocks
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        result = json.loads(response_text)
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        result = {
            "enhanced_prompt": response_text,
            "visual_style": "modern",
            "mood": "professional",
            "color_palette": "brand colors",
            "key_message": user_prompt,
            "target_audience": "general"
        }
    
    return result


async def generate_ad_script(
    enhanced_prompt: str,
    brand_name: Optional[str] = None,
    visual_style: Optional[str] = None,
    duration: int = 15
) -> dict:
    """
    Generate ad script based on enhanced prompt.
    
    Returns dict with script and scene breakdown.
    """
    client = get_llm_client()
    
    context = f"Enhanced Ad Concept: {enhanced_prompt}"
    if brand_name:
        context += f"\nBrand Name: {brand_name}"
    if visual_style:
        context += f"\nVisual Style: {visual_style}"
    context += f"\nTarget Duration: {duration} seconds"
    
    completion = client.chat.completions.create(
        model="kimi-k2",
        messages=[
            {"role": "system", "content": SCRIPT_GENERATOR_SYSTEM},
            {"role": "user", "content": context}
        ],
        temperature=0.8
    )
    
    response_text = completion.choices[0].message.content.strip()
    
    # Parse JSON response
    try:
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        result = json.loads(response_text)
    except json.JSONDecodeError:
        result = {
            "script": response_text,
            "duration_seconds": duration,
            "hook": "",
            "call_to_action": "",
            "tagline": "",
            "visual_notes": "",
            "scene_breakdown": []
        }
    
    return result


async def generate_image_prompt_from_script(
    script_data: dict,
    enhanced_prompt_data: dict,
    brand_name: Optional[str] = None
) -> str:
    """
    Create an image generation prompt from script and enhanced prompt data.
    This prompt will be used for text2img generation.
    """
    visual_style = enhanced_prompt_data.get("visual_style", "modern, professional")
    mood = enhanced_prompt_data.get("mood", "engaging")
    color_palette = enhanced_prompt_data.get("color_palette", "")
    visual_notes = script_data.get("visual_notes", "")
    
    # Construct a detailed image prompt
    prompt_parts = [
        f"Professional advertisement image",
        f"Style: {visual_style}",
        f"Mood: {mood}",
    ]
    
    if brand_name:
        prompt_parts.append(f"For brand: {brand_name}")
    
    if color_palette:
        prompt_parts.append(f"Color scheme: {color_palette}")
    
    if visual_notes:
        prompt_parts.append(f"Visual direction: {visual_notes}")
    
    # Add quality keywords
    prompt_parts.extend([
        "high quality",
        "professional photography",
        "clean composition",
        "commercial advertising style",
        "4k resolution"
    ])
    
    return ", ".join(prompt_parts)


async def qa_check_content(
    script: str,
    image_url: Optional[str] = None,
    video_url: Optional[str] = None,
    brand_name: Optional[str] = None,
    brand_description: Optional[str] = None,
    enhanced_prompt: Optional[str] = None
) -> dict:
    """
    Run QA check on generated content.
    
    Returns dict with approval status, scores, and feedback.
    """
    client = get_llm_client()
    
    # Build context for QA
    context_parts = ["Please evaluate the following ad content:"]
    
    if brand_name:
        context_parts.append(f"\nBrand: {brand_name}")
    if brand_description:
        context_parts.append(f"Brand Description: {brand_description}")
    
    context_parts.append(f"\n\nSCRIPT:\n{script}")
    
    if enhanced_prompt:
        context_parts.append(f"\n\nENHANCED CONCEPT:\n{enhanced_prompt}")
    
    if image_url:
        context_parts.append(f"\n\nIMAGE URL: {image_url}")
        context_parts.append("(Note: Evaluate based on URL description if you cannot view images)")
    
    if video_url:
        context_parts.append(f"\n\nVIDEO URL: {video_url}")
        context_parts.append("(Note: Evaluate video based on available information)")
    
    context = "\n".join(context_parts)
    
    completion = client.chat.completions.create(
        model="kimi-k2",
        messages=[
            {"role": "system", "content": QA_AGENT_SYSTEM},
            {"role": "user", "content": context}
        ],
        temperature=0.3  # Lower temperature for more consistent evaluation
    )
    
    response_text = completion.choices[0].message.content.strip()
    
    # Parse JSON response
    try:
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        result = json.loads(response_text)
    except json.JSONDecodeError:
        result = {
            "approved": False,
            "overall_score": 5,
            "feedback": "Could not parse QA response",
            "details": {},
            "recommendations": ["Manual review required"]
        }
    
    return result


class AdsPipelineClient:
    """Client for managing the ads pipeline with deAPI integration."""
    
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
                # deAPI returns {"data": {"request_id": "..."}}
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
        """Submit image-to-video request to deAPI using URL (downloads image first)."""
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
                # deAPI returns {"data": {"request_id": "..."}}
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
                # deAPI returns {"data": {...}}
                return result.get("data", result)


# Singleton instance
_pipeline_client: Optional[AdsPipelineClient] = None


def get_pipeline_client() -> AdsPipelineClient:
    global _pipeline_client
    if _pipeline_client is None:
        _pipeline_client = AdsPipelineClient()
    return _pipeline_client
