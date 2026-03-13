"""
Credit System for Videlo
========================
Pricing structure with minimum 90% profit margin on all services.
Base Rate: 1 Credit = $0.01 USD
"""

from enum import Enum
from typing import Dict, Optional, Tuple


class InferenceType(Enum):
    TXT2IMG = "txt2img"
    IMG2IMG = "img2img"
    TXT2VIDEO = "txt2video"
    IMG2VIDEO = "img2video"
    AUDIO2VIDEO = "audio2video"
    TXT2AUDIO = "txt2audio"
    TXT2MUSIC = "txt2music"
    IMG_UPSCALE = "img-upscale"
    IMG_RMBG = "img-rmbg"
    IMG2TXT = "img2txt"
    TXT2EMBEDDING = "txt2embedding"
    AUDIO2TEXT = "audio2text"


# Credit pricing tables based on credit_system.txt
TXT2IMG_CREDITS = {
    "Flux1schnell": {
        (512, 512): 4,
        (768, 768): 5,
        (1024, 1024): 8,
        (1536, 1536): 12,
        (2048, 2048): 18,
    },
    "ZImageTurbo_INT8": {
        (512, 512): 8,
        (768, 768): 12,
        (1024, 1024): 20,
        (1536, 1536): 30,
        (2048, 2048): 45,
    },
    "Flux_2_Klein_4B_BF16": {
        (512, 512): 5,
        (768, 768): 8,
        (1024, 1024): 10,
        (1536, 1536): 15,
    },
}

IMG2IMG_CREDITS = {
    "QwenImageEdit_Plus_NF4": {
        (512, 512): 40,
        (768, 768): 70,
        (1024, 1024): 100,
    },
    "Flux_2_Klein_4B_BF16": {
        (768, 768): 12,
        (1024, 1024): 16,
        (1536, 1536): 25,
    },
}

TXT2VIDEO_CREDITS = {
    "Ltxv_13B_0_9_8_Distilled_FP8": {
        (512, 512, 30): 5,
        (512, 512, 60): 8,
        (512, 512, 120): 12,
        (768, 768, 120): 20,
    },
    "Ltx2_19B_Dist_FP8": {
        (512, 512, 49): 12,
        (768, 768, 120): 80,
        (1024, 1024, 120): 120,
        (768, 768, 241): 140,
    },
    "Ltx2_3_22B_Dist_INT8": {  # RECOMMENDED - Best value
        (512, 512, 49): 8,
        (768, 768, 120): 20,
        (1024, 1024, 120): 30,
        (768, 768, 241): 35,
        (1024, 1024, 241): 50,
    },
}

# Image-to-video uses same pricing as txt2video
IMG2VIDEO_CREDITS = TXT2VIDEO_CREDITS

AUDIO2VIDEO_CREDITS = {
    "Ltx2_3_22B_Dist_INT8": {
        (768, 768, 120): 25,
        (1024, 1024, 120): 35,
    },
}

TTS_CREDITS = {
    "Kokoro": {100: 2, 500: 4, 1000: 6, 5000: 20},  # RECOMMENDED - Best value
    "Chatterbox": {100: 4, 500: 12, 1000: 25, 2000: 50},
    "Qwen3_TTS_12Hz_1_7B_CustomVoice": {100: 6, 500: 25, 1000: 50},
    "Qwen3_TTS_12Hz_1_7B_Base": {100: 6, 500: 25},
    "Qwen3_TTS_12Hz_1_7B_VoiceDesign": {100: 6, 500: 25},
}

MUSIC_CREDITS = {
    "AceStep_1_5_Turbo": {30: 5, 60: 8, 120: 12, 180: 18, 300: 25},  # RECOMMENDED - Fast
    "AceStep_1_5_Base": {30: 8, 60: 12, 120: 35, 180: 50, 300: 80},
}

IMG_PROCESSING_CREDITS = {
    "RealESRGAN_x4": {512: 4, 768: 5, 1024: 8, 1536: 12, 2048: 15},
    "Ben2": {512: 2, 768: 2, 1024: 4, 1536: 5, 2048: 8},
    "Nanonets_Ocr_S_F16": {512: 8, 768: 12, 1024: 16, 2048: 30, 4096: 60},
}

TRANSCRIPTION_CREDITS = {
    "WhisperLargeV3": {60: 10, 300: 40, 600: 70, 1800: 200, 3600: 350},  # duration in seconds
}

EMBEDDING_CREDITS = 2  # Flat rate for all embeddings

# Default fallback credits
DEFAULT_CREDITS = {
    InferenceType.TXT2IMG: 10,
    InferenceType.IMG2IMG: 30,
    InferenceType.TXT2VIDEO: 30,
    InferenceType.IMG2VIDEO: 30,
    InferenceType.AUDIO2VIDEO: 30,
    InferenceType.TXT2AUDIO: 10,
    InferenceType.TXT2MUSIC: 15,
    InferenceType.IMG_UPSCALE: 8,
    InferenceType.IMG_RMBG: 4,
    InferenceType.IMG2TXT: 16,
    InferenceType.TXT2EMBEDDING: 2,
    InferenceType.AUDIO2TEXT: 50,
}


