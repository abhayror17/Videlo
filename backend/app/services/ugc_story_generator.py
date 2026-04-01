"""
UGC Story Generator Service for AI Ads Creator.

Generates compelling UGC-style ad stories with multiple scenes and shots
based on character and product references.
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .ads_pipeline import get_llm_client, call_llm


@dataclass
class UGCShot:
    """A single shot in a scene."""
    shot_num: int
    duration_sec: int
    frame_description: str
    action: str
    dialogue: str
    camera_angle: str
    lighting: str
    audio_notes: str


@dataclass
class UGCScene:
    """A scene in the ad story."""
    scene_num: int
    scene_name: str
    setting: str
    mood: str
    shots: List[UGCShot] = field(default_factory=list)


@dataclass
class UGCCharacter:
    """A character in the UGC ad."""
    name: str
    role: str  # protagonist, supporter, etc.
    age: int
    gender: str
    appearance: str
    outfit: str
    personality: str


@dataclass
class UGCProduct:
    """Product information for the ad."""
    name: str
    category: str
    description: str
    key_features: List[str]
    visual_description: str


@dataclass
class UGCAdStory:
    """Complete UGC ad story with scenes and shots."""
    story_id: str
    title: str
    total_duration_sec: int
    target_platform: str
    characters: List[UGCCharacter]
    product: UGCProduct
    setting: str
    scenes: List[UGCScene]
    hook: str
    cta: str
    inspiration_prompts: List[Dict[str, Any]] = field(default_factory=list)


# System prompt for UGC story generation
UGC_STORY_SYSTEM_PROMPT = """You are an expert UGC (User Generated Content) Ad Story Creator specializing in creating authentic, engaging short-form video ads.

Your task is to create a compelling 15-second UGC ad story broken into multiple 5-second segments that can be merged together.

## GUIDELINES:

1. **Authentic UGC Style**: Create content that feels like real users sharing genuine experiences, not polished commercials
2. **Character Consistency**: Characters must remain visually and personality-consistent across all scenes
3. **Product Integration**: Product should be featured naturally, not forced
4. **Scene Flow**: Each scene should transition smoothly to the next
5. **Shot Variety**: Use different camera angles and framing to maintain visual interest
6. **Audio Design**: Include notes for ambient sounds and dialogue

## OUTPUT FORMAT (JSON):

{
  "title": "Ad story title",
  "hook": "Opening hook line that stops the scroll",
  "cta": "Call to action",
  "target_platform": "Instagram/TikTok/YouTube Shorts",
  "total_duration_sec": 15,
  "setting": "Detailed setting description",
  "characters": [
    {
      "name": "Character name",
      "role": "protagonist/supporter",
      "age": 25,
      "gender": "female/male",
      "appearance": "Detailed physical description",
      "outfit": "What they're wearing",
      "personality": "Character personality traits"
    }
  ],
  "product": {
    "name": "Product name",
    "category": "Product category",
    "key_features": ["Feature 1", "Feature 2"],
    "visual_description": "How the product looks"
  },
  "scenes": [
    {
      "scene_num": 1,
      "scene_name": "Scene title",
      "setting": "Specific setting for this scene",
      "mood": "Emotional mood",
      "shots": [
        {
          "shot_num": 1,
          "duration_sec": 5,
          "frame_description": "Detailed visual description for first frame generation",
          "action": "What happens in this shot",
          "dialogue": "Spoken lines",
          "camera_angle": "e.g., medium shot, close-up, wide",
          "lighting": "e.g., warm golden, soft ambient",
          "audio_notes": "Ambient sounds, music notes"
        }
      ]
    }
  ]
}

## SHOT STRUCTURE (for 15-second ad):
- Scene 1: Hook (5 seconds) - Grab attention, introduce product
- Scene 2: Experience (5 seconds) - Show product in use, benefits
- Scene 3: Reaction/CTA (5 seconds) - Emotional payoff, call to action

Each shot MUST include:
1. **frame_description**: Detailed description for AI image generation (first frame)
2. **action**: What the character does
3. **dialogue**: Natural UGC-style dialogue
4. **camera_angle**: Shot composition
5. **lighting**: Lighting style
6. **audio_notes**: Sound design

