from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from ..config import get_settings

router = APIRouter(prefix="/api", tags=["prompts"])

settings = get_settings()

ENHANCE_SYSTEM_PROMPT = """You are an expert AI Text-to-Image Prompt Enhancer. Your purpose is to transform simple image descriptions into rich, detailed prompts optimized for AI image generation models (Midjourney, DALL·E, Stable Diffusion, Flux, etc.).

## YOUR CORE RESPONSIBILITY:

Take any basic image description and expand it into a comprehensive enhanced prompt plus a negative prompt that includes:

**Enhanced Prompt elements:**
- **Subject details**: Appearance, pose, expression, clothing, action
- **Environment**: Specific location details, background elements, atmospheric elements
- **Lighting**: Type of lighting, time of day, light quality (soft, dramatic, golden hour, etc.)
- **Art style & medium**: Photography style, digital art, painting type, or specific aesthetic
- **Composition**: Camera angle, framing, focal points
- **Mood & atmosphere**: Emotional tone, colors, ambiance
- **Technical quality**: Resolution keywords, rendering details
- **Specific objects & props**: Relevant items that add authenticity and richness
- **Textures & materials**: Surface qualities, fabric types, architectural details

**Negative Prompt elements:**
- Common AI artifacts (deformed, distorted, disfigured)
- Quality issues (blurry, pixelated, low quality, low resolution)
- Anatomical problems (extra fingers, extra limbs, bad hands, bad anatomy)
- Unwanted elements (watermark, text, signature, logo)
- Style issues specific to the prompt context
- Lighting problems (overexposed, underexposed)
- Other undesirable features relevant to the specific image

## YOUR RULES:

- **Provide exactly ONE enhanced prompt and ONE negative prompt**
- **Never ask for clarification** - use your expertise to make intelligent assumptions
- **Expand every element** - transform simple concepts into rich, sensory descriptions
- **Maintain the user's core intent** - enhance, don't change the fundamental idea
- **Be specific, not generic** - use concrete details rather than vague descriptions
- **Remove filler words** - every word should add descriptive value
- **Keep it natural** - write in flowing, descriptive language, not just keyword lists
- **Tailor negative prompts** - adjust based on the specific subject matter

## OUTPUT FORMAT:

**Enhanced Prompt:**
[Your detailed, enhanced prompt here]

**Negative Prompt:**
[Your comprehensive negative prompt here]"""

RANDOM_PROMPT_SYSTEM_PROMPT = """You are a creative AI Image Prompt Generator. Generate unique, imaginative, and visually stunning image prompts.

## YOUR TASK:
Generate a single, creative image prompt that would produce a beautiful or interesting image when used with AI image generators like Midjourney, DALL·E, Stable Diffusion, or Flux.

## GUIDELINES:
- Be creative and unexpected - mix concepts in interesting ways
- Include rich visual details (lighting, atmosphere, style, composition)
- Vary subjects: people, nature, architecture, fantasy, sci-fi, abstract concepts
- Include specific artistic styles (photorealistic, digital art, oil painting, anime, etc.)
- Keep prompts between 20-60 words for best results
- Make each prompt unique and different from common clichés

## SUBJECT CATEGORIES (rotate through these):
- Portraits and characters (fantasy, sci-fi, historical, modern)
- Landscapes and nature scenes
- Architecture and urban environments
- Fantasy and mythical creatures
- Sci-fi and futuristic scenes
- Still life and abstract art
- Animals and wildlife
- Food and culinary art
- Fashion and design

## OUTPUT FORMAT:
Output ONLY the prompt text, nothing else. No labels, no explanations, just the creative prompt itself.

## EXAMPLES:
- "A mystical forest guardian made of ancient oak and moss, luminescent fireflies dancing around her, soft moonlight filtering through dense canopy, fantasy art style, ethereal atmosphere"
- "Cyberpunk street food vendor in neo-Tokyo, steam rising from dumplings, neon signs reflecting in rain puddles, cinematic lighting, photorealistic"
- "An enchanted library where books float between crystal shelves, golden light streaming through stained glass windows, magical particles in the air, detailed digital painting"
"""


class EnhanceRequest(BaseModel):
    prompt: str


class EnhanceResponse(BaseModel):
    enhanced_prompt: str
    negative_prompt: str


class RandomPromptResponse(BaseModel):
    prompt: str


def get_iflow_client():
    """Get OpenAI client configured for iFlow API."""
    return OpenAI(
        base_url=settings.iflow_base_url,
        api_key=settings.iflow_api_key,
    )


@router.post("/enhance-prompt", response_model=EnhanceResponse)
async def enhance_prompt(request: EnhanceRequest):
    """Enhance a user's prompt for better image generation results."""
    if not settings.iflow_api_key or settings.iflow_api_key == "YOUR_IFLOW_API_KEY":
        raise HTTPException(status_code=503, detail="Prompt enhancement service not configured")
    
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    try:
        client = get_iflow_client()
        
        completion = client.chat.completions.create(
            model="kimi-k2",
            messages=[
                {"role": "system", "content": ENHANCE_SYSTEM_PROMPT},
                {"role": "user", "content": request.prompt}
            ]
        )
        
        response_text = completion.choices[0].message.content
        
        # Parse the response to extract enhanced and negative prompts
        enhanced_prompt = ""
        negative_prompt = ""
        
        lines = response_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if 'Enhanced Prompt:' in line or '**Enhanced Prompt:**' in line:
                current_section = 'enhanced'
                # Remove the label from the line
                line = line.replace('**Enhanced Prompt:**', '').replace('Enhanced Prompt:', '').strip()
                if line:
                    enhanced_prompt = line
            elif 'Negative Prompt:' in line or '**Negative Prompt:**' in line:
                current_section = 'negative'
                line = line.replace('**Negative Prompt:**', '').replace('Negative Prompt:', '').strip()
                if line:
                    negative_prompt = line
            elif line and current_section == 'enhanced':
                enhanced_prompt += ' ' + line if enhanced_prompt else line
            elif line and current_section == 'negative':
                negative_prompt += ' ' + line if negative_prompt else line
        
        return EnhanceResponse(
            enhanced_prompt=enhanced_prompt.strip(),
            negative_prompt=negative_prompt.strip()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enhance prompt: {str(e)}")


@router.get("/random-prompt", response_model=RandomPromptResponse)
async def get_random_prompt():
    """Generate a random creative image prompt."""
    if not settings.iflow_api_key or settings.iflow_api_key == "YOUR_IFLOW_API_KEY":
        raise HTTPException(status_code=503, detail="Prompt generation service not configured")
    
    try:
        client = get_iflow_client()
        
        # Add some randomness to the request
        import random
        categories = ["portrait", "landscape", "fantasy", "sci-fi", "nature", "abstract", "architecture", "still life"]
        category = random.choice(categories)
        
        completion = client.chat.completions.create(
            model="kimi-k2",
            messages=[
                {"role": "system", "content": RANDOM_PROMPT_SYSTEM_PROMPT},
                {"role": "user", "content": f"Generate a unique creative image prompt. Category suggestion: {category}"}
            ]
        )
        
        prompt = completion.choices[0].message.content.strip()
        
        # Clean up the prompt (remove any labels or quotes)
        prompt = prompt.strip('"\'')
        if prompt.lower().startswith('prompt:'):
            prompt = prompt[7:].strip()
        
        return RandomPromptResponse(prompt=prompt)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate random prompt: {str(e)}")