def get_closest_key(d: dict, value: int) -> int:
    """Find the closest key that is >= value, or return the max key."""
    keys = sorted(d.keys())
    for k in keys:
        if k >= value:
            return k
    return keys[-1] if keys else 0


def get_closest_resolution_key(pricing: dict, width: int, height: int) -> Optional[Tuple[int, int]]:
    """Find the closest resolution key that fits the requested dimensions."""
    for (w, h), credits in sorted(pricing.items()):
        if width <= w and height <= h:
            return (w, h), credits
    # Return max resolution if nothing fits
    if pricing:
        max_key = max(pricing.keys(), key=lambda x: x[0] * x[1])
        return max_key, pricing[max_key]
    return None, None


def get_closest_video_key(pricing: dict, width: int, height: int, frames: int) -> Optional[Tuple[int, int, int]]:
    """Find the closest video key that fits the requested dimensions and frames."""
    for (w, h, f), credits in sorted(pricing.items()):
        if width <= w and height <= h and frames <= f:
            return (w, h, f), credits
    # Return max if nothing fits
    if pricing:
        max_key = max(pricing.keys(), key=lambda x: x[0] * x[1] * x[2])
        return max_key, pricing[max_key]
    return None, None


def calculate_credits(
    inference_type: InferenceType,
    model: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    frames: Optional[int] = None,
    text_length: Optional[int] = None,
    duration: Optional[int] = None,
) -> int:
    """
    Calculate credits required for a generation request.
    All services have minimum 90% profit margin.
    
    Args:
        inference_type: Type of generation (txt2img, txt2video, etc.)
        model: Model slug/ID
        width: Output width in pixels
        height: Output height in pixels
        frames: Number of frames (for video)
        text_length: Text length (for TTS)
        duration: Duration in seconds (for music/transcription)
    
    Returns:
        int: Number of credits required
    """
    
    if inference_type == InferenceType.TXT2IMG:
        pricing = TXT2IMG_CREDITS.get(model, {})
        _, credits = get_closest_resolution_key(pricing, width or 512, height or 512)
        return credits or DEFAULT_CREDITS[inference_type]
    
    elif inference_type == InferenceType.IMG2IMG:
        pricing = IMG2IMG_CREDITS.get(model, {})
        _, credits = get_closest_resolution_key(pricing, width or 768, height or 768)
        return credits or DEFAULT_CREDITS[inference_type]
    
    elif inference_type in [InferenceType.TXT2VIDEO, InferenceType.IMG2VIDEO]:
        pricing = TXT2VIDEO_CREDITS.get(model, {})
        _, credits = get_closest_video_key(pricing, width or 512, height or 512, frames or 49)
        return credits or DEFAULT_CREDITS[inference_type]
    
    elif inference_type == InferenceType.AUDIO2VIDEO:
        pricing = AUDIO2VIDEO_CREDITS.get(model, {})
        _, credits = get_closest_video_key(pricing, width or 768, height or 768, frames or 120)
        return credits or DEFAULT_CREDITS[inference_type]
    
    elif inference_type == InferenceType.TXT2AUDIO:
        pricing = TTS_CREDITS.get(model, {})
        if pricing:
            key = get_closest_key(pricing, text_length or 100)
            return pricing.get(key, 10)
        return DEFAULT_CREDITS[inference_type]
    
    elif inference_type == InferenceType.TXT2MUSIC:
        pricing = MUSIC_CREDITS.get(model, {})
        if pricing:
            key = get_closest_key(pricing, duration or 60)
            return pricing.get(key, 15)
        return DEFAULT_CREDITS[inference_type]
    
    elif inference_type == InferenceType.IMG_UPSCALE:
        pricing = IMG_PROCESSING_CREDITS.get("RealESRGAN_x4", {})
        key = get_closest_key(pricing, max(width or 512, height or 512))
        return pricing.get(key, 8)
    
    elif inference_type == InferenceType.IMG_RMBG:
        pricing = IMG_PROCESSING_CREDITS.get("Ben2", {})
        key = get_closest_key(pricing, max(width or 512, height or 512))
        return pricing.get(key, 4)
    
    elif inference_type == InferenceType.IMG2TXT:
        pricing = IMG_PROCESSING_CREDITS.get("Nanonets_Ocr_S_F16", {})
        key = get_closest_key(pricing, max(width or 512, height or 512))
        return pricing.get(key, 16)
    
    elif inference_type == InferenceType.TXT2EMBEDDING:
        return EMBEDDING_CREDITS
    
    elif inference_type == InferenceType.AUDIO2TEXT:
        pricing = TRANSCRIPTION_CREDITS.get("WhisperLargeV3", {})
        key = get_closest_key(pricing, duration or 60)
        return pricing.get(key, 50)
    
    return 15  # Default fallback