Output ONLY valid JSON, no additional text."""


class UGCStoryGenerator:
    """Generator for UGC-style ad stories."""
    
    def __init__(self):
        self.llm_client = get_llm_client()
    
    async def generate_story(
        self,
        product_name: str,
        product_description: str,
        product_category: str,
        character_name: Optional[str] = None,
        character_description: Optional[str] = None,
        target_audience: Optional[str] = None,
        platform: str = "Instagram",
        ad_goal: str = "product_awareness",
        tone: str = "authentic",
        setting_preference: Optional[str] = None,
        inspiration_prompts: Optional[List[Dict]] = None
    ) -> UGCAdStory:
        """
        Generate a complete UGC ad story.
        
        Args:
            product_name: Name of the product
            product_description: Product description
            product_category: Product category (perfume, tech, fashion, etc.)
            character_name: Optional character name
            character_description: Optional character appearance/description
            target_audience: Target audience description
            platform: Target platform (Instagram, TikTok, YouTube)
            ad_goal: Advertising goal (awareness, conversion, engagement)
            tone: Ad tone (authentic, luxury, fun, emotional)
            setting_preference: Preferred setting/location
            inspiration_prompts: Optional matched prompt inspirations
        
        Returns:
            UGCAdStory object with complete story structure
        """
        
        # Build the user prompt
        user_prompt = f"""Create a UGC ad story for:

**Product**: {product_name}
**Category**: {product_category}
**Description**: {product_description}
**Platform**: {platform}
**Goal**: {ad_goal}
**Tone**: {tone}
"""
        
        if character_name:
            user_prompt += f"\n**Character Name**: {character_name}"
        
        if character_description:
            user_prompt += f"\n**Character Description**: {character_description}"
        
        if target_audience:
            user_prompt += f"\n**Target Audience**: {target_audience}"
        
        if setting_preference:
            user_prompt += f"\n**Setting Preference**: {setting_preference}"
        
        if inspiration_prompts:
            user_prompt += "\n\n**Inspiration Prompts** (use for visual style reference):\n"
            for i, prompt in enumerate(inspiration_prompts[:3], 1):
                user_prompt += f"{i}. {prompt.get('title', 'Prompt')}: {prompt.get('prompt', '')[:200]}...\n"
        
        # Call LLM to generate story
        result = await call_llm(UGC_STORY_SYSTEM_PROMPT, user_prompt, temperature=0.8)
        
        if "error" in result:
            raise Exception(f"Failed to generate story: {result['error']}")
        
        return self._parse_story_result(result, inspiration_prompts)
    
    def _parse_story_result(
        self,
        result: Dict[str, Any],
        inspiration_prompts: Optional[List[Dict]] = None
    ) -> UGCAdStory:
        """Parse LLM result into UGCAdStory object."""
        
        # Parse characters
        characters = []
        for char_data in result.get("characters", []):
            characters.append(UGCCharacter(
                name=char_data.get("name", "Character"),
                role=char_data.get("role", "protagonist"),
                age=char_data.get("age", 25),
                gender=char_data.get("gender", "female"),
                appearance=char_data.get("appearance", ""),
                outfit=char_data.get("outfit", ""),
                personality=char_data.get("personality", "")
            ))
        
        # Parse product
        product_data = result.get("product", {})
        product = UGCProduct(
            name=product_data.get("name", "Product"),
            category=product_data.get("category", ""),
            description=product_data.get("visual_description", ""),
            key_features=product_data.get("key_features", []),
            visual_description=product_data.get("visual_description", "")
        )
        
        # Parse scenes
        scenes = []
        for scene_data in result.get("scenes", []):
            shots = []
            for shot_data in scene_data.get("shots", []):
                shots.append(UGCShot(
                    shot_num=shot_data.get("shot_num", 1),
                    duration_sec=shot_data.get("duration_sec", 5),
                    frame_description=shot_data.get("frame_description", ""),
                    action=shot_data.get("action", ""),
                    dialogue=shot_data.get("dialogue", ""),
                    camera_angle=shot_data.get("camera_angle", "medium shot"),
                    lighting=shot_data.get("lighting", "natural"),
                    audio_notes=shot_data.get("audio_notes", "")
                ))
            
            scenes.append(UGCScene(
                scene_num=scene_data.get("scene_num", 1),
                scene_name=scene_data.get("scene_name", f"Scene {scene_data.get('scene_num', 1)}"),
                setting=scene_data.get("setting", ""),
                mood=scene_data.get("mood", ""),
                shots=shots
            ))
        
        return UGCAdStory(
            story_id=f"ugc_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=result.get("title", "UGC Ad Story"),
            total_duration_sec=result.get("total_duration_sec", 15),
            target_platform=result.get("target_platform", "Instagram"),
            characters=characters,
            product=product,
            setting=result.get("setting", ""),
            scenes=scenes,
            hook=result.get("hook", ""),
            cta=result.get("cta", ""),
            inspiration_prompts=inspiration_prompts or []
        )
    
    def generate_image_prompt_for_shot(
        self,
        shot: UGCShot,
        character: UGCCharacter,
        product: UGCProduct,
        aspect_ratio: str = "16:9"
    ) -> str:
        """
        Generate an optimized image generation prompt for a shot.
        
        Args:
            shot: The shot to generate prompt for
            character: Character in the shot
            product: Product being featured
            aspect_ratio: Target aspect ratio
        
        Returns:
            Optimized prompt string for Flux2/KLIE HD
        """
        
        prompt_parts = []
        
        # Add quality modifiers for Flux2
        prompt_parts.append("Ultra-realistic, high-quality professional photography")
        
        # Add character description with consistency lock
        char_desc = f"{character.appearance}, wearing {character.outfit}, {character.personality} expression"
        prompt_parts.append(char_desc)
        
        # Add frame description
        if shot.frame_description:
            prompt_parts.append(shot.frame_description)
        
        # Add product if mentioned in shot
        if product.name.lower() in shot.action.lower() or product.name.lower() in shot.dialogue.lower():
            prompt_parts.append(f"holding {product.visual_description}")
        
        # Add camera and lighting
        prompt_parts.append(f"{shot.camera_angle}, {shot.lighting} lighting")
        
        # Add style modifiers based on platform
        if "tiktok" in shot.audio_notes.lower() or "instagram" in shot.audio_notes.lower():
            prompt_parts.append("vertical format, mobile-first composition")
        
        # Add aspect ratio
        prompt_parts.append(f"--ar {aspect_ratio}")
        
        return ", ".join(prompt_parts)
    
    def generate_video_prompt_for_shot(
        self,
        shot: UGCShot,
        character: UGCCharacter,
        product: UGCProduct
    ) -> str:
        """
        Generate video generation prompt for LTX-2.3.
        
        Args:
            shot: The shot to animate
            character: Character in the shot
            product: Product being featured
        
        Returns:
            Motion description for img2video
        """
        
        motion_parts = []
        
        # Add character motion
        if "speak" in shot.action.lower() or "say" in shot.action.lower():
            motion_parts.append(f"{character.name} speaking naturally with subtle head movements and gestures")
        
        if "hold" in shot.action.lower() or "show" in shot.action.lower():
            motion_parts.append(f"gently holding and presenting the {product.name}")
        
        if "spray" in shot.action.lower() or "apply" in shot.action.lower():
            motion_parts.append(f"spraying motion with visible mist particles")
        
        if "smile" in shot.action.lower():
            motion_parts.append(f"warm genuine smile spreading across face")
        
        # Add camera motion
        if "close-up" in shot.camera_angle.lower():
            motion_parts.append("subtle camera push-in")
        elif "wide" in shot.camera_angle.lower():
            motion_parts.append("gentle camera drift")
        else:
            motion_parts.append("natural handheld camera movement")
        
        # Add environmental motion
        if "mist" in shot.frame_description.lower() or "spray" in shot.frame_description.lower():
            motion_parts.append("floating particles and mist drifting in air")
        
        if "light" in shot.lighting.lower():
            motion_parts.append(f"{shot.lighting} light rays shimmering")
        
        # Add UGC authenticity markers
        motion_parts.append("natural breathing, subtle blinking, authentic UGC style")
        
        return ", ".join(motion_parts)


# Singleton instance
_generator_instance: Optional[UGCStoryGenerator] = None


def get_ugc_story_generator() -> UGCStoryGenerator:
    """Get or create the singleton UGCStoryGenerator instance."""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = UGCStoryGenerator()
    return _generator_instance