def get_generation_type_inference_type(generation_type: str) -> InferenceType:
    """Convert generation_type string to InferenceType enum."""
    mapping = {
        "text2img": InferenceType.TXT2IMG,
        "txt2img": InferenceType.TXT2IMG,
        "img2img": InferenceType.IMG2IMG,
        "txt2video": InferenceType.TXT2VIDEO,
        "img2video": InferenceType.IMG2VIDEO,
        "audio2video": InferenceType.AUDIO2VIDEO,
        "txt2audio": InferenceType.TXT2AUDIO,
        "txt2music": InferenceType.TXT2MUSIC,
        "img-upscale": InferenceType.IMG_UPSCALE,
        "img_rmbg": InferenceType.IMG_RMBG,
        "img2txt": InferenceType.IMG2TXT,
        "txt2embedding": InferenceType.TXT2EMBEDDING,
        "audio2text": InferenceType.AUDIO2TEXT,
        "audiofile2txt": InferenceType.AUDIO2TEXT,
        "videofile2txt": InferenceType.AUDIO2TEXT,
        "vid2txt": InferenceType.AUDIO2TEXT,
        "aud2txt": InferenceType.AUDIO2TEXT,
    }
    return mapping.get(generation_type, InferenceType.TXT2IMG)


def get_credit_breakdown(
    inference_type: InferenceType,
    model: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    frames: Optional[int] = None,
    text_length: Optional[int] = None,
    duration: Optional[int] = None,
) -> Dict:
    """
    Get a detailed breakdown of credits for display purposes.
    
    Returns:
        Dict with credits, model info, and parameters
    """
    credits = calculate_credits(
        inference_type=inference_type,
        model=model,
        width=width,
        height=height,
        frames=frames,
        text_length=text_length,
        duration=duration,
    )
    
    # Build friendly model name
    model_names = {
        "Flux1schnell": "FLUX.1 Schnell",
        "Flux_2_Klein_4B_BF16": "FLUX.2 Klein",
        "ZImageTurbo_INT8": "Z-Image Turbo",
        "QwenImageEdit_Plus_NF4": "Qwen Image Edit",
        "Ltxv_13B_0_9_8_Distilled_FP8": "LTX-Video 13B",
        "Ltx2_19B_Dist_FP8": "LTX-2 19B",
        "Ltx2_3_22B_Dist_INT8": "LTX-2.3 22B",
        "Kokoro": "Kokoro TTS",
        "Chatterbox": "Chatterbox TTS",
        "AceStep_1_5_Turbo": "ACE-Step Turbo",
        "AceStep_1_5_Base": "ACE-Step Base",
        "RealESRGAN_x4": "RealESRGAN x4",
        "Ben2": "Ben2",
        "Nanonets_Ocr_S_F16": "Nanonets OCR",
        "WhisperLargeV3": "Whisper Large V3",
    }
    
    friendly_name = model_names.get(model, model)
    
    # Build description
    if inference_type in [InferenceType.TXT2IMG, InferenceType.IMG2IMG]:
        desc = f"{friendly_name} - {width}x{height}"
    elif inference_type in [InferenceType.TXT2VIDEO, InferenceType.IMG2VIDEO, InferenceType.AUDIO2VIDEO]:
        video_duration = (frames or 49) / 24  # Assuming 24 fps
        desc = f"{friendly_name} - {width}x{height}, ~{video_duration:.1f}s"
    elif inference_type == InferenceType.TXT2AUDIO:
        desc = f"{friendly_name} - {text_length or 100} chars"
    elif inference_type == InferenceType.TXT2MUSIC:
        desc = f"{friendly_name} - {duration or 60}s"
    elif inference_type == InferenceType.IMG_UPSCALE:
        desc = f"{friendly_name} - {width}x{height} -> {width*4}x{height*4}"
    elif inference_type == InferenceType.IMG_RMBG:
        desc = f"Background Removal - {width}x{height}"
    else:
        desc = friendly_name
    
    return {
        "credits": credits,
        "model": model,
        "model_name": friendly_name,
        "description": desc,
        "parameters": {
            "width": width,
            "height": height,
            "frames": frames,
            "text_length": text_length,
            "duration": duration,
        }
    }


# Credit packages for purchase
CREDIT_PACKAGES = [
    {"id": "starter", "name": "Starter", "credits": 100, "price_cents": 100, "bonus_percent": 0},
    {"id": "basic", "name": "Basic", "credits": 500, "price_cents": 450, "bonus_percent": 10},
    {"id": "pro", "name": "Pro", "credits": 1500, "price_cents": 1200, "bonus_percent": 20},
    {"id": "ultimate", "name": "Ultimate", "credits": 5000, "price_cents": 3500, "bonus_percent": 30},
    {"id": "enterprise", "name": "Enterprise", "credits": 15000, "price_cents": 9000, "bonus_percent": 40},
]

# Free credits for new users
FREE_CREDITS_ON_SIGNUP = 20
